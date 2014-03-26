import urllib
import time
import sys
import os
import radical.pilot as sagapilot
import saga

#------------------------------------------------------------------------------
#
def pilot_state_cb(pilot, state):
    """pilot_state_change_cb() is a callback function. It gets called very
    time a ComputePilot changes its state.
    """
    print "[Callback]: ComputePilot '{0}' state changed to {1}.".format(
        pilot.uid, state)

    if state == sagapilot.states.FAILED:
        sys.exit(1)

#------------------------------------------------------------------------------
#
def unit_state_change_cb(unit, state):
    """unit_state_change_cb() is a callback function. It gets called very
    time a ComputeUnit changes its state.
    """
    print "[Callback]: ComputeUnit '{0}' state changed to {1}.".format(
        unit.uid, state)
    if state == sagapilot.states.FAILED:
        print "            Log: %s" % unit.log[-1]

#---------------------------------------------------------------------------------


class simple:

    def __init__(self,DBURL):
        # Create a new session. A session is the 'root' object for all other
        # SAGA-Pilot objects. It encapsualtes the MongoDB connection(s) as
        # well as security crendetials.

        if DBURL is None:
            print "ERROR: SAGAPILOT_DBURL (MongoDB server URL) is not defined."
            sys.exit(1)

        self.session = sagapilot.Session(database_url=DBURL)
        print "Session UID: {0} ".format(self.session.uid)

        # Add an ssh identity to the session.
        cred = sagapilot.SSHCredential()
        cred.user_id = "vivek91"
        self.session.add_credential(cred)
        return
		
    # ----------------------------------------------------------------------------
	
    def startResource(self,resource_info,RCONF):
        self.resource_info = resource_info

        # Add a Pilot Manager. Pilot managers manage one or more ComputePilots.
        self.pmgr = sagapilot.PilotManager(session=self.session, resource_configurations=RCONF)

        #pmgr.register_callback(pilot_state_cb)

        # Start a pilot at the remote host as per the configs
        pdesc = sagapilot.ComputePilotDescription()
        pdesc.resource = self.resource_info['remote_host']
        pdesc.runtime = self.resource_info['walltime']
        pdesc.cores = self.resource_info['number_of_cores']
        pdesc.sandbox = self.resource_info['remote_directory']


        # Launch the pilot.
        pilot = self.pmgr.submit_pilots(pdesc)

        #
        print "Pilot UID       : {0} ".format(pilot.uid )


        self.umgr = sagapilot.UnitManager(session=self.session,scheduler=sagapilot.SCHED_DIRECT_SUBMISSION)
        # Register our callback with the UnitManager. This callback will get
        # called every time any of the units managed by the UnitManager
        # change their state.
        self.umgr.register_callback(unit_state_change_cb)

        # Add the previsouly created ComputePilot to the UnitManager.
        self.umgr.add_pilots(pilot)
        print('Resource Allocation Done')
		
		
    def checkEnv(self):
        '''Run a simple job which returns the version of gromacs'''

        compute_units = []
        cu = sagapilot.ComputeUnitDescription()
        cu.executable = "/bin/bash"
        cu.arguments = ["-l","-c",'"module load gromacs && pdb2gmx -version"']
        cu.cores = 1

        compute_units.append(cu)

        # Submit the previously created ComputeUnit descriptions to the
        # PilotManager. This will trigger the selected scheduler to start
        # assigning ComputeUnits to the ComputePilots.
        self.umgr.submit_units(compute_units)
        # Wait for all compute units to finish.
        self.umgr.wait_units()

        for unit in self.umgr.get_units():
            # Get the stdout and stderr streams of the ComputeUnit.
            print "  STDOUT: {0}".format(unit.stdout)
            print "  STDERR: {0}".format(unit.stderr)

        # Cancel all pilots.
        self.pmgr.cancel_pilots()

        # Remove session from database
        self.session.destroy()



    def startTestJob(self):
        '''Run a simple job which executes a sample gromacs task'''

        inpfiles = {
            "aladip.pdb" : "http://repex2.tacc.utexas.edu/cybertools/sampledata/gromacs/aladip.pdb",
            "run.mdp" : "http://repex2.tacc.utexas.edu/cybertools/sampledata/gromacs/run.mdp",
            "em.mdp" : "http://repex2.tacc.utexas.edu/cybertools/sampledata/gromacs/em.mdp",
            "gromacs_python_wrapper.py" : "http://repex2.tacc.utexas.edu/cybertools/sampledata/gromacs/gromacs_python_wrapper.py",
            }

        try:
            for key, val in inpfiles.iteritems():
                print(" * Downloading sample input data %s" % val)
                urllib.urlretrieve(val, key)
        except Exception as ex:
            print("ERROR - Couldn't download sample data: %s" % str(ex))
            return 1

        compute_units = []
        cu = sagapilot.ComputeUnitDescription()
        cu.executable = "python"
        cu.arguments = ['gromacs_python_wrapper.py','aladip.pdb','run.mdp','em.mdp','amber03','none']
        cu.cores = 1
        cu.input_data = ["/%s/aladip.pdb" % os.getcwd(), "/%s/em.mdp" % os.getcwd(),"/%s/run.mdp" % os.getcwd(),"/%s/gromacs_python_wrapper.py" % os.getcwd()]

        compute_units.append(cu)

        self.umgr.submit_units(compute_units)

        # Wait for all compute units to finish.
        self.umgr.wait_units()

        for unit in self.umgr.get_units():
            # Get the stdout and stderr streams of the ComputeUnit.
            print "  STDOUT: {0}".format(unit.stdout)
            print "  STDERR: {0}".format(unit.stderr)

        # Cancel all pilots.
        self.pmgr.cancel_pilots()

        # Remove session from database
        self.session.destroy()

        return 0


    def startTasks(self,task_info):

        self.task_info=task_info
        print('Starting Tasks')

        #Aggregate all input filenames into list
        inputfiles = os.listdir(self.task_info['source_directory'])
        input_to_data_transfer_task = []
        for f in inputfiles:
            temp = '%s/%s' % (self.task_info['source_directory'],f)
            input_to_data_transfer_task.append(temp)

        #SHARED INPUT TASK
        data_transfer_task = sagapilot.ComputeUnitDescription()
        data_transfer_task.executable = "/bin/true"
        data_transfer_task.cores = 1
        data_transfer_task.input_data = input_to_data_transfer_task

        units = self.umgr.submit_units(data_transfer_task)

        # Wait for data transfer task to finish.
        self.umgr.wait_units()

        #get the path of the shared data directory
        shared_input_url = saga.Url(units.working_directory).path

        gromacs_tasks = []

        for i in range(0,self.task_info['number_of_tasks']):
            gromacs_task = sagapilot.ComputeUnitDescription()
            gromacs_task.executable = "python"
            gromacs_task.arguments = ["linker.py %s %s"%(shared_input_url,self.task_info['kernel_name'])]
            gromacs_task.input_data = ['linker.py']
            gromacs_task.cores = self.task_info['cores_per_task']

            gromacs_tasks.append(gromacs_task)

        units = self.umgr.submit_units(gromacs_tasks)

        # Wait for all compute units to finish.
        self.umgr.wait_units()

        # Cancel all pilots.
        self.pmgr.cancel_pilots()

        # Remove session from database
        self.session.destroy()

        return 0
