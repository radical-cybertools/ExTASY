__author__ = 'vivek'

import radical.pilot
from radical.ensemblemd.mdkernels import MDTaskDescription
import os
import time


def Simulator(umgr,RPconfig,Kconfig,cycle):

    p1 = time.time()
    #curdir = os.path.dirname(os.path.realpath(__file__))

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

    compute_units = []
    for i in range(Kconfig.nreps):

        step_1 = 'pmemd -O -i {mininfilename} -o min{cycle}.out -inf min{cycle}.inf -r md{cycle}.crd -p {topfilename} -c min{cycle}.crd -ref min{cycle}.crd'.format(**dict)
        step_2 = 'pmemd -O -i {mdinfilename} -o md{cycle}.out -inf md{cycle}.inf -x md{cycle}.ncdf -r md{cycle}.rst -p {topfilename} -c md{cycle}.crd'.format(**dict)

        mdtd = MDTaskDescription()
        mdtd.kernel = "AMBER"
        mdtd.arguments = ['-l', '-c', " %s && %s" % (step_1, step_2)]
        mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
        cu = radical.pilot.ComputeUnitDescription()
        cu.cores      = 1
        cu.executable = mdtd_bound.executable
        cu.pre_exec   = mdtd_bound.pre_exec
        cu.arguments  = mdtd_bound.arguments
        if(cycle==0):
            cu.input_staging = ['%s > min%s.crd'%(dict['crdfile'],cycle),'%s'%(dict['topfile']),'%s'%(dict['minin']),'%s'%(dict['mdin'])]
        else:
            cu.input_staging = ['min%s%s.crd > min%s.crd'%(cycle,i,cycle),'%s'%(dict['topfile']),'%s'%(dict['minin']),'%s'%(dict['mdin'])]
        cu.output_staging = ['md%s.ncdf > md_%s_%s.ncdf'%(cycle,cycle,i)]
        compute_units.append(cu)

    units = umgr.submit_units(compute_units)
    umgr.wait_units()

    p2 = time.time()

    print 'Total Simulation Time : ', (p2-p1)

    for unit in units:
        #print 'Start : ', unit.start_time, 'Stop : ', unit.stop_time
        start_times.append(unit.start_time)
        end_times.append(unit.stop_time)

    print 'Simulation Execution Time : ', (max(end_times)-min(start_times)).total_seconds()

