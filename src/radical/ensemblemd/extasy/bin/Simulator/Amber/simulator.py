__author__ = 'vivek'

import radical.pilot
from radical.ensemblemd.mdkernels import MDTaskDescription
import os
import time
import saga
import sys


def Simulator(umgr,RPconfig,Kconfig,cycle):


    print 'Starting Simulation'

    if (Kconfig.num_cores_per_sim_cu < 2):
        print 'Amber MPI requires num_cores_per_sim_cu to be greater than or equal to 2'
        sys.exit(1)

    MY_STAGING_AREA = 'staging:///'

    #------------------------------------------------------------------
    # Extract filenames from paths from Kconfig file
    dict = {}
    dict['crdfile'] = Kconfig.initial_crd_file
    dict['crdfilename'] = os.path.basename(dict['crdfile'])
    dict['topfile'] = Kconfig.top_file
    dict['topfilename'] = os.path.basename(dict['topfile'])
    dict['mdin']    = Kconfig.md_input_file
    dict['mdinfilename'] = os.path.basename(dict['mdin'])
    dict['minin']   = Kconfig.minimization_input_file
    dict['mininfilename'] = os.path.basename(dict['minin'])
    dict['cycle'] = cycle
    #------------------------------------------------------------------

    start_times = []
    end_times = []
    cudesc_list_A = []


    for i in range(Kconfig.num_CUs):

        #==================================================================
        # CU Definition for Amber - Stage 1

        mdtd = MDTaskDescription()
        mdtd.kernel = "AMBER"
        mdtd.arguments = ['-O',
                          '-i', dict['mininfilename'],
                          '-o', 'min%s.out'%cycle,
                          '-inf', 'min%s.inf'%cycle,
                          '-r', 'md%s.crd'%cycle,
                          '-p', dict['topfilename'],
                          '-c', dict['crdfilename'],#
                          '-ref','min%s.crd'%cycle]
        mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
        cu = radical.pilot.ComputeUnitDescription()
        cu.cores = Kconfig.num_cores_per_sim_cu
        cu.mpi = True
        cu.executable = mdtd_bound.executable
        cu.pre_exec = mdtd_bound.pre_exec
        cu.arguments = mdtd_bound.arguments

        #==================================================================
        # Data Staging for the CU

        #------------------------------------------------------------------
        # Coordinate file staging

        if(cycle==0):

            crd_stage = {
                        'source': MY_STAGING_AREA + 'iter0/' + dict['crdfilename'],
                        'target': 'min0.crd',
                        'action': radical.pilot.LINK
                        }
        else:

            crd_stage = {
                        'source': MY_STAGING_AREA + 'iter{0}/min{0}{1}.crd'.format(cycle,i),
                        'target': 'min{0}.crd'.format(cycle),
                        'action': radical.pilot.LINK
                        }
        #------------------------------------------------------------------

        #------------------------------------------------------------------
        # Configure the staging directive for shared input file.
        top_stage = {
                    'source': MY_STAGING_AREA + dict['topfilename'],
                    'target': dict['topfilename'],
                    'action': radical.pilot.LINK
                    }
        minin_stage = {
                    'source': MY_STAGING_AREA + dict['mininfilename'],
                    'target': dict['mininfilename'],
                    'action': radical.pilot.LINK
                    }

        init_crd_stage = {
                    'source': MY_STAGING_AREA + dict['crdfilename'],
                    'target': dict['crdfilename'],
                    'action': radical.pilot.LINK
        }
        #------------------------------------------------------------------

        #------------------------------------------------------------------
        # Stage OUT the output to the staging area

        md_stage_out = {
                    'source': 'md{0}.crd'.format(cycle),
                    'target': MY_STAGING_AREA + 'iter{0}/md{0}{1}.crd'.format(cycle,i),
                    'action': radical.pilot.LINK
                    }
        #----------------------------------------------------------

        cu.input_staging = [crd_stage,top_stage,minin_stage,init_crd_stage]
        cu.output_staging = [md_stage_out]
        cudesc_list_A.append(cu)


    cudesc_list_B = []

    for i in range(0,Kconfig.num_CUs):

        #==================================================================
        # CU Definition for Amber - Stage 2
        mdtd = MDTaskDescription()
        mdtd.kernel = "AMBER"
        mdtd.arguments = ['-O',
                            '-i', dict['mdinfilename'],
                            '-o', 'md%s.out'%cycle,
                            '-inf', 'md%s.inf'%cycle,
                            '-x', 'md%s.ncdf'%cycle,
                            '-r', 'md%s.rst'%cycle,
                            '-p', dict['topfilename'],
                            '-c', 'md%s.crd'%cycle
                        ]
        mdtd_bound = mdtd.bind(resource=RPconfig.REMOTE_HOST)
        cudesc = radical.pilot.ComputeUnitDescription()
        cudesc.cores = Kconfig.num_cores_per_sim_cu
        cudesc.mpi = True
        cudesc.executable = mdtd_bound.executable
        cudesc.arguments = mdtd_bound.arguments
        cudesc.pre_exec = mdtd_bound.pre_exec

        #==================================================================
        # Data Staging

        #------------------------------------------------------------------
        # Link to output from first-stage of Amber
        md_stage_in = {
                        'source': MY_STAGING_AREA + 'iter{0}/md{0}{1}.crd'.format(cycle,i),
                        'target': 'md{0}.crd'.format(cycle),
                        'action': radical.pilot.LINK
                        }

        # Link to shared data from staging area
        mdin_stage = {
                        'source': MY_STAGING_AREA + dict['mdinfilename'],
                        'target': dict['mdinfilename'],
                        'action': radical.pilot.LINK
                        }
        top_stage = {
                        'source': MY_STAGING_AREA + dict['topfilename'],
                        'target': dict['topfilename'],
                        'action': radical.pilot.LINK
                    }

        cudesc.input_staging = [md_stage_in,mdin_stage,top_stage]
        #------------------------------------------------------------------


        #------------------------------------------------------------------
        # Link output data to staging area
        ncdf_stage_out = {
                        'source': 'md{0}.ncdf'.format(cycle),
                        'target': MY_STAGING_AREA + 'iter{0}/md_{0}_{1}.ncdf'.format(cycle, i),
                        'action': radical.pilot.COPY
                        }
        cudesc.output_staging = [ncdf_stage_out]
        #------------------------------------------------------------------

        #------------------------------------------------------------------
        # Directive to transfer data to localhost
        if((cycle+1)%Kconfig.nsave==0):
            md_transfer = {
                        'source': 'md{0}.ncdf'.format(cycle),
                        'target': 'backup/iter{0}/md_{0}_{1}.ncdf'.format(cycle,i)
                        }
            cudesc.output_staging.append(md_transfer)
        #----------------------------------------------------------    

        cudesc_list_B.append(cudesc)    

    #Submit all Amber CUs in Stage 1
    cu_list_A = umgr.submit_units(cudesc_list_A)

    cu_list_B = []
    cu_list_A_copy = cu_list_A[:]

    while cu_list_A:
        for cu_a in cu_list_A:
            idx = cu_list_A_copy.index(cu_a)
            cu_a.wait ()
            cu_list_B.append(umgr.submit_units(cudesc_list_B[idx]))
            cu_list_A.remove(cu_a)

    for cu_b in cu_list_B:
        cu_b.wait()

    try:
        for unit_a in cu_list_A_copy:
            start_times.append(unit_a.start_time)

        for unit_b in cu_list_B:
            end_times.append(unit_b.stop_time)

        print 'Simulation Execution Time : ', (max(end_times)-min(start_times)).total_seconds()

    except:
        pass

