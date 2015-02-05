__author__ = 'vivek'

import radical.pilot
import saga
import glob
import sys
import os

def param_check(Kconfig):

    pass

def Preprocessing(Kconfig,umgr,cycle,paths):

    list_of_files = []

    print 'Preprocessing stage ....'

    if(cycle==0):
        curdir = os.path.dirname(os.path.realpath(__file__))
        list_of_files = [Kconfig.initial_crd_file,Kconfig.md_input_file,Kconfig.minimization_input_file
            ,Kconfig.top_file,'%s/../../Analyzer/CoCo/postexec.py'%curdir]

        cud = radical.pilot.ComputeUnitDescription()
        cud.cores = 1
        cud.mpi = False
        cud.executable = '/bin/echo'
        cud.arguments = ['1']
        cud.input_staging = list_of_files

        cu = umgr.submit_units(cud)

        umgr.wait_units()

        init_path=saga.Url(cu.working_directory).path

        return [init_path]



    elif((cycle!=0)and(cycle%Kconfig.nsave==0)):
        for file in glob.glob('%s/backup/iter%s/*.ncdf'%(os.getcwd(),cycle)):
            list_of_files.append(file)

        cud = radical.pilot.ComputeUnitDescription()
        cud.cores = 1
        cud.mpi = False
        cud.executable = '/bin/echo'
        cud.arguments = ['2']
        #cud.pre_exec = ['ln %s/min%s*.crd .'%(paths[cycle-1],cycle)]
        cud.input_staging = list_of_files

        cu = umgr.submit_units(cud)

        umgr.wait_units()

        rem_path=saga.Url(cu.working_directory).path

        return [rem_path]


    else:

        cud = radical.pilot.ComputeUnitDescription()
        cud.cores = 1
        cud.mpi = False
        cud.executable = '/bin/echo'
        cud.arguments = ['3']
        cud.pre_exec = ['ln %s/*.ncdf .'%(paths[cycle-1])]

        cu = umgr.submit_units(cud)

        umgr.wait_units()

        rem_path=saga.Url(cu.working_directory).path

        return [rem_path]