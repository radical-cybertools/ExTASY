__author__ = 'vivek'

from radical.ensemblemd.mdkernels import MDTaskDescription
import radical.pilot
import os
import saga
import subprocess
import pipes

def exists_remote(host, paths):
    qpath = ''
    for path in paths:
        qpath += 'test -f {0};'.format(pipes.quote(path))
    proc = subprocess.Popen(['ssh', host, qpath])
    proc.wait()
    return proc.returncode == 0

def Analyzer(umgr,RPconfig,Kconfig,cycle,pilot):

    print 'Starting Analysis'
    MY_STAGING_AREA = 'staging:///'

    nearest_neighbor_file = 'neighbors.nn'
    evfile = 'tmpha.ev'
    num_clone_files = 'ncopies.nc'
    outgrofile_name = 'out.gro'

    curdir = os.path.dirname(os.path.realpath(__file__))
    
    #==================================================================
    # CU Definition for Trjconv

    mdtd=MDTaskDescription()
    mdtd.kernel="GROMACS"
    mdtd.arguments = ['pre_analyze.py','{0}'.format(Kconfig.num_CUs),'{0}'.format(Kconfig.md_output_file)]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    trjconv = radical.pilot.ComputeUnitDescription()
    trjconv.pre_exec = mdtd_bound.pre_exec
    trjconv.executable = 'python'
    trjconv.arguments = mdtd_bound.arguments
    trjconv.mpi = True
    trjconv.cores = 1


    #==================================================================
    # Data Staging for the CU

    #-------------------------------------------------------------------------------------------------------------------
    # Stage-in the output of the simulation stage which is present 
    # in the staging area

    pre_ana_stage = {
                        'source':MY_STAGING_AREA + 'pre_analyze.py',
                        'target':'pre_analyze.py',
                        'action': radical.pilot.LINK
                    }

    trjconv.input_staging = [pre_ana_stage]

    for inst in range(0,Kconfig.num_CUs):
        temp = {
                    'source': MY_STAGING_AREA + 'iter{0}/out{1}.gro'.format(cycle,inst),
                    'target': 'out{0}.gro'.format(inst),
                    'action': radical.pilot.LINK
        }
        trjconv.input_staging.append(temp)    
    #-------------------------------------------------------------------------------------------------------------------


    #-------------------------------------------------------------------------------------------------------------------
    # Stage out tmpha.gro to the staging area

    md_stage_out = {
                        'source': Kconfig.md_output_file,
                        'target': MY_STAGING_AREA + 'iter{0}/{1}'.format(cycle,Kconfig.md_output_file),
                        'action': radical.pilot.LINK
                    }

    tmpha_out = {
                    'source':'tmpha.gro',
                    'target':MY_STAGING_AREA + 'iter{0}/tmpha.gro'.format(cycle),
                    'action': radical.pilot.LINK
                }

    trjconv.output_staging = [md_stage_out,tmpha_out]
    #-------------------------------------------------------------------------------------------------------------------

    trjconvCU = umgr.submit_units(trjconv)
    trjconvCU.wait()

    #==================================================================
    # CU Definition for LSDMap
    
    
    mdtd=MDTaskDescription()
    mdtd.kernel="LSDMAP"
    mdtd.arguments = ['lsdm.py','-f','config.ini','-c','tmpha.gro','-n','%s'%nearest_neighbor_file,'-w','%s' %Kconfig.w_file]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    lsdm=radical.pilot.ComputeUnitDescription()
    lsdm.pre_exec = mdtd_bound.pre_exec
    lsdm.executable = mdtd_bound.executable
    lsdm.arguments = mdtd_bound.arguments
    lsdm.mpi = True
    lsdm.cores = RPconfig.PILOTSIZE


    #==================================================================
    # Data Staging for the CU
    
    
    #-------------------------------------------------------------------------------------------------------------------
    # tmpha, config and analyzer input staging

    tmpha_stage = {
                    'source': MY_STAGING_AREA + 'iter{0}/tmpha.gro'.format(cycle),
                    'target': 'tmpha.gro',
                    'action': radical.pilot.LINK
        }

    config_stage = {
                        'source': MY_STAGING_AREA + 'config.ini',
                        'target': 'config.ini',
                        'action': radical.pilot.LINK
                    }

    ana_stage = {
                        'source': MY_STAGING_AREA + 'run_analyzer.sh',
                        'target': 'run_analyzer.sh',
                        'action': radical.pilot.LINK
                }

    lsdm_stage = {
                        'source': MY_STAGING_AREA + 'lsdm.py',
                        'target': 'lsdm.py',
                        'action': radical.pilot.LINK
    }

    lsdm.input_staging = [tmpha_stage,config_stage,ana_stage,lsdm_stage]
    #-------------------------------------------------------------------------------------------------------------------
    

    #-------------------------------------------------------------------------------------------------------------------
    # Stage-in the weight file from the previous iteration
    
    if(cycle>0):
        weight_stage_in = {
                            'source': MY_STAGING_AREA + 'iter{0}/weight.w'.format(cycle-1),
                            'transfer': 'weight.w',
                            'action': radical.pilot.LINK
                    }
        lsdm.input_staging.append (weight_stage_in)
    #-------------------------------------------------------------------------------------------------------------------


    #-------------------------------------------------------------------------------------------------------------------
    # Stage-out neighbors, eigen vector file + output of lsdmap
    nn_stage_out = {
                        'source': nearest_neighbor_file,
                        'target': MY_STAGING_AREA + 'iter{0}/{1}'.format(cycle,nearest_neighbor_file),
                        'action': radical.pilot.LINK
                    }

    ev_stage_out = {
                        'source': evfile,
                        'target': MY_STAGING_AREA + 'iter{0}/{1}'.format(cycle,evfile),
                        'action': radical.pilot.LINK
                    }
    
    lsdm.output_staging = [nn_stage_out,ev_stage_out]
    
    #-------------------------------------------------------------------------------------------------------------------


    #-------------------------------------------------------------------------------------------------------------------
    # Stage-out LSDMap log file when necessary
    if ((cycle+1)%Kconfig.nsave == 0):
        logfile_transfer = {
                        'source': 'lsdmap.log',
                        'target': 'backup/iter{0}/lsdmap.log'.format(cycle)
                        }

        lsdm.output_staging.append(logfile_transfer)
    #-------------------------------------------------------------------------------------------------------------------

    lsdmCU = umgr.submit_units(lsdm)
    lsdmCU.wait()
    
    #==================================================================
    
    
    #==================================================================
    # CU Definition for Selection + Reweighting

    print 'Select + Reweighting step'
    
    post=radical.pilot.ComputeUnitDescription()
    post.pre_exec = mdtd_bound.post_exec


    #-------------------------------------------------------------------------------------------------------------------
    # Stage-in postanalyzer, select and reweight python files
    post_ana_stage = {
                        'source': MY_STAGING_AREA + 'post_analyze.py',
                        'target': 'post_analyze.py',
                        'action': radical.pilot.LINK
                    }

    select_stage = {
                        'source': MY_STAGING_AREA + 'selection.py',
                        'target': 'selection.py',
                        'action': radical.pilot.LINK
                    }

    reweight_stage = {
                        'source': MY_STAGING_AREA + 'reweighting.py',
                        'target': 'reweighting.py',
                        'action': radical.pilot.LINK
                    }
    #-------------------------------------------------------------------------------------------------------------------
    
    #-------------------------------------------------------------------------------------------------------------------
    # Stage-in neighbor, eigen vector, lsdmap output + weight file
    nn_stage_in = {
                        'source': MY_STAGING_AREA + 'iter{0}/{1}'.format(cycle,nearest_neighbor_file),
                        'target': nearest_neighbor_file,
                        'action': radical.pilot.LINK
                }

    ev_stage_in = {
                        'source': MY_STAGING_AREA + 'iter{0}/{1}'.format(cycle,evfile),
                        'target': evfile,
                        'action': radical.pilot.LINK
                }

    md_stage_in = {
                        'source': MY_STAGING_AREA + 'iter{0}/{1}'.format(cycle,Kconfig.md_output_file),
                        'target': Kconfig.md_output_file,
                        'action': radical.pilot.LINK
                }

    #-------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------
    # Stage-in spliter to split the reweighted coordinate file for
    # next iteration
    
    spliter_stage = {
                        'source': MY_STAGING_AREA + 'spliter.py',
                        'target': 'spliter.py',
                        'action': radical.pilot.LINK
                }

    post.input_staging = [post_ana_stage,select_stage,reweight_stage,nn_stage_in,ev_stage_in,md_stage_in,
                          spliter_stage]

    if(cycle>0):
        weight_stage_in = {
                            'source': MY_STAGING_AREA + 'iter{0}/weight.w'.format(cycle-1),
                            'transfer': 'weight.w',
                            'action': radical.pilot.COPY
                    }
        post.input_staging.append(weight_stage_in)

    #-------------------------------------------------------------------------------------------------------------------
    
    
    post.executable = 'python'
    post.arguments = ['post_analyze.py',Kconfig.num_runs,evfile,num_clone_files,Kconfig.md_output_file,nearest_neighbor_file,
                         Kconfig.w_file,outgrofile_name,Kconfig.max_alive_neighbors,Kconfig.max_dead_neighbors,
                         os.path.basename(Kconfig.md_input_file),cycle,Kconfig.num_CUs]

    
    #-------------------------------------------------------------------------------------------------------------------
    # Stage-out+transfer weight file and new coordinate file
    
    if((cycle+1)%Kconfig.nsave==0):

        wfile_transfer = {
                            'source': 'weight.w',
                            'target': 'backup/iter{0}/weight.w'.format(cycle)
                        }
        wfile_stage = {
                            'source': 'weight.w',
                            'target': MY_STAGING_AREA + 'iter{0}/weight.w'.format(cycle),
                            'action': radical.pilot.COPY
                        }

        md_transfer = {
                            'source': '{0}_{1}'.format(cycle+1,os.path.basename(Kconfig.md_input_file)),
                            'target': 'backup/iter{0}/{1}_{2}'.format(cycle,cycle+1,os.path.basename(Kconfig.md_input_file)),
        }

        md_stage = {
                            'source': '{0}_{1}'.format(cycle+1,os.path.basename(Kconfig.md_input_file)),
                            'target': MY_STAGING_AREA + 'iter{0}/{1}_{2}'.format(cycle,cycle+1,os.path.basename(Kconfig.md_input_file)),
                            'action': radical.pilot.LINK
        }

        post.output_staging = [wfile_stage,wfile_transfer,md_transfer,md_stage]
        
    else:

        wfile_stage = {
                            'source': 'weight.w',
                            'target': MY_STAGING_AREA + 'iter{0}/weight.w'.format(cycle),
                            'action': radical.pilot.COPY
                        }

        md_stage = {
                            'source': '{0}_{1}'.format(cycle+1,os.path.basename(Kconfig.md_input_file)),
                            'target': MY_STAGING_AREA + 'iter{0}/{1}_{2}'.format(cycle,cycle+1,os.path.basename(Kconfig.md_input_file)),
                            'action': radical.pilot.LINK
        }
               
        post.output_staging = [wfile_stage,md_stage]
        
    #-------------------------------------------------------------------------------------------------------------------

    #-------------------------------------------------------------------------------------------------------------------
    # Stage-out the split coordinate files for next iteration
    if (cycle < Kconfig.start_iter + Kconfig.num_iterations - 1):
        for inst in range(0,Kconfig.num_CUs):
            temp = {
                        'source': 'temp/start{0}.gro'.format(inst),
                        'target': MY_STAGING_AREA + 'iter{0}/start{1}.gro'.format(cycle+1,inst),
                        'action': radical.pilot.LINK
                }
            post.output_staging.append(temp)
    #-------------------------------------------------------------------------------------------------------------------
    postCU = umgr.submit_units(post)
    postCU.wait()


    if (cycle+1)%Kconfig.checkfiles==0:

        if pilot.resource == 'xsede.stampede':
            remote='stampede.tacc.utexas.edu'
        else:
            remote='login.archer.ac.uk'

        paths=[]
        for i in range(0,Kconfig.num_CUs):
            paths.append(saga.Url(pilot.sandbox).path + 'staging_area/iter{0}/start{1}.gro'.format(cycle+1,i))
        
        if exists_remote('{0}@{1}'.format(RPconfig.UNAME,remote),paths):
            print 'All expected files present on remote'
        else:
            print 'Error finding expected files on remote'
            sys.exit(-1)

    try:
        print 'Analysis Execution time : ',((trjconvCU.stop_time-trjconvCU.start_time).total_seconds()+
                                            (lsdmCU.stop_time - lsdmCU.start_time).total_seconds()+
                                            (postCU.stop_time - postCU.start_time).total_seconds())

    except:
        pass

    return
