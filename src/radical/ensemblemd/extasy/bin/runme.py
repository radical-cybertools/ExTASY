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

    # Mitigate the erroneous management of the pilot state from the RP
    # back-end. In some conditions, the callback is called when the state of
    # the pilot is not available even if it should be.
    if pilot:

        print "[Callback]: ComputePilot '{0}' state changed to {1}.".format(
            pilot.uid, state)

        if state == radical.pilot.states.FAILED:
            print "#######################"
            print "##       ERROR       ##"
            print "#######################"
            print "Pilot {0} has FAILED. Can't recover.".format(pilot.uid)
            print "Pilot log:- "
            for log in pilot.log:
                print log.as_dict()
            print 'Pilot STDOUT : {0}'.format(pilot.stdout)
            print 'Pilot STDERR : {0}'.format(pilot.stderr)
            sys.exit(1)

#------------------------------------------------------------------------------
#
def unit_state_change_cb(unit, state):
    """unit_state_change_cb() is a callback function. It gets called very
    time a ComputeUnit changes its state.
    """

    if unit:
        print "[Callback]: ComputeUnit '{0}' state changed to {1}.".format(
            unit.uid, state)

        if state == radical.pilot.states.FAILED:
            print "#######################"
            print "##       ERROR       ##"
            print "#######################"
            print "ComputeUnit {0} has FAILED. Can't recover.".format(unit.uid)
            print "ComputeUnit log:- "
            for log in unit.log:
                print log.as_dict()
            print u"STDERR : {0}".format(unit.stderr)
            print u"STDOUT : {0}".format(unit.stdout)
            sys.exit(1)

        elif state == radical.pilot.states.CANCELED:
            print "#######################"
            print "##       ERROR       ##"
            print "#######################"
            print "ComputeUnit {0} was canceled prematurely because the pilot was terminated. Can't recover.".format(unit.uid)
            sys.exit(1)

    else:
        return


#---------------------------------------------------------------------------------

def check_config_vals(Kconfig,RPconfig):

    if Kconfig.num_cores_per_sim_cu > RPconfig.PILOTSIZE:
        print '#####################'
        print 'Error : Cores allocated to each CU greater than the Pilotsize .. Please check the config files'
        print '#####################'
        sys.exit(1)

    # Base case - start from 0 !
    if (Kconfig.start_iter==0):
        if (os.path.isdir('%s/backup' % os.getcwd())) is True:
            shutil.rmtree('%s/backup' % os.getcwd())
        os.mkdir('%s/backup'%os.getcwd())
        restart = False


    # Restart case - test if iter? folder exists
    elif ((Kconfig.start_iter!=0) and ( not (os.path.isdir('{0}/backup/iter{1}'.format(os.getcwd(),Kconfig.start_iter-1))))) is True:
        print 'Backups not found .. You need to have a backup/iter{0} folder ..'.format(Kconfig.start_iter - 1)
        print 'Exiting ...'
        exit(0)

    # Restart case - valid
    else:
        restart = True

    return restart

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
    # umgr.add_pilots(pilot)

    return umgr,session,pilot


def main():

    session = None
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

    try:

        #Version printing

        import radical.ensemblemd.extasy as extasy
        print 'ExTASY version : ',extasy.version

        RPconfig = imp.load_source('RPconfig', args.RPconfig)
        Kconfig = imp.load_source('Kconfig', args.Kconfig)

        restart = check_config_vals(Kconfig,RPconfig)

        Load_Preprocessor = Kconfig.simulator

        if ( Load_Preprocessor == 'Gromacs'):
            from Preprocessor.Gromacs.preprocessor import Preprocessing

        if (Load_Preprocessor == 'Amber'):
            from Preprocessor.Amber.preprocessor import Preprocessing

        umgr, session, pilot = startPilot(Kconfig,RPconfig)

        if ( Kconfig.simulator == 'Amber'):
            from Simulator.Amber.simulator import Simulator
        if ( Kconfig.analyzer == 'CoCo'):
            from Analyzer.CoCo.analyzer import Analyzer

        if ( Kconfig.simulator == 'Gromacs'):
            from Simulator.Gromacs.simulator import Simulator
        if ( Kconfig.analyzer == 'LSDMap'):
            from Analyzer.LSDMap.analyzer import Analyzer

        Preprocessing(Kconfig, umgr,pilot,restart)


        for i in range(Kconfig.start_iter,Kconfig.start_iter + Kconfig.num_iterations):
            print 'Cycle : %s'%i

            if (Kconfig.simulator == 'Gromacs' and Kconfig.analyzer == 'LSDMap'):
                Simulator(umgr, RPconfig, Kconfig, i)
                Analyzer(umgr, RPconfig, Kconfig, i)
            elif (Kconfig.simulator == 'Amber' and Kconfig.analyzer == 'CoCo'):
                Analyzer(umgr, RPconfig, Kconfig, i)
                Simulator(umgr, RPconfig, Kconfig, i)

    except Exception as e:
        print "An error occurred: %s" % ((str(e)))
        sys.exit(-1)
    except KeyboardInterrupt:
        print "Execution was interrupted"
        sys.exit(-1)
    finally:
        if session is not None:
            print "Closing session, exiting now ..."
            if os.getenv("EXTASY_DEBUG") is not None:
                session.close(cleanup=False)
            else:
                session.close(cleanup=True)
        else:
            print 'Exception triggered, no session created, exiting now...'
            sys.exit(-1)

        #cleanup downloaded lsdm file
        try:
            os.remove('%s/lsdm.py'%os.getcwd())
        except:
            pass

if __name__ == '__main__':
    main()
