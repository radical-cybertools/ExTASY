__author__ = 'vivek'

import radical.pilot
import urllib
import saga
import glob
import sys
import os

def Preprocessing(Kconfig,umgr,pilot,restart):

    list_of_files = []

    print 'Preprocessing stage ....'
    sd_pilot = []

    curdir = os.path.dirname(os.path.realpath(__file__))
    MY_STAGING_AREA = 'staging:///'


    #Download the latest lsdm.py file
    lsdm_file = urllib.URLopener()
    lsdm_file.retrieve("http://sourceforge.net/p/lsdmap/git/ci/extasy-0.1-rc2/tree/lsdmap/lsdm.py?format=raw","%s/lsdm.py"%os.getcwd())


    list_of_files = [    Kconfig.mdp_file,
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
                         '%s/lsdm.py'%os.getcwd()
                         ]
                         
    if restart == False:
        list_of_files.append(Kconfig.md_input_file)

    if Kconfig.ndx_file is not None:
            list_of_files.append('%s' % Kconfig.ndx_file)

    if Kconfig.itp_file_loc is not None:
            for itpfile in glob.glob(Kconfig.itp_file_loc + '*.itp'):
                list_of_files.append('%s' % itpfile)

    for item in list_of_files:
        if item.startswith('.'):
            dict = {
                'source': 'file://%s/%s'%(os.getcwd(),os.path.basename(item)),
                'target': "%s%s" % (MY_STAGING_AREA,os.path.basename(item)),
                'action': radical.pilot.TRANSFER
                }
        else:
            dict = {
                'source': 'file://%s'%(item),
                'target': "%s%s" % (MY_STAGING_AREA,os.path.basename(item)),
                'action': radical.pilot.TRANSFER
                }
        sd_pilot.append(dict)

    if restart == True:
        cycle=Kconfig.start_iter-1
        more_files = [os.getcwd() + '/backup/iter{0}/{1}_input.gro'.format(cycle,cycle+1),
                      os.getcwd() + '/backup/iter{0}/weight.w'.format(cycle)]
        for item in more_files:
            dict = {
                        'source': 'file://%s'%(item),
                        'target': '{0}iter{1}/{2}'.format(MY_STAGING_AREA,cycle,os.path.basename(item)),
                        'action': radical.pilot.TRANSFER
            }
            sd_pilot.append(dict)

    pilot.stage_in(sd_pilot)

    umgr.add_pilots(pilot)

    # CUD when restart is False.
    if restart ==  False:

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

        cud.output_staging = []
        for i in range(0,Kconfig.num_CUs):
            temp = {
                    'source': 'temp/start{0}.gro'.format(i),
                    'target': MY_STAGING_AREA + 'iter0/start{0}.gro'.format(i),
                    'action': radical.pilot.LINK
            }
            cud.output_staging.append(temp)

        cud.input_staging = [prep_stage,md_stage]

        cu = umgr.submit_units(cud)

        cu.wait()


    #CUD when restart is True
    else:

        cud = radical.pilot.ComputeUnitDescription()
        cud.cores = 1
        cud.mpi = False
        cud.executable = 'python'
        cud.arguments = ['spliter.py',Kconfig.num_CUs,'{0}_input.gro'.format(Kconfig.start_iter)]

        prep_stage = {
                    'source' : MY_STAGING_AREA + 'spliter.py',
                    'target' : 'spliter.py',
                    'action' : radical.pilot.LINK
        }

        md_stage = {
                    'source' : MY_STAGING_AREA + 'iter{0}/{1}_input.gro'.format(Kconfig.start_iter-1,Kconfig.start_iter),
                    'target' : '{0}_input.gro'.format(Kconfig.start_iter),
                    'action' : radical.pilot.LINK
        }

        cud.output_staging = []
        for i in range(0,Kconfig.num_CUs):
            temp = {
                    'source': 'temp/start{0}.gro'.format(i),
                    'target': MY_STAGING_AREA + 'iter{1}/start{0}.gro'.format(i,Kconfig.start_iter),
                    'action': radical.pilot.LINK
            }
            cud.output_staging.append(temp)

        cud.input_staging = [prep_stage,md_stage]

        cu = umgr.submit_units(cud)

        cu.wait()



