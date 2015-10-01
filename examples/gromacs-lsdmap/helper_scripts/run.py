__author__ = 'vivek'

'''
Purpose :   This file is executed by each of the compute units in the
            simulation stage. Uses the arguments to create a bash script
            which is executed on the remote machine to perform the
            gromacs simulation.

Arguments : --mdp = name of the gromacs parameter file
            --top = name of the topology file
            --gro = name of the coordinate file
            --out = name of the output file

Changes :   - the script evaluates RP_CORE_COUNT and manages a process pool
              which runs that number of concurrent processes
'''


import os
import time
import argparse
import multiprocessing as mp

from mpi4py import MPI


# ------------------------------------------------------------------------------
#
def write_scripts (grofile_name, mdpfile_name, topfile_name,
                   grompp_opts,  mdrun_opts,   ndxfile_opts, threadnum):

    scripts = list()

    with open(grofile_name) as f1:
        lines  = f1.readlines()
        nlines = len(lines)
        natoms = int(lines[1])

    lpf     = natoms + 3        # lines per frame
    nframes = int(nlines / lpf) # number of frames


    for idx in range(nframes):

        start = lpf *  idx + 1  # first 1 on frame 'idx'
        end   = lpf * (idx + 1) # last line line of frame 'idx'
                                # = first line on frame (idx+1) - 1

        script = 'run_%05d.sh' % idx
        with open(script,'w') as f2:

            tmp="""#!/bin/bash

idx=%(idx)05d

exec  > stdout_$idx
exec 2> stdout_$idx

sed "%(start)s"','"%(end)s"'!d' %(grofile_name)s > start_$idx.gro

grompp %(grompp_opts)s \\
       %(ndxfile_opts)s \\
       -f  %(mdpfile_name)s \\
       -p  %(topfile_name)s \\
       -c  start_$idx.gro \\
       -o  topol_$idx.tpr \\
       -po mdout_$idx.mdp

mdrun  -nt %(threadnum)s \\
       %(mdrun_opts)s \\
       -o traj_$idx.trr \\
       -e ener_$idx.edr \\
       -s topol_$idx.tpr \\
       -g mdlog_$idx.log \\
       -cpo state_$idx.cpt \\
       -c outgro_$idx

""" % locals()

            f2.write(tmp)
            scripts.append(script)

    return scripts


# ------------------------------------------------------------------------------
#
def run_script(script):
    os.system ('sh ./%s' % script)
    return script


# ------------------------------------------------------------------------------
#
def log_result(result):
    # This is called whenever run_script() returns a result.  This callcack is
    # in the main thread.
    print '%s finished' % result


# ------------------------------------------------------------------------------
#
def run_scripts_in_pool(scripts, n=1):
    pool = mp.Pool(processes=n)
    for script in scripts:
        pool.apply_async(run_script, args=[script], callback=log_result)
    pool.close()
    pool.join()


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    # initialize mpi variables
    comm  = MPI.COMM_WORLD  # MPI environment
    cores = comm.Get_size() # number of threads
    rank  = comm.Get_rank() # number of the current thread

    if rank == 0:
        parser = argparse.ArgumentParser()
        parser.add_argument('--mdp', dest='mdpfile_name', required=True, type=str)
        parser.add_argument('--gro', dest='grofile_name', required=True, type=str)
        parser.add_argument('--top', dest='topfile_name', required=True, type=str)
        parser.add_argument('--out', dest='output_grofile_name', required=True, type=str)
        args = parser.parse_args()

        grompp_opts  = os.environ.get('grompp_options','')
        mdrun_opts   = os.environ.get('mdrun_options','')
        ndxfile_name = os.environ.get('ndxfile','')
        thread_num   = 1

        if ndxfile_name:
            ndxfile_opts = '-n ' + ndxfile_name
        else:
            ndxfile_opts = ''

        # create all scripts
        scripts = write_scripts(args.grofile_name, args.mdpfile_name, args.topfile_name,
                                grompp_opts, mdrun_opts, ndxfile_opts, cores)

        # runs scripts in a pool of size==#cores
        run_scripts_in_pool (scripts, n=cores)

        # collect results
        os.system('cat outgro_* >> %s' % args.output_grofile_name)

# ------------------------------------------------------------------------------

