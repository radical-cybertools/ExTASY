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
        #print "Submitting new 'pmemd' compute unit"
        dict['rep'] = str(i)
        dict['path'] = Kconfig.exp_loc
        # output files that need to be transferred back: *.mdcrd

        step_1 = 'pmemd -O -i {path}/{minin} -o {path}/rep0{rep}/min{cycle}.out -inf {path}/rep0{rep}/min{cycle}.inf -r {path}/rep0{rep}/md{cycle}.crd -p {path}/{topfile} -c {path}/rep0{rep}/min{cycle}.crd -ref {path}/rep0{rep}/min{cycle}.crd'.format(**dict)
        step_2 = 'pmemd -O -i {path}/{mdin} -o {path}/rep0{rep}/md{cycle}.out -inf {path}/rep0{rep}/md{cycle}.inf -x {path}/rep0{rep}/md{cycle}.mdcrd -r {path}/rep0{rep}/md{cycle}.rst -p {path}/{topfile} -c {path}/rep0{rep}/md{cycle}.crd'.format(**dict)

        cu = radical.pilot.ComputeUnitDescription()
        cu.executable = "/bin/bash"
        cu.cores      = 1
        cu.pre_exec = ['module load TACC ','module load amber','cd %s' % Kconfig.exp_loc]
        cu.arguments  = ['-l', '-c', " %s && %s" % (step_1, step_2)]
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

