__author__ = 'vivek'

from radical.ensemblemd.mdkernels import MDTaskDescription
import radical.pilot
import os
import saga

def exists_remote(host, paths):
    qpath = ''
    for path in paths:
        qpath += 'test -f {0};'.format(pipes.quote(path))
    proc = subprocess.Popen(['ssh', host, qpath])
    proc.wait()
    return proc.returncode == 0


MY_STAGING_AREA = 'staging:///'

def Analyzer(umgr,RPconfig,Kconfig,cycle,pilot):


    if (cycle == 0):
        print 'Skipping Analysis for iteration 0'
        return

    print 'Starting Analysis'

    #==================================================================
    # CU Definition for CoCo

    mdtd=MDTaskDescription()
    mdtd.kernel="CoCo"
    mdtd.arguments = ['-l','-c','pyCoCo --grid %s --dims %s --frontpoints %s --topfile %s --mdfile *.ncdf --output pentaopt%s --logfile %s --mpi'%(Kconfig.grid,Kconfig.dims,Kconfig.num_CUs,os.path.basename(Kconfig.top_file),cycle,Kconfig.logfile)]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    cudesc = radical.pilot.ComputeUnitDescription()
    cudesc.cores = Kconfig.num_CUs  #pyCoCo should use as many as cores as the number of frontpoints
    cudesc.executable = mdtd_bound.executable
    cudesc.pre_exec = mdtd_bound.pre_exec
    cudesc.arguments = mdtd_bound.arguments
    cudesc.post_exec = mdtd_bound.post_exec + ['python postexec.py %s %s' % (Kconfig.num_CUs,cycle)]
    cudesc.mpi = True


    #==================================================================
    # Data Staging for the CU

    #------------------------------------------------------------------
    # postexec and topology file staging

    postexec_stage = {
                    'source': MY_STAGING_AREA + 'postexec.py',
                    'target': 'postexec.py',
                    'action': radical.pilot.LINK
                }

    top_stage = {
                    'source': MY_STAGING_AREA + os.path.basename(Kconfig.top_file),
                    'target': os.path.basename(Kconfig.top_file),
                    'action': radical.pilot.LINK
                }
    cudesc.input_staging = [postexec_stage,top_stage]
    #------------------------------------------------------------------


    #------------------------------------------------------------------
    # stage in the ncdf files from all previous iterations
    for iter in range(0,cycle):
        for inst in range(0,Kconfig.num_CUs):
            dir = {
                    'source': MY_STAGING_AREA + 'iter{0}/md_{0}_{1}.ncdf'.format(iter,inst),
                    'target': 'md_{0}_{1}.ncdf'.format(iter,inst),
                    'action': radical.pilot.COPY
                    }
            cudesc.input_staging.append(dir)
    #------------------------------------------------------------------

    cudesc.output_staging = []
    #------------------------------------------------------------------
    # stage out the crd files to staging area
    for inst in range(0,Kconfig.num_CUs):
        dir = {
                'source': 'min{0}{1}.crd'.format(cycle,inst),
                'target': MY_STAGING_AREA + 'iter{0}/min{0}{1}.crd'.format(cycle,inst),
                'action': radical.pilot.LINK
                }
        cudesc.output_staging.append(dir)
    #------------------------------------------------------------------

    #------------------------------------------------------------------
    # transfer logfile to localhost
    if((cycle+1)%Kconfig.nsave == 0):
        logfile_transfer = {
                            'source': '%s'%Kconfig.logfile,
                            'target': 'backup/iter{0}/{0}_{1}'.format(cycle,Kconfig.logfile)
                        }
        cudesc.output_staging.append(logfile_transfer)
    #------------------------------------------------------------------


    #------------------------------------------------------------------
    # transfer the ncdf files from all previous iterations
        for iter in range(0,cycle):
            for inst in range(0,Kconfig.num_CUs):
                dir = {
                    'source': 'md_{0}_{1}.ncdf'.format(iter,inst),
                    'target': 'backup/iter{2}/md_{0}_{1}.ncdf'.format(iter,inst,cycle),
                    }
                cudesc.output_staging.append(dir)
    #------------------------------------------------------------------

    unit = umgr.submit_units(cudesc)

    unit.wait()


    if (cycle+1)%Kconfig.checkfiles==0:

        if pilot.resource == 'xsede.stampede':
            remote='stampede.tacc.utexas.edu'
        else:
            remote='login.archer.ac.uk'

        paths=[]
        for i in range(0,Kconfig.num_CUs):
            paths.append(saga.Url(pilot.sandbox).path + 'staging_area/iter{0}/min{0}{1}.crd'.format(cycle,i))
        
        if exists_remote('{0}@{1}'.format(RPconfig.UNAME,remote),paths):
            print 'All expected files present on remote'
        else:
            print 'Error finding expected files on remote'
            sys.exit(-1)

    try:
        print 'Analysis Execution time : ',(unit.stop_time - unit.start_time).total_seconds()

    except:
        pass

    return