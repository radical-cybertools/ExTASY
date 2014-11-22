__author__ = 'vivek'

import radical.pilot
import saga
import glob
import sys
import os

def Preprocessing(Kconfig,umgr,cycle,paths):

    list_of_files = []

    if(cycle==0):
        curdir = os.path.dirname(os.path.realpath(__file__))
        list_of_files = [Kconfig.md_input_file,Kconfig.mdp_file,Kconfig.top_file,Kconfig.lsdm_config_file,
                         '%s/gro.py'%curdir,'%s/spliter.py','%s/../../Simulator/Gromacs/run.py'%curdir,

                         ]

        if Kconfig.ndx_file is not None:
            list_of_files.append('%s' % Kconfig.ndx_file)
        if Kconfig.itp_file_loc is not None:
            for itpfile in glob.glob(Kconfig.itp_file_loc + '*.itp'):
                list_of_files.append('%s' % itpfile)

        cud = radical.pilot.ComputeUnitDescription()
        cud.cores = 1
        cud.mpi = False
        cud.executable = 'python'
        cud.arguments = ['spliter.py',Kconfig.num_CUs,os.path.basename(Kconfig.md_input_file)]
        cud.input_staging = list_of_files

        cu = umgr.submit_units(cud)

        cu.wait()

        init_path=saga.Url(cu.working_directory).path

        return [init_path]

    elif((cycle!=0)and(cycle%Kconfig.nsave==0)):
        list_of_files = ['%s/backup/%s_%s'%(os.getcwd(),cycle,os.path.basename(Kconfig.md_input_file))]

        cud = radical.pilot.ComputeUnitDescription()
        cud.cores = 1
        cud.mpi = False
        cud.executable = 'python'
        cud.pre_exec = ['cp %s/gro.py .'% paths[0] ,'cp %s/spliter.py .'% paths[0]]
        cud.arguments = ['spliter.py',Kconfig.num_CUs,'%s_%s'%(cycle,os.path.basename(Kconfig.md_input_file))]
        cud.input_staging = list_of_files

        cu = umgr.submit_units(cud)

        cu.wait()

        rem_path=saga.Url(cu.working_directory).path

        return [rem_path]

    else:

        cud = radical.pilot.ComputeUnitDescription()
        cud.cores = 1
        cud.mpi = False
        cud.executable = 'python'
        cud.arguments = ['spliter.py',Kconfig.num_CUs,'%s_%s'%(cycle,os.path.basename(Kconfig.md_input_file))]
        cud.pre_exec = ['cp %s/gro.py .'%paths[0],'cp %s/spliter.py .'% paths[0], 'cp %s/%s_%s' %(paths[cycle-1],cycle,os.path.basename(Kconfig.md_input_file))]

        cu = umgr.submit_units(cud)

        cu.wait()

        rem_path=saga.Url(cu.working_directory).path

        return [rem_path]