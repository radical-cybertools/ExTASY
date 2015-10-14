.. _develop:

*************
Customization
*************

Writing New Application Kernels
-------------------------------

While the current set of available application kernels might provide a good set of tools to start, sooner or later you will probably want to use a tool for which no application Kernel exsits. This section describes how you can add your custom kernels. 

We have two files, user_script.py which contains the user application which **uses** our custom kernel, new_kernel.py which contains the definition of the custom kernel. You can download them from the following links:

* :download:`user_script.py <../scripts/user_script.py>`
* :download:`new_kernel.py <../scripts/new_kernel.py>`


Let's first take a look at ``new_kernel.py``.

.. literalinclude:: ../scripts/new_kernel.py
        :language: python
        :linenos:

Lines 5-24 contain information about the kernel to be defined. "name" and "arguments" keys are mandatory. The "arguments" key needs to specify the arguments the kernel expects. You can specify whether the individual arguments are mandatory or not. "machine_configs" is not mandatory, but creating a dictionary with resource names (same as defined in the SingleClusterEnvironment) as keys and values which are resource specific lets use the same kernel to be used on different machines.

In lines 28-50, we define a user defined class (of "KernelBase" type) with two mandatory functions. First the constructor, self-explanatory. Second, ``_bind_to_resource`` which is the function that (as the name suggests) binds the kernel with its resource specific values, during execution. In lines 41, 43-45, you can see how the "machine_configs" dictionary approach is helping us solve the tool-level heterogeneity across resources. There might be other ways to do this (if conditions,etc), but we feel this could be quite convenient.

Now, let's take a look at ``user_script.py``

.. literalinclude:: ../scripts/user_script.py
        :language: python
        :linenos:

There are 3 important lines in this script. In line 7, we import the get_engine function in order to register our new kernel. In line 10, we import our new kernel and in line 13, we register our kernel. **THAT'S IT**. We can continue with the application as in the previous examples.


Writing a Custom Resource Configuration File
--------------------------------------------

A number of resources are already supported by RADICAL-Pilot, they are list in :ref:`chapter_resources`. If you want to use RADICAL-Pilot with a resource that is not in any of the provided configuration files, you can write your own, and drop it in $HOME/.radical/pilot/configs/<your_site>.json.

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