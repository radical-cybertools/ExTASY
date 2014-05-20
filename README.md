Coupled Simulation-Analysis Execution (ExTASY)
===============================================

Provides a command line interface to run multiple Molecular Dynamics (MD) simulations, which can be coupled to an analysis tool. The coupled simulation-analysis execution pattern (aka ExTASY pattern) currently supports two examples: 
(a) Gromacs as the "Simulator" and LSDMap as the "Analyzer"; (b) AMBER as the simulation engine and COCO as the analyzer. Due to the plugin-based architecture, this execution pattern, will be 
expandable as to support more Simulators and Analyzers.


Requirements
============

* python >= 2.6
* virtualenv >= 1.11
* pip >= 1.5
* Password-less ssh login to remote machine

> Some tips to setup a password-less login
> ```
> http://www.linuxproblem.org/art_9.html
> ```


Installation
=============

To install the ExTASY framework, create a virtual environment and use pip to install the package

```
virtualenv /tmp/test
source /tmp/test/bin/activate
cd /tmp/
git clone https://github.com/radical-cybertools/ExTASY.git
cd ExTASY
python setup.py install
```

To verify the installation, check the current version

```
python -c 'import radical.ensemblemd.extasy as extasy; print extasy.version'
```

> You can set an Environement variable CONFIG to point to the configuration folder in the cloned repository.
> ```
> export CONFIG=/tmp/ExTASY/config
> ```

Usage
======


Adding a Resource
-------------------

The various resources to be used are added to a JSON file. The resources are referenced through the config.py file. An example set of resource
 configurations can be found in

 ```
 https://github.com/radical-cybertools/ExTASY/tree/master/config
 ```

Resource config files for XSEDE & FUTUREGRID have been added as part of the config. To write your own resource configuration files, refer
 to the *Writing a Custom Resource Configuration File section* in the radical. pilot documentation

 ```
 http://radicalpilot.readthedocs.org/en/latest/machconf.html#writing-a-custom-resource-configuration-file
 ```


Config file
-------------

This section is mainly to explain the format of the config file. Skip ahead for running sample tests.

```
https://github.com/radical-cybertools/ExTASY/tree/master/config/config.py
```

This is the primary configuration file that needs to modified by the user. This file allows the user to :-

1) Specify resource details

* select the target resource (machine + working directory) from the bulk of resources present in the JSON config files.
* define the number of cores to be reserved for the totality of the experiment (aka pilot size)
* define the time for which you want to reserve the cores


```

RESOURCE = {
        #Resource related inputs	--MANDATORY
        'remote_host' : 'stampede.tacc.utexas.edu',
        'number_of_cores' : 2,
        'walltime' : 5
    }


```

2) Specify task details

* specify the source directory from which the data has to be transfered. All the files which are commonly shared/accessed by individual tasks need to be in this folder; all the files in this folder are transferred to the remote host.
* specify the output file to be transferred back to the local machine.
* the name and type of the kernel to be executed as the task
* number of tasks (or ensembles) to be executed
* number of cores out of the total cores to allocated to each task


```
TASK = {
        #Task related inputs		--MANDATORY

        #Paths/Directories involved
        #Keep the kernel and the files accessed by the kernel/that need to be transferred in the source_directory
        'source_directory' : '/tmp/ExTASY/gromacs_input_PYP/',
        'output' : "md.log",

        #kernel/wrapper names
        'kernel_type' : '/bin/bash',       #/bin/bash or python
        'kernel' : 'MDRun.sh',      #this file should contain all the bash level commands/functions that are executed

        #Resource requirement and number of tasks
        'cores_per_task' : 1,
        'number_of_tasks' : 2,
    }
```

3) UNAME

Username to login the remote target (leave as '' if running as localhost)

3) RCONF

This is a list of paths to different resource configuration JSON files.


4) DBURL

This a url to the mongodb server to be used.


Running the tests
------------------

The API provides two modes of running tests. **checkenv** and **testjob**. Both the tests are recommended before submitting large workloads.

You will have to do things.

* Set an Environment variable "RADICAL_PILOT_USERNAME"  - username on the remote/target machine
* Open the config.py file inside $CONFIG, and set the target machine in remote_host. By default, it is set to Stampede.

> For more possible values for "remote_host", see
> ```
> https://raw.githubusercontent.com/radical-cybertools/radical.pilot/master/configs/xsede.json

> https://raw.githubusercontent.com/radical-cybertools/radical.pilot/master/configs/futuregrid.json
> ```



1) **checkenv**

This mode is to check whether the necessary modules are present and loaded in the remote host before workload submission.

To run a environment check on the intended remote host, use the --checkenv argument
```ensemble --config $CONFIG/config.py --checkenv```

**Note**
* ```--config``` should be followed by the complete path of the config.py file or $CONFIG/config.py if CONFIG has been set.
* Be sure to have the config.py file and JSON resource configuration files set before running the tests.


2) **testjob**

This mode is to submit a basic dummy gromacs task on to the specified remote host to make sure the execution is complete and usable.

To run a simple testjob on the intended remote host, use the --testjob argument
```ensemble --config $CONFIG/config.py --testjob```

**Note**
* ```--config``` should be followed by the complete path of the config.py file or $CONFIG/config.py if CONFIG has been set.
* Be sure to have the config.py file and JSON resource configuration files set before running the tests.



Running the workload
--------------------

To run the particular workload of your experiment. Setup the TASK definitions in the config file and use the --workload or --w argument.

```ensemble --config $CONFIG/config.py --workload```

**Note**
* ```--config``` should be followed by the complete path of the config.py file or $CONFIG/config.py if CONFIG has been set.
* Be sure to have the config.py file and JSON resource configuration files set before running the workload.
