__author__ = 'vivek'

import radical.pilot
#import imp
from config.parameters import *
from Analyzer.LSDMap.analyzer import Analyzer
from Preprocessor.Gromacs.preprocessor import Preprocessing
from Simulator.Gromacs.simulator import Simulator
from config.config_file import *

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

def startPilot():

    session = radical.pilot.Session(database_url=DBURL)
    print "Session UID: {0} ".format(session.uid)

    # Add an ssh identity to the session.
    cred = radical.pilot.SSHCredential()
    cred.user_id = UNAME
    session.add_credential(cred)

    # Add a Pilot Manager. Pilot managers manage one or more ComputePilots.
    pmgr = radical.pilot.PilotManager(session=session)

    pmgr.register_callback(pilot_state_cb)

    # Start a pilot at the remote host as per the configs
    pdesc = radical.pilot.ComputePilotDescription()
    pdesc.resource = REMOTE_HOST
    pdesc.runtime = WALLTIME
    pdesc.cores = PILOTSIZE


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

    return umgr



if __name__ == '__main__':


    #Preprocessor=imp.load_source('Preprocessor','file:///home/vivek/Research/thesis/Preprocessor/%s/preprocessor.py' % UPreprocessor)
    #from Preprocessor import Preprocessing

    #Sim=imp.load_source('Sim','file:///home/vivek/Research/thesis/Simulator/%s/simulator.py' % USimulator)
    #from Sim import Simulator

    #Analyze=imp.load_source('Analyze','file:///home/vivek/Research/thesis/Analyzer/%s/analyzer.py' % UAnalyzer)
    #from Analyze import Analyzer
    Preprocessing()

    umgr=startPilot()

    for i in range(0,num_iterations):
        print 'Starting Simulation'
        Simulator(umgr)
        if UAnalyzer:
            print 'Starting Analysis'
            Analyzer(umgr)


