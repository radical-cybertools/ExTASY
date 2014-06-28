import os
import sys
import radical.pilot

""" DESCRIPTION: Tutorial 1: A Simple Workload consisting of a Bag-of-Tasks
"""

# DBURL defines the MongoDB server URL and has the format mongodb://host:port.
# For the installation of a MongoDB server, refer to http://docs.mongodb.org.
DBURL = os.getenv("RADICAL_PILOT_DBURL")
if DBURL is None:
    print "ERROR: RADICAL_PILOT_DBURL (MongoDB server URL) is not defined."
    sys.exit(1)

#------------------------------------------------------------------------------
#
def pilot_state_cb(pilot, state):
    """pilot_state_change_cb() is a callback function. It gets called very
    time a ComputePilot changes its state.
    """
    print "[Callback]: ComputePilot '{0}' state changed to {1}.".format(pilot.uid, state)

    if state == radical.pilot.states.FAILED:
        sys.exit(1)



#------------------------------------------------------------------------------
#
def unit_state_change_cb(unit, state):
    """unit_state_change_cb() is a callback function. It gets called very
    time a ComputeUnit changes its state.
    """
    print "[Callback]: ComputeUnit '{0}' state changed to {1}.".format(unit.uid, state)
    if state == radical.pilot.states.FAILED:
        print "            Log: %s" % unit.log[-1]


#----------------------------------------------------------------------------
#
def main():

    try:
        # Create a new session. A session is the 'root' object for all other
        # RADICAL-Pilot objects. It encapsulates the MongoDB connection(s) as
        # well as security credentials.
        session = radical.pilot.Session(database_url=DBURL)

        # Add an ssh identity to the session.
        cred = radical.pilot.SSHCredential()
        cred.user_id = 'vivek91'
        session.add_credential(cred)

        # Add a Pilot Manager. Pilot managers manage one or more ComputePilots.
        print "Initializing Pilot Manager ..."
        pmgr = radical.pilot.PilotManager(session=session)

        # Register our callback with the PilotManager. This callback will get
        # called every time any of the pilots managed by the PilotManager
        # change their state.
        pmgr.register_callback(pilot_state_cb)

        # this describes the parameters and requirements for our pilot job
        pdesc = radical.pilot.ComputePilotDescription ()
        pdesc.resource = "stampede.tacc.utexas.edu" # NOTE: This is a "label", not a hostname
        pdesc.runtime  = 5 # minutes
        pdesc.cores    = 1
        #pdesc.cleanup  = True

        # submit the pilot.
        print "Submitting Compute Pilot to Pilot Manager ..."
        pilot = pmgr.submit_pilots(pdesc)

        # Combine the ComputePilot, the ComputeUnits and a scheduler via
        # a UnitManager object.
        print "Initializing Unit Manager ..."
        umgr = radical.pilot.UnitManager(
            session=session,
            scheduler=radical.pilot.SCHED_DIRECT_SUBMISSION)

        # Register our callback with the UnitManager. This callback will get
        # called every time any of the units managed by the UnitManager
        # change their state.
        umgr.register_callback(unit_state_change_cb)

        # Add the created ComputePilot to the UnitManager.
        print "Registering Compute Pilot with Unit Manager ..."
        umgr.add_pilots(pilot)

        NUMBER_JOBS  = 1 # the total number of cus to run

        # submit CUs to pilot job
        cudesc_list = []
        for i in range(NUMBER_JOBS):

            # -------- BEGIN USER DEFINED CU DESCRIPTION --------- #
            cudesc = radical.pilot.ComputeUnitDescription()
	    cudesc.pre_exec    = ["module load TACC","module load Linux","module load intel/14.0.1.106","module load python/2.7.6"
					,"git clone https://github.com/jp43/lsdmap.git","export PATH=$PATH:$PWD/lsdmap/bin",
					"chmod +x lsdmap/bin/lsdmap"
]
            #cudesc.environment = {'INPUT1': 'test.sh','INPUT2':'hello'}
            cudesc.executable  = "lsdmap"
            cudesc.arguments   = ['-f','lsdmap/examples/lsdmap/config.ini' ,'-c', 'lsdmap/examples/lsdmap/aladip_1000.gro']
            cudesc.cores       = 1
	    #cudesc.input_data  = ['test.sh']
	    #cudesc.mpi	       = False
            # -------- END USER DEFINED CU DESCRIPTION --------- #

            cudesc_list.append(cudesc)

        # Submit the previously created ComputeUnit descriptions to the
        # PilotManager. This will trigger the selected scheduler to start
        # assigning ComputeUnits to the ComputePilots.
        print "Submit Compute Units to Unit Manager ..."
        cu_set = umgr.submit_units (cudesc_list)

        print "Waiting for CUs to complete ..."
        umgr.wait_units()
        print "All CUs completed successfully!"

        session.close()
        print "Closed session, exiting now ..."

    except Exception as e:
            print "AN ERROR OCCURRED: %s" % ((str(e)))
            return(-1)


#------------------------------------------------------------------------------
#
if __name__ == "__main__":

    sys.exit(main())

#
#------------------------------------------------------------------------------
