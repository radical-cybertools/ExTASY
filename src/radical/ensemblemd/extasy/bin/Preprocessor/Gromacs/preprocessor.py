__author__ = 'vivek'

import radical.pilot
import saga
import glob
import sys
import os

def Preprocessing(Kconfig,umgr,cycle,paths):

    list_of_files = []

    print 'Preprocessing stage ....'

    if(cycle==0):
        curdir = os.path.dirname(os.path.realpath(__file__))
        list_of_files = [Kconfig.md_input_file,Kconfig.mdp_file,Kconfig.top_file,Kconfig.lsdm_config_file,
                         '%s/gro.py'%curdir,'%s/spliter.py'%curdir,'%s/../../Simulator/Gromacs/run.py'%curdir,
                         '%s/../../Analyzer/LSDMap/pre_analyze.py'%curdir,
                         '%s/../../Analyzer/LSDMap/run_analyzer.sh'%curdir,
                         '%s/../../Analyzer/LSDMap/lsdm.py'%curdir,
                         '%s/../../Analyzer/LSDMap/post_analyze.py'%curdir,
                         '%s/../../Analyzer/LSDMap/select.py'%curdir,
                         '%s/../../Analyzer/LSDMap/reweighting.py'%curdir,
                         '%s/../../Analyzer/LSDMap/lsdmap/rw/reader.py'%curdir,
                         '%s/../../Analyzer/LSDMap/lsdmap/rw/writer.py'%curdir,
                         '%s/../../Analyzer/LSDMap/lsdmap/rw/ev.py'%curdir,
                         '%s/../../Analyzer/LSDMap/lsdmap/rw/gro.py > grofile.py'%curdir,
                         '%s/../../Analyzer/LSDMap/lsdmap/rw/sl.py'%curdir,
                         '%s/../../Analyzer/LSDMap/lsdmap/rw/xvg.py'%curdir
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
        cud.pre_exec = ['mkdir lsdmap','cd lsdmap','touch __init__.py','mkdir rw','cd rw','touch __init__.py',
                        'cd ..','cd ..',
                        'mv ev.py lsdmap/rw/','mv grofile.py lsdmap/rw/gro.py',
                        'mv reader.py lsdmap/rw/','mv sl.py lsdmap/rw/',
                        'mv writer.py lsdmap/rw/','mv xvg.py lsdmap/rw/',
                        ]
        cud.arguments = ['spliter.py',Kconfig.num_CUs,os.path.basename(Kconfig.md_input_file)]
        cud.input_staging = list_of_files

        cu = umgr.submit_units(cud)

        cu.wait()

        init_path=saga.Url(cu.working_directory).path

        return [init_path]


    elif((cycle!=0)and(cycle%Kconfig.nsave==0)):
        list_of_files = ['{0}/back/iter{1}/{1}_{2}'.format(os.getcwd(),cycle,os.path.basename(Kconfig.md_input_file)),
                         '{0}/back/iter{1}/weight.w'.format(os.getcwd(),cycle)]

        cud = radical.pilot.ComputeUnitDescription()
        cud.cores = 1
        cud.mpi = False
        cud.executable = 'python'
        cud.pre_exec = ['ln %s/gro.py .'% paths[0] ,'ln %s/spliter.py .'% paths[0]]
        #cud.pre_exec = cud.pre_exec + ['cp %s/%s_%s .'%(paths[cycle-1],cycle,os.path.basename(Kconfig.md_input_file))]
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
        cud.pre_exec = ['ln %s/gro.py .'%paths[0],'ln %s/spliter.py .'% paths[0], 'ln %s/%s_%s .' %(paths[cycle-1],cycle,os.path.basename(Kconfig.md_input_file)),
                        'ln %s/weight.w .' %(paths[cycle-1])]

        cu = umgr.submit_units(cud)

        cu.wait()

        rem_path=saga.Url(cu.working_directory).path

        return [rem_path]
