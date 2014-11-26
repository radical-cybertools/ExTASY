__author__ = 'vivek'

import radical.pilot
from radical.ensemblemd.mdkernels import MDTaskDescription
import os
import time
import glob


def Simulator(umgr,RPconfig,Kconfig,cycle,paths):

    curdir = os.path.dirname(os.path.realpath(__file__))

    print 'Cycle %s' %cycle
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
            ndx_opts = ''
        mdtd.arguments = ['run.py','--mdp','%s'%grompp_name,'--gro','start.gro','--top','%s'%topol_name,'--out','out.gro']
        mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
        gromacs_task = radical.pilot.ComputeUnitDescription()
        gromacs_task.pre_exec = ['export grompp_options="%s" mdrun_options="%s" ndxfile="%s"'%(grompp_opts,mdrun_opts,ndxfile_name)] + mdtd_bound.pre_exec
        gromacs_task.executable = 'python'
        gromacs_task.arguments = mdtd_bound.arguments
        gromacs_task.mpi = True
        gromacs_task.cores = Kconfig.num_cores_per_sim_cu

        #gromacs_task.input_staging = ['%s/run.sh > run.sh'%curdir,'%s/temp/start%s.gro > start.gro' % (os.getcwd(), i),'%s' % (Kconfig.mdp_file), '%s' % (Kconfig.top_file)]
        inputs = ['cp %s/run.py .'%paths[0],'cp %s/temp/start%s.gro start.gro'%(paths[cycle],i),'cp %s/%s .'%(paths[0],grompp_name),'cp %s/%s .'%(paths[0],topol_name)]
        gromacs_task.pre_exec = gromacs_task.pre_exec + inputs

        if Kconfig.ndx_file is not None:
            #gromacs_task.input_staging.append('%s' % Kconfig.ndx_file)
            gromacs_task.pre_exec = gromacs_task.pre_exec + ['cp %s/%s .'%(paths[0],ndxfile_name)]
        if Kconfig.itp_file_loc is not None:
            # for itpfile in glob.glob(Kconfig.itp_file_loc + '*.itp'):
            #    gromacs_task.input_staging.append('%s' % itpfile)
            gromacs_task.pre_exec = gromacs_task.pre_exec + ['cp %s/*.itp .' % paths[0]]
        #gromacs_task.output_staging = ['out.gro > out%s.gro' % i]
        gromacs_task.post_exec = ['cp out.gro %s/out%s.gro'%(paths[cycle],i)]

        gromacs_tasks.append(gromacs_task)

    units = umgr.submit_units(gromacs_tasks)

    start_times = []
    end_times = []

    # Wait for all compute units to finish.
    umgr.wait_units()

    try:
        for unit in units:
            #print 'Start : ', unit.start_time, 'Stop : ', unit.stop_time
            start_times.append(unit.start_time)
            end_times.append(unit.stop_time)
    
        print 'Simulation Execution Time : ', (max(end_times)-min(start_times)).total_seconds()

    except:
        pass
