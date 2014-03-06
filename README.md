MDEnsemble API
============

Provides an easy-to-use interface based on BigJobAsync and provides functional support to execute Molecular Dynamics simulations using gromacs 


Requirements
============

* Python >= 2.5
* BigJobAsync 0.2

BigJobAsync Installation
========================

To install BigJobAsync follow the instructions on 

```
https://github.com/oleweidner/BigJobAsync/
```

Adding a Resource
==================

The resource dictionary is a set of configurations for different possible resources that might be used. 
```
https://github.com/oleweidner/BigJobAsync/blob/master/bigjobasync/resource_dictionary.py
```

The resources are referenced through the config.py file.

To use a new resource, it is enough to add the details of the resource to the resource_dictionary.py file.


Configuration file
==================

This is the primary configuration file that needs to modified by the user.
```
https://github.com/vivek-bala/MDAppKernel/blob/master/config.py
```

Two set of details to be filled in - RESOURCE details and TASK details.

RESOURCE DETAILS (example):-


		'remote_host' : 'FUTUREGRID.SIERRA',
		'remote_directory' : '/N/u/vivek91/tryout/',
		'username' : 'vivek91',
		'number_of_cores' : 2,
		'resource_name' : "sierra:12cores",
		'project_id' : "TG-MCB090174",
		'walltime' : 10

remote_host -  The target host where resource is to be acquired

remote_directory - Working directory in the remote host

username - Username required to login to the remote host

number_of_cores - Number of cores to be acquired at the remote host for all the tasks

resource_name - User can name the resource for identification purposes incase of multiple resource acquisitions at the same remote host

project_id - User can name the project for identification purposes

walltime - Time in minutes for which the resources are to be acquired


TASK DETAILS (example):-



		'source_directory' : '/home/vivek/Research/github_tests/EnsembleAPI3/gromacs_input_PYP/',
        	'output_directory' : "",

		'kernel_type' : 'python',       
        	'app_kernel' : 'gromacs_run.py',
		
		'cores_per_task' : 1,
		'number_of_tasks' : 2,



source_directory - Path at localhost from where files need to be transferred

output_directory - Path at localhost where output files need to be transferred

app_kernel_ - Filename of the python wrapper(placed in the gromacs_bjasync folder)

cores_per_task - Number of cores to be allocated to eack task

number_of_tasks - Number of ensemble members




Running the example
===================

Running the example is quite simple. Most of the changes have to be made in the config file and the file to be executed 
remains the same.

Use the --help argument to view the possible arguments
```bash
python example.py --help
```


The config file, which contains the remote host configurations and task details, is a mandatory input. To run a environment check on the intended remote host, use the --checkenv argument
```python example.py --config config.py --checkenv```


To run a simple testjob (recommended), use the --testjob argument
```python example.py --config config.py --testjob```


To run the particular workload of your experiment. Setup the TASK definitions in the config file and use the --workload argument.

```python example.py --config config.py --workload```


