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
    dict['crdfile'] = Kconfig.crdfile
    dict['topfile'] = Kconfig.topfile
    dict['mdin']    = Kconfig.mdshortfile
    dict['minin']   = Kconfig.minfile
    dict['cycle'] = cycle

    start_times = []
    end_times = []

    compute_units = []
    for i in range(Kconfig.nreps):

        step_1 = 'pmemd -O -i {minin} -o min{cycle}.out -inf min{cycle}.inf -r md{cycle}.crd -p {topfile} -c min{cycle}.crd -ref min{cycle}.crd'.format(**dict)
        step_2 = 'pmemd -O -i {mdin} -o md{cycle}.out -inf md{cycle}.inf -x md{cycle}.mdcrd -r md{cycle}.rst -p {topfile} -c md{cycle}.crd'.format(**dict)

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
            cu.input_staging = ['%s/%s > min%s.crd'%(Kconfig.crd_loc,dict['crdfile'],cycle),'%s/%s'%(Kconfig.top_loc,dict['topfile']),'%s/%s'%(Kconfig.min_loc,dict['minin']),'%s/%s'%(Kconfig.mdshort_loc,dict['mdin'])]
        else:
            cu.input_staging = ['min%s%s.crd > min%s.crd'%(cycle,i,cycle),'%s/%s'%(Kconfig.top_loc,dict['topfile']),'%s/%s'%(Kconfig.min_loc,dict['minin']),'%s/%s'%(Kconfig.mdshort_loc,dict['mdin'])]
        cu.output_staging = ['md%s.mdcrd > md_%s_%s.mdcrd'%(cycle,cycle,i)]
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

