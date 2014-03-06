import urllib
import time
import sys
import os
import bigjobasync


def resource_cb(origin, old_state, new_state):
    """Resource callback function: writes resource allocation state 
    	changes to STDERR.
	
	    It aborts the script script with exit code '-1' if the resource 
	    allocation state is 'FAILED'.
	
	    (Obviously, more logic can be built into the callback function, for 
	    example fault tolerance.)
	    """ 
    msg = " * Resource '%s' state changed from '%s' to '%s'.\n" % \
      		(str(origin), old_state, new_state)
    sys.stderr.write(msg)

    if new_state == bigjobasync.FAILED:
        # Print the log and exit if big job has failed
        for entry in origin.log:
            print("   * LOG: %s" % entry)
        sys.stderr.write("   * EXITING.\n")
        sys.exit(-1)

# ----------------------------------------------------------------------------
#
def task_cb(origin, old_state, new_state):
    """Task callback function: writes task state changes to STDERR
    """
    msg = " * Task %s state changed from '%s' to '%s'.\n" % \
        (str(origin), old_state, new_state)
    sys.stderr.write(msg)
	
    if new_state == bigjobasync.FAILED:
        # Print the log entry if task has failed to run
        for entry in origin.log:
            print("     LOG: %s" % entry)


class simple:

    def __init__(self):
        return
		
    # ----------------------------------------------------------------------------
	
    def startResource(self,resource_info):
        self.resource_info = resource_info
        #API currently supports single pilot applications
        #print 'Start pilot service'
        self.remote_host = bigjobasync.Resource(
            name       = self.resource_info['resource_name'],
            resource   = bigjobasync.RESOURCES[self.resource_info['remote_host']],
        	username   = self.resource_info['username'],
        	runtime    = self.resource_info['walltime'],
       		cores      = self.resource_info['number_of_cores'],
       		workdir    = self.resource_info['remote_directory'],
        	project_id = self.resource_info['project_id']
       	)
        self.remote_host.register_callbacks(resource_cb)
        self.remote_host.allocate(terminate_on_empty_queue=True)
        print('Resource Allocation Done')
		
		
    def checkEnv(self):
        '''Run a simple job which returns the version of gromacs'''
        self.checker = bigjobasync.Task(
            name = "Env-Checker-job",
            cores = 1,
            executable = "/bin/bash",
            arguments = ["-l","-c",'"module load gromacs && pdb2gmx -version"'],
            output = [
                {
                    "mode"	: bigjobasync.COPY,
                    "origin_path"        : "STDOUT",
                    "destination"      : bigjobasync.LOCAL,
                    "destination_path" : "."
                }
            ]
        )
        self.checker.register_callbacks(task_cb)
        self.remote_host.schedule_tasks([self.checker])
        self.remote_host.wait()
        if self.checker.state is bigjobasync.FAILED:
            print("\nError: Could not run job to check environment")
        else:
            with open('STDOUT', 'r') as content_file:
                content = content_file.read()
                print(content)
                #remove the output file
                os.remove('STDOUT')
        return 0


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

        self.testjob = bigjobasync.Task(
            name = "test-job-sample-task",
            cores = 1,
            executable = "python",
            arguments = ['gromacs_python_wrapper.py','aladip.pdb','run.mdp','em.mdp','amber03','none'],
            input = [
                {
                    "mode" : bigjobasync.COPY,
                    "origin" : bigjobasync.LOCAL,
                    "origin_path" : "/%s/aladip.pdb" % os.getcwd(),
                },
                {
                    "mode" : bigjobasync.COPY,
                    "origin" : bigjobasync.LOCAL,
                    "origin_path" : "/%s/run.mdp" % os.getcwd(),
                },
                {
                    "mode" : bigjobasync.COPY,
                    "origin" : bigjobasync.LOCAL,
                    "origin_path" : "/%s/em.mdp" % os.getcwd(),
                },
                {
                    "mode" : bigjobasync.COPY,
                    "origin" : bigjobasync.LOCAL,
                    "origin_path" : "/%s/gromacs_python_wrapper.py" % os.getcwd(),
                },
            ],
            output = [
                {
                    "mode"	: bigjobasync.COPY,
                    "origin_path"        : "STDOUT",
                    "destination"      : bigjobasync.LOCAL,
                    "destination_path" : "STDOUT-test-job"
                },
                {
                    "mode"	: bigjobasync.COPY,
                    "origin_path"        : "STDERR",
                    "destination"      : bigjobasync.LOCAL,
                    "destination_path" : "STDERR-test-job"
                }
            ]
        )
        self.testjob.register_callbacks(task_cb)
        self.remote_host.schedule_tasks([self.testjob])
        self.remote_host.wait()

        if self.testjob.state is bigjobasync.FAILED:
            print("\nError: Could not run test job")
        else:
            with open('STDOUT-test-job', 'r') as stdout_file:
                content = stdout_file.read()
                print(content)
            with open('STDERR-test-job', 'r') as stderr_file:
                content = stderr_file.read()
                print(content)
                #remove the output file
                os.remove('STDOUT-test-job')
                os.remove('STDERR-test-job')

        return 0


    def startTasks(self,task_info):
        self.task_info=task_info
        print('Starting Tasks')
        self.all_tasks=[]
        #Aggregate all input files to transfer together
        inputfiles = os.listdir(self.task_info['source_directory'])
        input_to_data_transfer_task = []
        for f in inputfiles:
            temp = {
                "mode" : bigjobasync.COPY,
                "origin" : bigjobasync.LOCAL,
                "origin_path" : self.task_info['source_directory']+f,
            }
            input_to_data_transfer_task.append(temp)

        #Dummy task to transfer common files
        self.data_transfer_task = bigjobasync.Task(
            name = "data-staging-task",
            cores = 1,
            executable = "/bin/true",
            input = input_to_data_transfer_task,
        )
        self.data_transfer_task.register_callbacks(task_cb)
        self.all_tasks.append(self.data_transfer_task)

        self.remote_host.schedule_tasks(self.all_tasks)
        # Wait for the Resource allocation to finish
        self.remote_host.wait()

        self.all_tasks = []
        #Aggregate all input files to be linked with gromacs task
        input_to_gromacs_task = []
        for f in inputfiles:
            temp = {
                "mode" : bigjobasync.LINK,
                "origin_path" : f,
                "origin" : self.data_transfer_task,
            }
            input_to_gromacs_task.append(temp)

        for i in range(0,self.task_info['number_of_tasks']):
            self.gromacs_task = bigjobasync.Task(
                name        = "gromacs-task-%s" % i,
                cores       = self.task_info['cores_per_task'],
                executable  = self.task_info['kernel_type'],
                arguments   = [self.task_info['app_kernel']],
                input = input_to_gromacs_task,
                output = [
                            {
                                "mode"	: bigjobasync.COPY,
                                "origin_path"        : "STDOUT",
                                "destination"      : bigjobasync.LOCAL,
                                "destination_path" : self.task_info['output_directory']+'STDOUT-task-%s'%i
                            },
                            {
                                "mode"	: bigjobasync.COPY,
                                "origin_path"	: "STDERR",
                                "destination"      : bigjobasync.LOCAL,
                                "destination_path" : self.task_info['output_directory']+'STDERR-task-%s'%i
                            }
                        ]
                )
            self.gromacs_task.register_callbacks(task_cb)
            self.all_tasks.append(self.gromacs_task)

        # Submit all tasks to remote_host
        t1=time.time()
        self.remote_host.schedule_tasks(self.all_tasks)

        # Wait for the Resource allocation to finish
        self.remote_host.wait()
        print(self.remote_host.resource_name())
        t2 = time.time()
        print('All tasks completed')

        return (t2-t1)
		  		
