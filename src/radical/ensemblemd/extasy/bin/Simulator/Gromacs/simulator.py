__author__ = 'vivek'

import radical.pilot
from radical.ensemblemd.mdkernels import MDTaskDescription
import os
import time
import glob


def Simulator(umgr,RPconfig,Kconfig,cycle):

    curdir = os.path.dirname(os.path.realpath(__file__))

    print 'Cycle %s' %cycle
    Kconfig.grompp_name = os.path.basename(Kconfig.mdp_file)
    Kconfig.topol_name = os.path.basename(Kconfig.top_file)
    Kconfig.ndxfile_name = os.path.basename(Kconfig.ndx_file)

    print 'Starting Simulation'

    gromacs_tasks = []
    for i in range(0, Kconfig.num_CUs):
        mdtd = MDTaskDescription()
        mdtd.kernel = "GROMACS"
        mdtd.arguments = ['-l','-c',". run.sh %s start.gro %s out.gro %s" % (Kconfig.grompp_name,Kconfig.topol_name,Kconfig.num_cores_per_sim_cu)]
        mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
        gromacs_task = radical.pilot.ComputeUnitDescription()
        gromacs_task.environment = {}
        if Kconfig.grompp_options is not None:
            gromacs_task.environment['grompp_options'] = '"%s"' % Kconfig.grompp_options
        if Kconfig.mdrun_options is not None:
            gromacs_task.environment['mdrun_options'] = '"%s"' % Kconfig.mdrun_options
        if Kconfig.ndxfile_name is not None:
            gromacs_task.environment['ndxfile'] = '"%s"' % Kconfig.ndxfile_name
        gromacs_task.pre_exec = mdtd_bound.pre_exec
        gromacs_task.executable = '/bin/bash'
        gromacs_task.arguments = mdtd_bound.arguments
        gromacs_task.mpi = True
        gromacs_task.cores = Kconfig.num_cores_per_sim_cu
        gromacs_task.input_staging = ['%s/run.sh > run.sh'%curdir,'%s/temp/start%s.gro > start.gro' % (os.getcwd(), i),'%s' % (Kconfig.mdp_file), '%s' % (Kconfig.top_file)]
        if Kconfig.ndx_file is not None:
            gromacs_task.input_staging.append('%s' % Kconfig.ndx_file)
        if Kconfig.itp_file_loc is not None:
            for itpfile in glob.glob(Kconfig.itp_file_loc + '*.itp'):
                gromacs_task.input_staging.append('%s/%s' % itpfile)
        gromacs_task.output_staging = ['out.gro > out%s.gro' % i]

        gromacs_tasks.append(gromacs_task)

    units = umgr.submit_units(gromacs_tasks)

    start_times = []
    end_times = []

    # Wait for all compute units to finish.
    umgr.wait_units()

    if os.path.exists('%s/%s' % (os.getcwd(),Kconfig.md_output_file)):
        os.remove(os.getcwd() + '/' + Kconfig.md_output_file)

    with open(Kconfig.md_output_file, 'w') as output_grofile:
        for i in range(0,Kconfig.num_CUs):
            with open('out%s.gro' % i, 'r') as output_file:
                for line in output_file:
                    print >> output_grofile, line.replace("\n", "")
            os.remove('out%s.gro'%i)

    try:
        for unit in units:
            #print 'Start : ', unit.start_time, 'Stop : ', unit.stop_time
            start_times.append(unit.start_time)
            end_times.append(unit.stop_time)
    
        print 'Simulation Execution Time : ', (max(end_times)-min(start_times)).total_seconds()

    except:
        pass
