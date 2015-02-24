__author__ = 'vivek'

import radical.pilot
import os

def Preprocessing(Kconfig,umgr,pilot):

    print 'Preprocessing stage ....'

    MY_STAGING_AREA = 'staging:///'
    sd_pilot = []

    curdir = os.path.dirname(os.path.realpath(__file__))

    list_of_files = [Kconfig.initial_crd_file,
                     Kconfig.md_input_file,
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

    pilot.stage_in(sd_pilot)

    umgr.add_pilots(pilot)
