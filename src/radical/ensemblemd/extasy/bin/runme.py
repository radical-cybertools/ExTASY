__author__ = 'vivek'

import radical.pilot
import argparse
import imp
import os
import sys
import time
import shutil


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

def startPilot(Kconfig,RPconfig):

    session = radical.pilot.Session(database_url=RPconfig.DBURL)
    print "Session UID: {0} ".format(session.uid)

    # Add an ssh identity to the session.
    cred = radical.pilot.Context('ssh')
    cred.user_id = RPconfig.UNAME
    session.add_context(cred)

    # Add a Pilot Manager. Pilot managers manage one or more ComputePilots.
    pmgr = radical.pilot.PilotManager(session=session)

    pmgr.register_callback(pilot_state_cb)

    # Start a pilot at the remote host as per the configs
    pdesc = radical.pilot.ComputePilotDescription()
    pdesc.resource = RPconfig.REMOTE_HOST
    pdesc.runtime = RPconfig.WALLTIME
    pdesc.cores = RPconfig.PILOTSIZE
    if RPconfig.WORKDIR is not None:
        pdesc.sandbox = RPconfig.WORKDIR
    pdesc.queue = RPconfig.QUEUE
    pdesc.project = RPconfig.ALLOCATION


    # Launch the pilot.
    pilot = pmgr.submit_pilots(pdesc)

    print "Pilot UID       : {0} ".format(pilot.uid)


    umgr = radical.pilot.UnitManager(session=session, scheduler=radical.pilot.SCHED_DIRECT_SUBMISSION)
    # Register our callback with the UnitManager. This callback will get
    # called every time any of the units managed by the UnitManager
    # change their state.
    umgr.register_callback(unit_state_change_cb)

    # Add the previously created ComputePilot to the UnitManager.
    umgr.add_pilots(pilot)

    return umgr,session



def main():

    usage = 'usage: %prog --RPconfig RPCONFIG --Kconfig KCONFIG'

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


    Load_Preprocessor = Kconfig.simulator

    if ( Load_Preprocessor == 'Gromacs'):
        from Preprocessor.Gromacs.preprocessor import Preprocessing

    if (Load_Preprocessor == 'Amber'):
        from Preprocessor.Amber.preprocessor import Preprocessing



    umgr,session=startPilot(Kconfig,RPconfig)


    if ( Kconfig.simulator == 'Amber'):
        from Simulator.Amber.simulator import Simulator
    if ( Kconfig.analyzer == 'CoCo'):
        from Analyzer.CoCo.analyzer import Analyzer

    if ( Kconfig.simulator == 'Gromacs'):
        from Simulator.Gromacs.simulator import Simulator
    if ( Kconfig.analyzer == 'LSDMap'):
        from Analyzer.LSDMap.analyzer import Analyzer

    for i in range(Kconfig.start_iter,Kconfig.num_iterations):
        Preprocessing(Kconfig,umgr,i)
        if Kconfig.simulator:
            p1=time.time()
            Simulator(umgr,RPconfig,Kconfig,i)
        if Kconfig.analyzer:
            Analyzer(umgr,RPconfig,Kconfig,i)
            p2=time.time()
        if p1.is_integer() and p2.is_integer():
            print 'TTC for one iteration : ', p2-p1
        if (Kconfig.simulator == 'Gromacs'):
            if((i+1)%Kconfig.nsave == 0):
                if os.path.isdir('%s/backup' % os.getcwd()) is False:
                    os.mkdir('%s/backup' % os.getcwd())
                os.mkdir('%s/backup/iter%s/'%(os.getcwd(),i+1))
                shutil.copy('%s_%s'%(i+1,os.path.basename(Kconfig.md_input_file)),'%s/backup/iter%s/%s'%(os.getcwd(),i+1,os.path.basename(Kconfig.md_input_file)))
                shutil.copy(Kconfig.w_file,'%s/backup/iter%s/%s'%(os.getcwd(),i+1,os.path.basename(Kconfig.w_file)))
                shutil.copy('lsdmap.log','%s/backup/iter%s/lsdmap.log'%(os.getcwd(),i+1))

    if os.getenv("EXTASY_DEBUG") is not None:
        session.close(delete=False)
    else:
        session.close(delete=True)

if __name__ == '__main__':
    main()
