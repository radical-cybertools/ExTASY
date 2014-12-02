
from radical.ensemblemd.mdkernels import MDTaskDescription
import radical.pilot
import os
import glob

def Analyzer(umgr,RPconfig,Kconfig,cycle,paths):


    if (cycle == 0):
        print 'Skipping Analysis for iteration 0'
        return

    print 'Starting Analysis'
    curdir = os.path.dirname(os.path.realpath(__file__))

    print 'Submitting COCO Compute Unit'

    mdtd=MDTaskDescription()
    mdtd.kernel="CoCo"
    mdtd.arguments = ['-l','-c','pyCoCo --grid %s --dims %s --frontpoints %s --topfile %s --mdfile *.ncdf --output pentaopt%s --logfile %s'%(Kconfig.grid,Kconfig.dims,Kconfig.num_CUs,os.path.basename(Kconfig.top_file),cycle,Kconfig.logfile)]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    cudesc = radical.pilot.ComputeUnitDescription()
    cudesc.cores = RPconfig.PILOTSIZE
    cudesc.executable = mdtd_bound.executable
    cudesc.pre_exec = mdtd_bound.pre_exec
    cudesc.arguments = mdtd_bound.arguments
    cudesc.pre_exec = cudesc.pre_exec + ['ln %s/postexec.py .'%paths[0],'ln %s/%s .'%(paths[0],Kconfig.top_file)]
    for i in range(0,len(paths)):
        cudesc.pre_exec = cudesc.pre_exec + ['ln %s/*.ncdf .'%paths[i]]
    cudesc.post_exec = ['export PYTHONPATH=/home1/01915/laughton/.public/lib/python2.7/site-packages/extasy.coco-0.1-py2.7.egg:$PYTHONPATH','python postexec.py %s %s' % (Kconfig.num_CUs,cycle)]
    cudesc.mpi = True
    if((cycle+1)%Kconfig.nsave==0):
            cudesc.output_staging = ['%s > %s_%s'%(Kconfig.logfile,cycle,Kconfig.logfile)]
    cudesc.post_exec = cudesc.post_exec + ['ln min%s*.crd %s/'%(cycle,paths[cycle])]

    unit = umgr.submit_units(cudesc)

    unit.wait()

    try:
        print 'Analysis Execution time : ',(unit.stop_time - unit.start_time).total_seconds()

    except:
        pass

    return