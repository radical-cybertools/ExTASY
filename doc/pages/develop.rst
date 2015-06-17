.. _develop:

***************************
Customization Documentation
***************************

Writing New Application Kernels
-------------------------------

While the current set of available application kernels might provide a good set of tools to start, sooner or later you will probably want to use a tool for which no application Kernel exsits. In this case, you will have to write your own one.

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

The existing kernels can be found `here <https://github.com/radical-cybertools/radical.ensemblemd/tree/master/src/radical/ensemblemd/kernel_plugins>`_