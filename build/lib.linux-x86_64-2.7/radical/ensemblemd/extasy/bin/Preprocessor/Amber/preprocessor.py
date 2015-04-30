__author__ = 'vivek'

import radical.pilot
import os
import sys

def Preprocessing(Kconfig,umgr,pilot,restart):

    print 'Preprocessing stage ....'

    MY_STAGING_AREA = 'staging:///'
    sd_pilot = []

    curdir = os.path.dirname(os.path.realpath(__file__))

    list_of_files = [Kconfig.md_input_file,
                     Kconfig.minimization_input_file,
                     Kconfig.top_file,
                     '%s/../../Analyzer/CoCo/postexec.py'%curdir
                      ]

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

    # Transfer the crd file for the first iteration
    if restart == False:
        dict = {
                'source': 'file://%s/%s'%(os.getcwd(),os.path.basename(Kconfig.initial_crd_file)),
                'target': '%siter0/%s'%(MY_STAGING_AREA,os.path.basename(Kconfig.initial_crd_file)),
                'action': radical.pilot.TRANSFER
            }
        sd_pilot.append(dict)


    # Transfer all the ncdf files from all iterations
    else:

        print 'Expecting {0} ncdf files in backup/iter{1} folder'.format(Kconfig.start_iter*Kconfig.num_CUs,Kconfig.start_iter-1)
        if (len(os.listdir('backup/iter{0}'.format(Kconfig.start_iter-1))) == (Kconfig.start_iter*Kconfig.num_CUs + 1)):
            print 'Expected number of files found ...'
        else:
            print 'Expected number of files not found ... Exiting restart ...'
            sys.exit(0)

        for iter in range(0,Kconfig.start_iter):
            for inst in range(0,Kconfig.num_CUs):
                dict = {
                        'source': 'file://{3}/backup/iter{0}/md_{1}_{2}.ncdf'.format(Kconfig.start_iter-1,iter,inst,os.getcwd()),
                        'target': '{0}iter{1}/md_{1}_{2}.ncdf'.format(MY_STAGING_AREA,iter,inst),
                        'action': radical.pilot.TRANSFER
                }
                sd_pilot.append(dict)

    pilot.stage_in(sd_pilot)

    umgr.add_pilots(pilot)
