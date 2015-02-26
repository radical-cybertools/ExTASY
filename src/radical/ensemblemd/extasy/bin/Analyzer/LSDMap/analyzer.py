__author__ = 'vivek'

from radical.ensemblemd.mdkernels import MDTaskDescription
import radical.pilot
import os

def Analyzer(umgr,RPconfig,Kconfig,cycle):

    print 'Starting Analysis'
    MY_STAGING_AREA = 'staging:///'

    nearest_neighbor_file = 'neighbors.nn'
    evfile = 'tmpha.ev'
    num_clone_files = 'ncopies.nc'
    outgrofile_name = 'out.gro'

    curdir = os.path.dirname(os.path.realpath(__file__))
    
    #==================================================================
    # CU Definition for LSDMap
    
    
    mdtd=MDTaskDescription()
    mdtd.kernel="LSDMAP"
    mdtd.arguments = ['-f','config.ini','-c','tmpha.gro','-n','%s'%nearest_neighbor_file,'-w','%s' %Kconfig.w_file]
    mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
    lsdm=radical.pilot.ComputeUnitDescription()
    lsdm.pre_exec = ['module load gromacs']
    lsdm.pre_exec = lsdm.pre_exec + ['python pre_analyze.py %s %s'%(Kconfig.num_CUs,Kconfig.md_output_file)]
    lsdm.pre_exec = lsdm.pre_exec + ['echo 2 | trjconv -f %s -s %s -o tmpha.gro'%(Kconfig.md_output_file,Kconfig.md_output_file)]
    lsdm.pre_exec = lsdm.pre_exec + mdtd_bound.pre_exec
    lsdm.executable = mdtd_bound.executable
    lsdm.arguments = mdtd_bound.arguments
    lsdm.mpi = True
    lsdm.cores = RPconfig.PILOTSIZE


    #==================================================================
    # Data Staging for the CU
    
    
    #-------------------------------------------------------------------------------------------------------------------
    # preanalyze, config and analyzer input staging

    pre_ana_stage = {
                        'source': MY_STAGING_AREA + 'pre_analyze.py',
                        'target': 'pre_analyze.py',
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

    lsdm.input_staging = [pre_ana_stage,config_stage,ana_stage]
    #-------------------------------------------------------------------------------------------------------------------
    
    
    #-------------------------------------------------------------------------------------------------------------------
    # Stage-in the output of the simulation stage which is present 
    # in the staging area
    
    for inst in range(0,Kconfig.num_CUs):
        temp = {
                    'source': MY_STAGING_AREA + 'iter{0}/out{1}.gro'.format(cycle,inst),
                    'target': 'out{0}.gro'.format(inst),
                    'action': radical.pilot.LINK
        }
        lsdm.input_staging.append(temp)
    
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

    md_stage_out = {
                        'source': Kconfig.md_output_file,
                        'target': MY_STAGING_AREA + 'iter{0}/{1}'.format(cycle,Kconfig.md_output_file),
                        'action': radical.pilot.LINK
                    }
    
    lsdm.output_staging = [nn_stage_out,ev_stage_out,md_stage_out]
    
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
                        'source': MY_STAGING_AREA + 'select.py',
                        'target': 'select.py',
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
        post.input_staging.append (weight_stage_in)

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
    if (cycle < Kconfig.num_iterations):
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

    try:
        print 'Analysis Execution time : ',((lsdmCU.stop_time - lsdmCU.start_time).total_seconds()+(postCU.stop_time - postCU.start_time).total_seconds())

    except:
        pass

    return
