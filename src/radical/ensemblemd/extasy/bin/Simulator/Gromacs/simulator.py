__author__ = 'vivek'

import radical.pilot
from radical.ensemblemd.mdkernels import MDTaskDescription
import os
import time


def Simulator(umgr,RPconfig,Kconfig,cycle):

    p1 = time.time()
    curdir = os.path.dirname(os.path.realpath(__file__))

    print 'Cycle %s' %cycle

    print 'Starting Simulation'

    gromacs_tasks = []
    for i in range(0, Kconfig.num_CUs):
        mdtd = MDTaskDescription()
        mdtd.kernel = "GROMACS"
        mdtd.arguments = ['-l','-c',". run.sh %s start.gro %s out.gro" % (Kconfig.grompp_name,Kconfig.topol_name)]
        mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
        gromacs_task = radical.pilot.ComputeUnitDescription()
        gromacs_task.pre_exec = mdtd_bound.pre_exec
        gromacs_task.executable = mdtd_bound.executable
        gromacs_task.arguments = mdtd_bound.arguments
        gromacs_task.input_data = ['%s/run.sh > run.sh'%curdir,'%s/temp/start%s.gro > start.gro' % (os.getcwd(), i),'%s/%s' % (Kconfig.grompp_loc, Kconfig.grompp_name), '%s/%s' % (Kconfig.topol_loc, Kconfig.topol_name)]
        gromacs_task.output_data = ['out.gro > out%s.gro' % i]
        gromacs_task.cores = 1

        gromacs_tasks.append(gromacs_task)

    units = umgr.submit_units(gromacs_tasks)

    start_times = []
    end_times = []

    # Wait for all compute units to finish.
    umgr.wait_units()


    if os.path.exists('%s/%s' % (os.getcwd(),Kconfig.tmp_grofile)):
        os.remove(os.getcwd() + '/' + Kconfig.tmp_grofile)

    with open(Kconfig.tmp_grofile, 'w') as output_grofile:
        for i in range(0,64):
            with open('out%s.gro' % i, 'r') as output_file:
                for line in output_file:
                    print >> output_grofile, line.replace("\n", "")
            os.remove('out%s.gro'%i)

    p2 = time.time()

    print 'Total Simulation Time : ', (p2-p1)
    
    for unit in units:
        #print 'Start : ', unit.start_time, 'Stop : ', unit.stop_time
        start_times.append(unit.start_time)
        end_times.append(unit.stop_time)
    
    print 'Simulation Execution Time : ', (max(end_times)-min(start_times)).total_seconds()

