.. _develop:

*************
Customization
*************

Writing New Application Kernels
-------------------------------

While the current set of available application kernels might provide a good set of tools to start, sooner or later you will probably want to use a tool for which no application Kernel exists. In this case, you will have to write your own one.

The easiest way to describe how this works is by example:

.. code::

	from radical.ensemblemd import Kernel
	from radical.ensemblemd import Pipeline
	from radical.ensemblemd import EnsemblemdError
	from radical.ensemblemd import SingleClusterEnvironment

	from radical.ensemblemd.engine import get_engine
	from radical.ensemblemd.kernel_plugins.kernel_base import KernelBase


	# ------------------------------------------------------------------------------
	#
	_KERNEL_INFO = {
	    "name":         "my.user.defined.kernel",
	    "description":  "Brief description of your Kernel.",
	    "arguments":   {
        	"--sleep-interval=": {
            "mandatory": True,
	            "description": "Number of seconds to do nothing."
    	    },	
    	}
	}

	# ------------------------------------------------------------------------------
	#
	class MyUserDefinedKernel(KernelBase):

    	def __init__(self):
	        """Le constructor.
        	"""
        	super(MyUserDefinedKernel, self).__init__(_KERNEL_INFO)

    	@staticmethod
    	def get_name():
	        return _KERNEL_INFO["name"]

    	def _bind_to_resource(self, resource_key):
	        """This function binds the Kernel to a specific resource defined in
           	"resource_key".
        	"""
        	executable = "/bin/sleep"
        	arguments  = ['{0}'.format(self.get_arg("--sleep-interval="))]

        	self._executable  = executable
        	self._arguments   = arguments
        	self._environment = None
        	self._uses_mpi    = False
        	self._pre_exec    = None
        	self._post_exec   = None

	# ------------------------------------------------------------------------------
	# Register the user-defined kernel with Ensemble MD Toolkit.
	get_engine().add_kernel_plugin(MyUserDefinedKernel)

	# ------------------------------------------------------------------------------
	#
	class Sleep(Pipeline):
	    """The Sleep class implements a Bag of Task. All ensemble members
       	simply sleep for 60 seconds.
    	"""

    	def __init__(self, instances):
	        Pipeline.__init__(self, instances)

    	def step_1(self, instance):
	        """This step sleeps for 60 seconds.
        	"""
        	k = Kernel(name="my.user.defined.kernel")
        	k.arguments = ["--sleep-interval=60"]
        	return k

	# ------------------------------------------------------------------------------
	#
	if __name__ == "__main__":

	    try:
        	# Create a new static execution context with one resource and a fixed
        	# number of cores and runtime.
        	cluster = SingleClusterEnvironment(
	            resource="localhost",
            	cores=1,
            	walltime=15,
            	username=None,
            	allocation=None
        	)

        	# Allocate the resources.
        	cluster.allocate()

        	# Set the 'instances' of the pipeline to 16. This means that 16 instances
        	# of each pipeline step are executed.
        	#
        	# Execution of the 16 pipeline instances can happen concurrently or
        	# sequentially, depending on the resources (cores) available in the
        	# SingleClusterEnvironment.
        	sleep = Sleep(instances=16)

        	cluster.run(sleep)

    	except EnsemblemdError, er:

	        print "Ensemble MD Toolkit Error: {0}".format(str(er))
	        raise # Just raise the execption again to get the backtrace

The existing kernels can be found `here <misc.html>`_


Writing a Custom Resource Configuration File
--------------------------------------------

If you want to use RADICAL-Pilot with a resource that is not in any of the provided configuration files, you can write your own, and drop it in $HOME/.radical/pilot/configs/<your_site>.json.

.. note:: Be advised that you may need system admin level knowledge for the target cluster to do so. Also, while RADICAL-Pilot can handle very different types of systems and batch system, it may run into trouble on specific configurationsor versions we did not encounter before. If you run into trouble using a cluster not in our list of officially supported ones, please drop us a note on the users mailing list.

A configuration file has to be valid JSON. The structure is as follows:

    :: 

        # filename: lrz.json
        {
            "supermuc":
            {
                "description"                 : "The SuperMUC petascale HPC cluster at LRZ.",
                "notes"                       : "Access only from registered IP addresses.",
                "schemas"                     : ["gsissh", "ssh"],
                "ssh"                         :
                {
                    "job_manager_endpoint"    : "loadl+ssh://supermuc.lrz.de/",
                    "filesystem_endpoint"     : "sftp://supermuc.lrz.de/"
                },  
                "gsissh"                      :
                {
                    "job_manager_endpoint"    : "loadl+gsissh://supermuc.lrz.de:2222/",
                    "filesystem_endpoint"     : "gsisftp://supermuc.lrz.de:2222/"
                },
                "default_queue"               : "test",
                "lrms"                        : "LOADL",
                "task_launch_method"          : "SSH",
                "mpi_launch_method"           : "MPIEXEC",
                "forward_tunnel_endpoint"     : "login03",
                "global_virtenv"              : "/home/hpc/pr87be/di29sut/pilotve",
                "pre_bootstrap"               : ["source /etc/profile",
                                                "source /etc/profile.d/modules.sh",
                                                "module load python/2.7.6",
                                                "module unload mpi.ibm", "module load mpi.intel",
                                                "source /home/hpc/pr87be/di29sut/pilotve/bin/activate"
                                                ],
                "valid_roots"                 : ["/home", "/gpfs/work", "/gpfs/scratch"],
                "pilot_agent"                 : "radical-pilot-agent-multicore.py"
            },
            "ANOTHER_KEY_NAME":
            {
                ...
            }
        }

The name of your file (here lrz.json) together with the name of the resource (supermuc) form the resource key which is used in the class:ComputePilotDescription resource attribute (lrz.supermuc).

All fields are mandatory, unless indicated otherwise below.

* **description**: a human readable description of the resource
* **notes**: information needed to form valid pilot descriptions, such as which parameter are required, etc.
* **schemas**: allowed values for the access_schema parameter of the pilot description. The first schema in the list is used by default. For each schema, a subsection is needed which specifies job_manager_endpoint and filesystem_endpoint.
* **job_manager_endpoint**: access url for pilot submission (interpreted by SAGA)
* **filesystem_endpoint**: access url for file staging (interpreted by SAGA)
* **default_queue**: queue to use for pilot submission (optional)
* **lrms**: type of job management system (LOADL, LSF, PBSPRO, SGE, SLURM, TORQUE, FORK)
* **task_launch_method**: type of compute node access (required for non-MPI units: SSH,`APRUN` or LOCAL)
* **mpi_launch_method**: type of MPI support (required for MPI units: MPIRUN, MPIEXEC, APRUN, IBRUN or POE)
* **python_interpreter**: path to python (optional)
* **pre_bootstrap**: list of commands to execute for initialization (optional)
* **valid_roots**: list of shared file system roots (optional). Pilot sandboxes must lie under these roots.
* **pilot_agent**: type of pilot agent to use (radical-pilot-agent-multicore.py)
* **forward_tunnel_endpoint**: name of host which can be used to create ssh tunnels from the compute nodes to the outside world (optional)

Several configuration files are part of the RADICAL-Pilot installation, and live under radical/pilot/configs/.