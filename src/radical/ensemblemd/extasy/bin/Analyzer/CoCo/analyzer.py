
from radical.ensemblemd.mdkernels import MDTaskDescription
import time
import radical.pilot
import os
import imp

def Analyzer(umgr,RPconfig,Kconfig,cycle):

    print 'Starting Analysis'
    cycle=cycle+1

    print 'Submitting COCO Compute Unit'

    cudesc = radical.pilot.ComputeUnitDescription()
    cudesc.executable = 'python'
    cudesc.cores = RPconfig.PILOTSIZE
    cudesc.pre_exec = ['module load python','cp postexec.py %s'% Kconfig.exp_loc,'cd %s' % Kconfig.exp_loc,'module load mpi4py','module load amber']
    cudesc.arguments = ['cocoUi.py','--grid',Kconfig.grid,'--projs',Kconfig.projs,'--frontpoints',Kconfig.frontpoints,'--cycle','%s'% cycle ,'-vvv' ]
    cudesc.input_staging = ['%s/postexec.py'%(os.path.dirname(os.path.realpath(__file__)))]
    cudesc.post_exec = ['python postexec.py %s %s' % (Kconfig.nreps,cycle)]
    cudesc.mpi = True

    unit = umgr.submit_units(cudesc)

    unit.wait()

    print 'Analysis Execution time : ',(unit.stop_time - unit.start_time).total_seconds()

    return