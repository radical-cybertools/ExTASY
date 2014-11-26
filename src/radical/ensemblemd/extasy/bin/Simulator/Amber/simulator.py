__author__ = 'vivek'

import radical.pilot
from radical.ensemblemd.mdkernels import MDTaskDescription
import os
import time
import saga


def Simulator(umgr,RPconfig,Kconfig,cycle,paths):


    print 'Cycle %s' %cycle

    print 'Starting Simulation'

    dict = {}
    dict['crdfile'] = Kconfig.initial_crd_file
    dict['crdfilename'] = os.path.basename(dict['crdfile'])
    dict['topfile'] = Kconfig.top_file
    dict['topfilename'] = os.path.basename(dict['topfile'])
    dict['mdin']    = Kconfig.md_input_file
    dict['mdinfilename'] = os.path.basename(dict['mdin'])
    dict['minin']   = Kconfig.minimization_input_file
    dict['mininfilename'] = os.path.basename(dict['minin'])
    dict['cycle'] = cycle

    start_times = []
    end_times = []

    cudesc_list_A = []
    for i in range(Kconfig.num_CUs):

        #step_1 = 'pmemd.MPI -O -i {mininfilename} -o min{cycle}.out -inf min{cycle}.inf -r md{cycle}.crd -p {topfilename} -c min{cycle}.crd -ref min{cycle}.crd'.format(**dict)

        mdtd = MDTaskDescription()
        mdtd.kernel = "AMBER"
        mdtd.arguments = ['-O','-i',dict['mininfilename'],'-o','min%s.out'%cycle,'-inf','min%s.inf'%cycle,'-r',
                          'md%s.crd'%cycle,'-p',dict['topfilename'],'-c','min%s.crd'%cycle,'-ref','min%s.crd'%cycle]
        mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
        cu = radical.pilot.ComputeUnitDescription()
        cu.cores = Kconfig.num_cores_per_sim_cu
        cu.mpi = True
        cu.executable = mdtd_bound.executable
        cu.pre_exec = mdtd_bound.pre_exec
        cu.arguments = mdtd_bound.arguments
        if(cycle==0):
            cu.pre_exec = cu.pre_exec + ['cp %s/%s min%s.crd'%(paths[0],dict['crdfilename'],cycle),'cp %s/%s .'%(paths[0],dict['topfilename']),'cp %s/%s .'%(paths[0],dict['mininfilename'])]
        else:
            cu.pre_exec = cu.pre_exec + ['cp %s/min%s%s.crd min%s.crd'%(paths[cycle],cycle,i,cycle),'cp %s/%s .'%(paths[0],dict['topfilename']),'cp %s/%s .'%(paths[0],dict['mininfilename'])]
        cudesc_list_A.append(cu)

    cu_list_A = umgr.submit_units(cudesc_list_A)

    cu_list_B = []

    cu_list_A_copy = cu_list_A[:]

    i=0
    while cu_list_A:
        for cu_a in cu_list_A:
            cu_a.wait ()
            path=saga.Url(cu_a.working_directory).path

            step_2 = 'pmemd.MPI -O -i {mdinfilename} -o md{cycle}.out -inf md{cycle}.inf -x md{cycle}.ncdf -r md{cycle}.rst -p {topfilename} -c md{cycle}.crd'.format(**dict)

            mdtd = MDTaskDescription()
            mdtd.kernel = "AMBER"
            mdtd.arguments = ['-O','-i',dict['mdinfilename'],'-o','md%s.out'%cycle,'-inf','md%s.inf'%cycle,
                              '-x','md%s.ncdf'%cycle,'-r','md%s.rst'%cycle,'-p',dict['topfilename'],'-c','md%s.crd'%cycle]
            mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
            cudesc = radical.pilot.ComputeUnitDescription()
            cudesc.cores = Kconfig.num_cores_per_sim_cu
            cudesc.mpi = True
            cudesc.executable = mdtd_bound.executable
            cudesc.pre_exec = ['cp %s/* .'%path] + mdtd_bound.pre_exec
            cudesc.arguments = mdtd_bound.arguments
            #cudesc.input_staging = [dict['mdin']]
            cudesc.pre_exec = cudesc.pre_exec + ['cp %s/%s .'%(paths[0],dict['mdinfilename'])]
            #cudesc.output_staging = ['md%s.ncdf > md_%s_%s.ncdf'%(cycle,cycle,i)]
            cudesc.post_exec = ['cp md%s.ncdf %s/md_%s_%s.ncdf'%(cycle,paths[cycle],cycle,i)]
            cu_b = umgr.submit_units(cudesc)
            i+=1
            cu_list_B.append(cu_b)
            cu_list_A.remove(cu_a)

    for cu_b in cu_list_B:
        cu_b.wait()

    try:
        for unit_a,unit_b in cu_list_A_copy,cu_list_B:
            #print 'Start : ', unit.start_time, 'Stop : ', unit.stop_time
            start_times.append(unit_a.start_time)
            end_times.append(unit_b.stop_time)

        print 'Simulation Execution Time : ', (max(end_times)-min(start_times)).total_seconds()

    except:
        pass

