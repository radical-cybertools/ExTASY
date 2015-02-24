__author__ = 'vivek'

import radical.pilot
import saga
import glob
import sys
import os

def Preprocessing(Kconfig,umgr,pilot):

    list_of_files = []

    print 'Preprocessing stage ....'
    sd_pilot = []

    curdir = os.path.dirname(os.path.realpath(__file__))
    MY_STAGING_AREA = 'staging:///'


    list_of_files = [    Kconfig.md_input_file,
                         Kconfig.mdp_file,
                         Kconfig.top_file,
                         Kconfig.lsdm_config_file,
                         '%s/gro.py'%curdir,
                         '%s/spliter.py'%curdir,
                         '%s/../../Simulator/Gromacs/run.py'%curdir,
                         '%s/../../Analyzer/LSDMap/pre_analyze.py'%curdir,
                         '%s/../../Analyzer/LSDMap/run_analyzer.sh'%curdir,
                         '%s/../../Analyzer/LSDMap/post_analyze.py'%curdir,
                         '%s/../../Analyzer/LSDMap/select.py'%curdir,
                         '%s/../../Analyzer/LSDMap/reweighting.py'%curdir,
                         ]

    if Kconfig.ndx_file is not None:
            list_of_files.append('%s' % Kconfig.ndx_file)

    if Kconfig.itp_file_loc is not None:
            for itpfile in glob.glob(Kconfig.itp_file_loc + '*.itp'):
                list_of_files.append('%s' % itpfile)

    for item in list_of_files:

        source = radical.pilot.Url()
        source.schema = 'file'
        source.path = item
        source = str(str)

        target = radical.pilot.Url()
        target.schema = 'staging'
        target.path = item
        target = str(target)

        dict = {
                    'source' : source,
                    'target' : target,
                    'action' : radical.pilot.TRANSFER
                }

        sd_pilot.append(dict)

    pilot.stage_in(sd_pilot)

    umgr.add_pilot(pilot)

    cud = radical.pilot.ComputeUnitDescription()
    cud.cores = 1
    cud.mpi = False
    cud.executable = 'python'
    cud.arguments = ['spliter.py',Kconfig.num_CUs,os.path.basename(Kconfig.md_input_file)]

    prep_stage = {
                    'source' : MY_STAGING_AREA + 'spliter.py',
                    'target' : 'spliter.py',
                    'action' : radical.pilot.LINK
    }

    md_stage = {
                    'source' : MY_STAGING_AREA + os.path.basename(Kconfig.md_input_file),
                    'target' : os.path.basename(Kconfig.md_input_file),
                    'action' : radical.pilot.LINK
    }

    cud.input_staging = [prep_stage,md_stage]

    cu = umgr.submit_units(cud)

    cu.wait()


