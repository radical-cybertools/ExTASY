__author__ = 'vivek'

import radical.pilot
from radical.ensemblemd.mdkernels import MDTaskDescription
import os
import time
import glob
import subprocess
import pipes
import saga

def exists_remote(host, paths):
    qpath = ''
    for path in paths:
        qpath += 'test -f {0};'.format(pipes.quote(path))
    proc = subprocess.Popen(['ssh', host, qpath])
    proc.wait()
    return proc.returncode == 0

def Simulator(umgr,RPconfig,Kconfig,cycle,pilot):

    curdir = os.path.dirname(os.path.realpath(__file__))

    MY_STAGING_AREA = 'staging:///'

    grompp_name = os.path.basename(Kconfig.mdp_file)
    topol_name = os.path.basename(Kconfig.top_file)

    nsave = Kconfig.nsave

    print 'Starting Simulation'

    gromacs_tasks = []
    for i in range(0, Kconfig.num_CUs):
        mdtd = MDTaskDescription()
        mdtd.kernel = "GROMACS"
        if Kconfig.grompp_options is not None:
            grompp_opts = Kconfig.grompp_options
        else:
            grompp_opts = ''
        if Kconfig.mdrun_options is not None:
            mdrun_opts = Kconfig.mdrun_options
        else:
            mdrun_opts = ''
        if Kconfig.ndx_file is not None:
            ndxfile_name = os.path.basename(Kconfig.ndx_file)
        else:
            ndxfile_name = ''
        mdtd.arguments = ['run.py', '--mdp', '%s' % grompp_name, '--gro', 'start.gro', '--top', '%s' % topol_name, '--out', 'out.gro']
        mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
        gromacs_task = radical.pilot.ComputeUnitDescription()
        gromacs_task.pre_exec = ['export grompp_options="%s" mdrun_options="%s" ndxfile="%s"' % (grompp_opts, mdrun_opts, ndxfile_name)] + mdtd_bound.pre_exec
        gromacs_task.executable = 'python'
        gromacs_task.arguments = mdtd_bound.arguments
        gromacs_task.mpi = True
        gromacs_task.cores = Kconfig.num_cores_per_sim_cu

        run_stage = {
                        'source': MY_STAGING_AREA + 'run.py',
                        'target': 'run.py',
                        'action': radical.pilot.LINK
                    }

        gro_stage = {
                        'source': MY_STAGING_AREA + 'iter{0}/start{1}.gro'.format(cycle, i),
                        'target': 'start.gro',
                        'action': radical.pilot.LINK
                    }

        grompp_stage = {
                        'source': MY_STAGING_AREA + grompp_name,
                        'target': grompp_name,
                        'action': radical.pilot.LINK
                    }

        topol_stage = {
                        'source': MY_STAGING_AREA + topol_name,
                        'target': topol_name,
                        'action': radical.pilot.LINK
                    }

        gromacs_task.input_staging = [run_stage, gro_stage, grompp_stage, topol_stage]

        if Kconfig.ndx_file is not None:
            ndx_stage = {
                            'source': MY_STAGING_AREA + ndxfile_name,
                            'target': ndxfile_name,
                            'action': radical.pilot.LINK
                        }
            gromacs_task.input_staging.append(ndx_stage)

        if Kconfig.itp_file_loc is not None:
            for itpfile in glob.glob(Kconfig.itp_file_loc + '*.itp'):
                temp = {
                            'source': MY_STAGING_AREA + itpfile,
                            'target': itpfile,
                            'action': radical.pilot.LINK
                        }
                gromacs_task.input_staging.append(temp)

        out_stage = {
                        'source': 'out.gro',
                        'target': MY_STAGING_AREA + 'iter{0}/out{1}.gro'.format(cycle, i),
                        'action':radical.pilot.LINK
                    }

        gromacs_task.output_staging = [out_stage]

        gromacs_tasks.append(gromacs_task)

    units = umgr.submit_units(gromacs_tasks)

    start_times = []
    end_times = []

    # Wait for all compute units to finish.
    umgr.wait_units()

    if (cycle+1)%Kconfig.checkfiles==0:

        if pilot.resource == 'xsede.stampede':
            remote='stampede.tacc.utexas.edu'
        else:
            remote='login.archer.ac.uk'

        paths=[]
        for i in range(0,Kconfig.num_CUs):
            paths.append(saga.Url(pilot.sandbox).path + 'staging_area/iter{0}/out{1}.gro'.format(cycle,i))
        
        if exists_remote('{0}@{1}'.format(RPconfig.UNAME,remote),paths):
            print 'All expected files present on remote'
        else:
            print 'Error finding expected files on remote'
            sys.exit(-1)
    try:
        for unit in units:
            start_times.append(unit.start_time)
            end_times.append(unit.stop_time)
    
        print 'Simulation Execution Time : ', (max(end_times)-min(start_times)).total_seconds()

    except:
        pass


