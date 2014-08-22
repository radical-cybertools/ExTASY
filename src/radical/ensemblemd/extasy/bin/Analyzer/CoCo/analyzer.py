
from radical.ensemblemd.mdkernels import MDTaskDescription
import time
import radical.pilot
import os
import imp

def Analyzer(umgr,RPconfig_url,Kconfig_url,cycle):

    RPconfig = imp.load_source('RPconfig',RPconfig_url)
    Kconfig = imp.load_source('Kconfig',Kconfig_url)

    from RPconfig import *
    from Kconfig import *

    print 'Cycle : %s' % cycle
    print 'Submitting COCO Compute Unit'

    cudesc = radical.pilot.ComputeUnitDescription()
    cudesc.executable = 'python'
    cudesc.cores = 16
    cudesc.pre_exec = ['module load python','cp postexec.py %s'% exp_loc,'cd %s' % exp_loc,'module load mpi4py','module load amber']
    cudesc.arguments = ['cocoUi.py','--grid','5','--projs','3','--frontpoints','8','--cycle','%s'% cycle ,'-vvv' ]
    cudesc.input_data = ['%s/postexec.py'%(os.path.dirname(os.path.realpath(__file__)))]
    cudesc.post_exec = ['python postexec.py %s %s' % (nreps,cycle)]
    cudesc.mpi = True

    unit = umgr.submit_units(cudesc)

    unit.wait()

    print 'Analysis Execution time : ',(unit.stop_time - unit.start_time).total_seconds()

    return