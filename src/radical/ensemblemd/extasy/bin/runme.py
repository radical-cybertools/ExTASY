__author__ = 'vivek'

import radical.pilot
import argparse
import imp
#from config.kernel_config import *      #change this to command line
#from config.RP_config import *          #change this too
import os
import sys
import time


#------------------------------------------------------------------------------
#
def pilot_state_cb(pilot, state):
    """pilot_state_change_cb() is a callback function. It gets called very
    time a ComputePilot changes its state.
    """
    print "[Callback]: ComputePilot '{0}' state changed to {1}.".format(
        pilot.uid, state)

    if state == radical.pilot.states.FAILED:
        sys.exit(1)

#------------------------------------------------------------------------------
#
def unit_state_change_cb(unit, state):
    """unit_state_change_cb() is a callback function. It gets called very
    time a ComputeUnit changes its state.
    """
    print "[Callback]: ComputeUnit '{0}' state changed to {1}.".format(
        unit.uid, state)
    if state == radical.pilot.states.FAILED:
        print "            Log: %s" % unit.log[-1]

#---------------------------------------------------------------------------------

def startPilot(Kconfig_url,RPconfig_url):

    RPconfig = imp.load_source('RPconfig',RPconfig_url)
    Kconfig = imp.load_source('Kconfig',Kconfig_url)

    from RPconfig import *
    from Kconfig import *

    session = radical.pilot.Session(database_url=DBURL)
    print "Session UID: {0} ".format(session.uid)

    # Add an ssh identity to the session.
    cred = radical.pilot.Context('ssh')
    cred.user_id = UNAME
    session.add_context(cred)

    # Add a Pilot Manager. Pilot managers manage one or more ComputePilots.
    pmgr = radical.pilot.PilotManager(session=session)

    pmgr.register_callback(pilot_state_cb)

    # Start a pilot at the remote host as per the configs
    pdesc = radical.pilot.ComputePilotDescription()
    pdesc.resource = REMOTE_HOST
    pdesc.runtime = WALLTIME
    pdesc.cores = PILOTSIZE
    pdesc.workdir = WORKDIR
    pdesc.queue = QUEUE
    pdesc.project = ALLOCATION


    # Launch the pilot.
    pilot = pmgr.submit_pilots(pdesc)

    print "Pilot UID       : {0} ".format(pilot.uid )


    umgr = radical.pilot.UnitManager(session=session, scheduler=radical.pilot.SCHED_DIRECT_SUBMISSION)
    # Register our callback with the UnitManager. This callback will get
    # called every time any of the units managed by the UnitManager
    # change their state.
    umgr.register_callback(unit_state_change_cb)

    # Add the previously created ComputePilot to the UnitManager.
    umgr.add_pilots(pilot)

    return umgr,session



def main():

    usage = 'usage: %prog --RPconfig --Kconfig'

    parser = argparse.ArgumentParser()
    parser.add_argument('--RPconfig', help='link to Radical Pilot related configurations file')
    parser.add_argument('--Kconfig', help='link to Kernel configurations file')

    args = parser.parse_args()

    if args.RPconfig is None:
        parser.error('Please enter a RP configuration file')
        sys.exit(1)
    if args.Kconfig is None:
        parser.error('Please enter a Kernel configuration file')
        sys.exit(0)

    RPconfig = imp.load_source('RPconfig', args.RPconfig)
    Kconfig = imp.load_source('Kconfig', args.Kconfig)

    from RPconfig import *
    from Kconfig import *

    Load_Preprocessor = Load_Simulator

    if ( Load_Preprocessor == 'Gromacs'):
        from Preprocessor.Gromacs.preprocessor import Preprocessing

    if (Load_Preprocessor == 'Amber'):
        from Preprocessor.Amber.preprocessor import Preprocessing



    umgr,session=startPilot(args.Kconfig,args.RPconfig)

    Preprocessing(args.Kconfig,umgr)


    if ( Load_Simulator == 'Amber'):
        from Simulator.Amber.simulator import Simulator
    if ( Load_Analyzer == 'CoCo'):
        from Analyzer.CoCo.analyzer import Analyzer

    if ( Load_Simulator == 'Gromacs'):
        from Simulator.Gromacs.simulator import Simulator
    if ( Load_Analyzer == 'LSDMap'):
        from Analyzer.LSDMap.analyzer import Analyzer

    for i in range(0,num_iterations):
        if Load_Simulator:
            p1=time.time()
            print 'Starting Simulation'
            Simulator(umgr,args.RPconfig,args.Kconfig,i)
        if Load_Analyzer:
            print 'Starting Analysis'
            Analyzer(umgr,args.RPconfig,args.Kconfig,i)
            p2=time.time()
        if p1.is_integer() and p2.is_integer():
            print 'TTC for one iteration : ', p2-p1

    session.close()

if __name__ == '__main__':
    main()
