
from radical.ensemblemd.mdkernels import MDTaskDescription
import radical.pilot
import os

def Analyzer(umgr,RPconfig,Kconfig,cycle):

    print 'Starting Analysis'

    cycle=cycle+1

    print 'Submitting COCO Compute Unit'

    mdtd=MDTaskDescription()
    mdtd.kernel="CoCo"
    mdtd.arguments = ['cocoUi.py','--grid',Kconfig.grid,'--projs',Kconfig.projs,'--frontpoints',Kconfig.frontpoints,'--cycle','%s'% cycle ,'-vvv' ]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    cudesc = radical.pilot.ComputeUnitDescription()
    cudesc.cores = RPconfig.PILOTSIZE
    cudesc.executable = mdtd_bound.executable
    cudesc.pre_exec = mdtd_bound.pre_exec
    cudesc.pre_exec.append('cp postexec.py %s'%Kconfig.exp_loc)
    cudesc.pre_exec.append('cd %s'%Kconfig.exp_loc)
    cudesc.arguments = mdtd_bound.arguments
    cudesc.input_staging = ['%s/postexec.py'%(os.path.dirname(os.path.realpath(__file__)))]
    cudesc.post_exec = ['python postexec.py %s %s' % (Kconfig.nreps,cycle)]
    cudesc.mpi = True

    unit = umgr.submit_units(cudesc)

    unit.wait()

    print 'Analysis Execution time : ',(unit.stop_time - unit.start_time).total_seconds()

    return