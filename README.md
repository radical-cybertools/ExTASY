EnsembleAPI
============

Provides an easy-to-use interface based on Radical pilot and provides functional support to simulate Ensembles


Requirements
============

* Python >= 2.5


Radical-pilot Installation
========================

To install the EnsembleAPI framework, create a virtual environment and use pip to install the package

```
virtualenv $HOME/test
source $HOME/test/bin/activate
git clone https://github.com/radical-cybertools/MDEnsemble.git
cd MDEnsemble
python setup.py install
```

To verify the installation, check the current version

```
python -c 'import radical.ensemblemd.ensembleapi as ensembleapi; print ensembleapi.version'
```

USAGE
======


Adding a Resource
-------------------

The various resources to be used are added to a JSON file. The resources are referenced through the config.py file. An example set of resource
 configurations can be found in

 ```
 https://github.com/radical-cybertools/MDEnsemble/tree/master/config
 ```

Resource config files for XSEDE & FUTUREGRID have been added as part of the config. To write your own resource configuration files, refer
 to the *Writing a Custom Resource Configuration File section* in the radical. pilot documentation

 ```
 http://radicalpilot.readthedocs.org/en/latest/machconf.html#writing-a-custom-resource-configuration-file
 ```


Config file
-------------

```
https://github.com/radical-cybertools/MDEnsemble/tree/master/config/config.py
```


This is the primary configuration file that needs to modified by the user. This file allows the user to :-

1) Specify resource details

* select the target resource (machine + working directory) from the bulk of resources present in the JSON config files.
* define the number of cores to be reserved for the totality of the experiment (aka pilot size)
* define the time for which you want to reserve the cores
* define credentials for remote host access

```

RESOURCE = {
        #Resource related inputs	--MANDATORY
        'remote_host' : 'stampede.tacc.utexas.edu',
        'remote_directory' : '/home1/02734/vivek91/output/',
        'username' : 'vivek91',
        'number_of_cores' : 2,
        'walltime' : 5
    }

```

2) Specify task details

* specify the source directory from which the data has to be transfered + output directory to hold the output back on the local machine
* the name and type of the kernel to be executed as the task
* number of tasks/ensembles to executed
* number of cores out of the total cores to allocated to each task


```
TASK = {
        #Task related inputs		--MANDATORY

        #Paths/Directories involved
        'source_directory' : '../gromacs_input_alanine_dipeptide/',
        'output_directory' : "",    #None would bring the output to the current directory

        #kernel/wrapper names
        'kernel_type' : 'python',       #/bin/bash or python
        'kernel_name' : 'gromacs_python_wrapper.py',

        #Resource requirement and number of tasks
        'cores_per_task' : 1,
        'number_of_tasks' : 2,

    }
```

3) RCONF

This is a list of paths to different resource configuration JSON files.


4) DBURL

This a url to the mongodb server to be used.


Running the tests
------------------

The API provides two modes of running tests. **checkenv** and **testjob**. Both the tests are recommended before submitting large workloads.


* checkenv

This mode is to check whether the necessary modules are present and loaded in the remote host before workload submission.

To run a environment check on the intended remote host, use the --checkenv argument
```ensembleapi --config ../config/config.py --checkenv```

**Note**

* ```--config``` should be followed by the complete path of the config.py file
* Be sure to have the config.py file and JSON resource configuration files set before running the tests.


* testjob

This mode is to submit a basic dummy gromacs task on to the specified remote host to make sure the execution is complete and usable.

To run a simple testjob on the intended remote host, use the --testjob argument
```ensembleapi --config ../config/config.py --testjob```

**Note**

* ```--config``` should be followed by the complete path of the config.py file
* Be sure to have the config.py file and JSON resource configuration files set before running the tests.


Running the workload
--------------------

To run the particular workload of your experiment. Setup the TASK definitions in the config file and use the --workload or --w argument.

```ensembleapi --config ../config/config.py --workload```

**Note**

* ```--config``` should be followed by the complete path of the config.py file
* Be sure to have the config.py file and JSON resource configuration files set before running the tests.
