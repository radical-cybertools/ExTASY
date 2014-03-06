#!/usr/bin/env python

# ----------------------------------------------------------------------------
# MAIN DESCRIPTION

RESOURCE = {
        #Resource related inputs	--MANDATORY
        'remote_host' : 'FUTUREGRID.SIERRA',
        'remote_directory' : '/N/u/vivek91/tryout/',
        'username' : 'vivek91',
        'number_of_cores' : 1,
        'resource_name' : "sierra:12cores",
        'project_id' : "TG-MCB090174",
        'walltime' : 30
    }

TASK = {
        #Task related inputs		--MANDATORY

        #Paths/Directories involved
        'source_directory' : '/home/vivek/Research/github_tests/EnsembleAPI3/gromacs_input_PYP/',
        'output_directory' : "",

        #kernel/wrapper names
        'kernel_type' : 'python',       #/bin/bash or python
        'app_kernel' : 'gromacs_run.py',

        #Resource requirement and number of tasks
        'cores_per_task' : 1,
        'number_of_tasks' : 2,

    }

