.. _apiref:


*************
API Reference
*************


Execution Context API
=====================

.. topic:: class **radical.ensemblemd.SingleClusterEnvironment(resource,cores,walltime,database_url,queue=None,username=None,allocation=None,cleanup=False)**
	
	A static execution context provides a fixed set of computational resources.

* **name**: Returns the name of the execution context
* **allocate()**: Allocates the resources
* **deallocate()**: Deallocates the resources
* **run(pattern, force_plugin=None)**: Create a new SingleClusterEnvironment instance
* **get_name()**: Returns the name of the execution pattern


Application Kernel API
======================

.. topic:: class radical.ensemblemd.Kernel(name,args=None)
	
	The Kernel provides functions to support file movement as required by the pattern.

* **cores**: number of cores the kernel is using.
* **upload_input_data**: Instructs the application to upload one or more files or directories from the host the script is running on into the kernel’s execution directory. 

Example:
	.. parsed-literal:: 
		k = Kernel(name="misc.ccount")
		k.arguments = ["--inputfile=input.txt", "--outputfile=output.txt"]
		k.upload_input_data = ["/location/on/HOST/RUNNING/THE/SCRIPT/data.txt > input.txt"]

* **download_input_data**: Instructs the kernel to download one or more files or directories from a remote HTTP server into the kernel’s execution directory.

Example:
	.. parsed-literal::
		k = Kernel(name="misc.ccount")
		k.arguments = ["--inputfile=input.txt", "--outputfile=output.txt"]
		k.download_input_data = ["http://REMOTE.WEBSERVER/location/data.txt > input.txt"]

* **copy_input_data**: Instructs the kernel to copy one or more files or directories from the execution host’s filesystem into the kernel’s execution directory.

Example:
	.. parsed-literal::
		k = Kernel(name="misc.ccount")
		k.arguments = ["--inputfile=input.txt", "--outputfile=output.txt"]
		k.copy_input_data = ["/location/on/EXECUTION/HOST/data.txt > input.txt"]

* **link_input_data**: Instructs the kernel to create a link to one or more files or directories on the execution host’s filesystem in the kernel’s execution directory.

Example:
	.. parsed-literal::
		k = Kernel(name="misc.ccount")
		k.arguments = ["--inputfile=input.txt", "--outputfile=output.txt"]
		k.link_input_data = ["/location/on/EXECUTION/HOST/data.txt > input.txt"]

* **download_output_data**: Instructs the application to download one or more files or directories from the kernel’s execution directory back to the host the script is running on.

Example:
	.. parsed-literal::
		k = Kernel(name="misc.ccount")
		k.arguments = ["--inputfile=input.txt", "--outputfile=output.txt"]
		k.download_output_data = ["output.txt > output-run-1.txt"]

* **copy_output_data**: Instructs the application to download one or more files or directories from the kernel’s execution directory to a directory on the execution host's filesystem.

Example:
	.. parsed-literal::
		k = Kernel(name="misc.ccount")
		k.arguments = ["--inputfile=input.txt", "--outputfile=output.txt"]
		k.download_output_data = ["output.txt > /location/on/EXECUTION/HOST/output.txt"]		

* **get_raw_args()**: Returns the arguments passed to the kernel.
* **get arg(name)**: Returns the value of the kernel argument given by ‘arg_name’.


Exceptions & Errors
===================

This module defines and implement all ensemblemd Exceptions.

* **exception radical.ensemblemd.exceptions.EnsemblemdError(msg)**: EnsemblemdError is the base exception thrown by the ensemblemd library. `[source] <http://radicalensemblemd.readthedocs.org/en/0.2/_modules/radical/ensemblemd/exceptions.html#EnsemblemdError>`_
	.. parsed-literal::
		Bases: exceptions.Exception

* **exception radical.ensemblemd.exceptions.NotImplementedError(method_name, class_name)**: NotImplementedError is thrown if a class method or function is not implemented. `[source] <http://radicalensemblemd.readthedocs.org/en/0.2/_modules/radical/ensemblemd/exceptions.html#NotImplementedError>`_
	.. parsed-literal::
		Bases: radical.ensemblemd.exceptions.EnsemblemdError

* **exception radical.ensemblemd.exceptions.TypeError(expected_type, actual_type)**: TypeError is thrown if a parameter of a wrong type is passed to a method or function. `[source] <http://radicalensemblemd.readthedocs.org/en/0.2/_modules/radical/ensemblemd/exceptions.html#TypeError>`_
	.. parsed-literal::
		Bases: radical.ensemblemd.exceptions.EnsemblemdError

* **exception radical.ensemblemd.exceptions.FileError(message)**: FileError is thrown if something goes wrong related to file operations, i.e., if a file doesn’t exist, cannot be copied and so on. `[source] <http://radicalensemblemd.readthedocs.org/en/0.2/_modules/radical/ensemblemd/exceptions.html#FileError>`_
	.. parsed-literal::
		Bases: radical.ensemblemd.exceptions.EnsemblemdError

* **exception radical.ensemblemd.exceptions.ArgumentError(kernel_name, message, valid_arguments_set)**: A BadArgumentError is thrown if a wrong set of arguments were passed to a kernel. `[source] <http://radicalensemblemd.readthedocs.org/en/0.2/_modules/radical/ensemblemd/exceptions.html#ArgumentError>`_
	.. parsed-literal::
		Bases: radical.ensemblemd.exceptions.EnsemblemdError

* **exception radical.ensemblemd.exceptions.NoKernelPluginError(kernel_name)**: NoKernelPluginError is thrown if no kernel plug-in could be found for a given kernel name. `[source] <http://radicalensemblemd.readthedocs.org/en/0.2/_modules/radical/ensemblemd/exceptions.html#NoKernelPluginError>`_
	.. parsed-literal::
		Bases: radical.ensemblemd.exceptions.EnsemblemdError

* **exception radical.ensemblemd.exceptions.NoKernelConfigurationError(kernel_name, resource_key)**: NoKernelConfigurationError is thrown if no kernel configuration could be found for the provided resource key. `[source] <http://radicalensemblemd.readthedocs.org/en/0.2/_modules/radical/ensemblemd/exceptions.html#NoKernelConfigurationError`_
	.. parsed-literal::
		Bases: radical.ensemblemd.exceptions.EnsemblemdError

* **exception radical.ensemblemd.exceptions.NoExecutionPluginError(pattern_name, context_name, plugin_name)**: NoExecutionPluginError is thrown if a patterns is passed to an execution context via execut() but no execution plugin for the pattern exist. `[source] <http://radicalensemblemd.readthedocs.org/en/0.2/_modules/radical/ensemblemd/exceptions.html#NoExecutionPluginError>`_
	.. parsed-literal::
		Bases: radical.ensemblemd.exceptions.EnsemblemdError