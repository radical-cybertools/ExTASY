
from radical.ensemblemd.mdkernels import MDTaskDescription
import radical.pilot
import os
import glob

def Analyzer(umgr,RPconfig,Kconfig,cycle,paths):

    print 'Starting Analysis'
    curdir = os.path.dirname(os.path.realpath(__file__))

    print 'Submitting COCO Compute Unit'

    mdtd=MDTaskDescription()
    mdtd.kernel="CoCo"
    mdtd.arguments = ['-l','-c','pyCoCo --grid %s --dims %s --frontpoints %s --topfile %s --mdfile *.ncdf --output pentaopt%s'%(Kconfig.grid,Kconfig.dims,Kconfig.num_CUs,os.path.basename(Kconfig.top_file),cycle)]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    cudesc = radical.pilot.ComputeUnitDescription()
    cudesc.cores = RPconfig.PILOTSIZE
    cudesc.executable = mdtd_bound.executable
    cudesc.pre_exec = mdtd_bound.pre_exec
    cudesc.arguments = mdtd_bound.arguments
    #cudesc.input_staging = ['%s/postexec.py'%curdir,'%s/pycoco.py'%curdir,'%s'%(Kconfig.top_file)]
    cudesc.pre_exec = cudesc.pre_exec + ['cp %s/postexec.py .'%paths[0],'cp %s/%s .'%(paths[0],Kconfig.top_file)]
    #for file in glob.glob('*.ncdf'):
    #    cudesc.input_staging.append(file)
    for i in range(0,len(paths)):
        cudesc.pre_exec = cudesc.pre_exec + ['cp %s/*.ncdf .'%paths[i]]
    cudesc.post_exec = ['python postexec.py %s %s' % (Kconfig.num_CUs,cycle)]
    cudesc.mpi = True
    if((cycle+1)%Kconfig.nsave==0):
        cudesc.output_staging = []
        for i in range(0,Kconfig.num_CUs):
            cudesc.output_staging.append('min%s%s.crd'%(cycle+1,i))
    else:
        cudesc.post_exec = cudesc.post_exec + ['cp min%s*.crd %s/'%(cycle+1,paths[cycle])]

    unit = umgr.submit_units(cudesc)

    unit.wait()

    try:
        print 'Analysis Execution time : ',(unit.stop_time - unit.start_time).total_seconds()

    except:
        pass

    return