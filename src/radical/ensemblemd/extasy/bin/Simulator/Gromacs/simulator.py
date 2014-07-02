__author__ = 'vivek'

import radical.pilot
import os
import time
from config.kernel_config import *
import saga

def Simulator(umgr):

    p1 = time.time()
    curdir = os.path.dirname(os.path.realpath(__file__))

    gromacs_tasks = []
    for i in range(0, 64):
        gromacs_task = radical.pilot.ComputeUnitDescription()
        #gromacs_task.pre_exec = ['module load TACC','module load Linux','module load intel/13.0.2.146','module load mvapich2/1.9a2','module load python']
        gromacs_task.pre_exec = ['export PATH=$PATH:~marksant/bin']
        gromacs_task.executable = "/bin/bash"
        gromacs_task.arguments = ['-l','-c',". run.sh %s start.gro %s %s" % (grompp_name,topol_name,outgrofile_name)]
        gromacs_task.input_data = ['%s/run.sh > run.sh'%curdir,'%s/temp/start%s.gro > start.gro' % (os.getcwd(), i),'%s/%s' % (grompp_loc, grompp_name), '%s/%s' % (topol_loc, topol_name)]
        gromacs_task.output_data = ['out.gro > out%s.gro' % i]
        gromacs_task.cores = 1

        gromacs_tasks.append(gromacs_task)

    units = umgr.submit_units(gromacs_tasks)

    # Wait for all compute units to finish.
    umgr.wait_units()

    if os.path.exists('%s/%s' % (os.getcwd(),outgrofile_name)):
        os.remove(os.getcwd() + '/' + outgrofile_name)

    with open(outgrofile_name, 'w') as output_grofile:
        for i in range(0,64):
            with open('out%s.gro' % i, 'r') as output_file:
                for line in output_file:
                    print >> output_grofile, line.replace("\n", "")
            os.remove('out%s.gro'%i)
    p2 = time.time()

    print 'Simulation Time : ', (p2-p1)

