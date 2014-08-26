
from radical.ensemblemd.mdkernels import MDTaskDescription
import time
import radical.pilot
import os
import imp

def Analyzer(umgr,RPconfig,Kconfig,cycle):

    print 'Cycle : %s' % cycle
    print 'Submitting COCO Compute Unit'

    cudesc = radical.pilot.ComputeUnitDescription()
    cudesc.executable = 'python'
    cudesc.cores = RPconfig.PILOTSIZE
    cudesc.pre_exec = ['module load python','cp postexec.py %s'% Kconfig.exp_loc,'cd %s' % Kconfig.exp_loc,'module load mpi4py','module load amber']
    cudesc.arguments = ['cocoUi.py','--grid','5','--projs','3','--frontpoints','8','--cycle','%s'% cycle ,'-vvv' ]
    cudesc.input_data = ['%s/postexec.py'%(os.path.dirname(os.path.realpath(__file__)))]
    cudesc.post_exec = ['python postexec.py %s %s' % (Kconfig.nreps,cycle)]
    cudesc.mpi = True

    unit = umgr.submit_units(cudesc)

    unit.wait()

    print 'Analysis Execution time : ',(unit.stop_time - unit.start_time).total_seconds()

    return