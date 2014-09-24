
from radical.ensemblemd.mdkernels import MDTaskDescription
import radical.pilot
import os

def Analyzer(umgr,RPconfig,Kconfig,cycle):

    print 'Starting Analysis'
    curdir = os.path.dirname(os.path.realpath(__file__))
    cyc=cycle+1

    print 'Submitting COCO Compute Unit'

    mdtd=MDTaskDescription()
    mdtd.kernel="CoCo"
    mdtd.arguments = ['-l','-c','python pycoco.py --grid %s --dims %s --frontpoints %s --topfile %s --mdfile *.ncdf --output pentaopt%s'%(Kconfig.grid,Kconfig.dims,Kconfig.frontpoints,Kconfig.topfile,cycle) ]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    cudesc = radical.pilot.ComputeUnitDescription()
    cudesc.cores = RPconfig.PILOTSIZE
    cudesc.executable = mdtd_bound.executable
    cudesc.pre_exec = mdtd_bound.pre_exec
    cudesc.arguments = mdtd_bound.arguments
    cudesc.input_staging = ['%s/postexec.py'%curdir,'%s/pycoco.py'%curdir,'%s/%s'%(Kconfig.top_loc,Kconfig.topfile)]
    for i in range(0,Kconfig.nreps):
            cudesc.input_staging.append('md_%s_%s.ncdf'%(cycle,i))
    cudesc.post_exec = ['python postexec.py %s %s' % (Kconfig.nreps,cycle)]
    cudesc.mpi = True
    cudesc.output_staging = []
    for i in range(0,Kconfig.nreps):
        cudesc.output_staging.append('min%s%s.crd'%(cyc,i))

    unit = umgr.submit_units(cudesc)

    unit.wait()

    print 'Analysis Execution time : ',(unit.stop_time - unit.start_time).total_seconds()

    return