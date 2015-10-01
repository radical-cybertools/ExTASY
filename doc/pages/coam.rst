.. _coam:

:tocdepth: 4

*****************************
Running a Coco/Amber Workload
*****************************

This section will discuss details about the execution phase. The input to the tool
is given in terms of a resource configuration file and a workload configuration file.
The execution is started based on the parameters set in these configuration files. In 
section 3.1, we discuss execution on Stampede and in section 3.2, we discuss execution 
on Archer.

Running on Stampede
===================

Running using Example Workload Config and Resource Config
---------------------------------------------------------

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input
files:

    1. The resource configuration file sets the parameters of the HPC resource we want
       to run the workload on, in this case Stampede.

    2. The workload configuration file defines the CoCo/Amber workload itself. The configuration file given in this example is strictly meant for the coco-amber usecase only.

**Step 1** : Create a new directory for the example,

    ::

        mkdir $HOME/extasy-tutorial/
        cd $HOME/extasy-tutorial/

**Step 2** : Download the config files and the input files directly using the following link.

    ::

        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.1/tarballs/coam-on-stampede.tar.gz
        tar xvfz coam-on-stampede.tar.gz

**Step 3** : In the coam-on-stampede folder, a resource configuration file ``stampede.rcfg`` exists. Details and modifications required are as follows:

    .. note:: 
                For the purposes of this example, you require to change only:

                    * UNAME
                    * ALLOCATION

                The other parameters in the resource configuration are already set up to successfully execute the workload in this example.

    ::

        REMOTE_HOST = 'xsede.stampede'  # Label/Name of the Remote Machine
        UNAME       = 'username'                  # Username on the Remote Machine
        ALLOCATION  = 'TG-MCB090174'              # Allocation to be charged
        WALLTIME    = 60                          # Walltime to be requested for the pilot
        PILOTSIZE   = 16                          # Number of cores to be reserved
        WORKDIR     = None                        # Working directory on the remote machine
        QUEUE       = 'normal'                    # Name of the queue in the remote machine

        DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'


**Step 4** : In the coam-on-stampede folder, a workload configuration file ``cocoamber.wcfg`` exists. Details and modifications required are as follows:


    ::

        #-------------------------Applications----------------------
        simulator                = 'Amber'          # Simulator to be loaded
        analyzer                 = 'CoCo'           # Analyzer to be loaded

        #-------------------------General---------------------------
        num_iterations          = 4                 # Number of iterations of Simulation-Analysis
        start_iter              = 0                 # Iteration number with which to start
        num_CUs                 = 16                # Number of tasks or Compute Units
        nsave                   = 2                 # Iterations after which output is transfered to local machine
        checkfiles              = 4                 # Iterations after which to test if the expected files are present on remote/ does not download to local

        #-------------------------Simulation-----------------------
        num_cores_per_sim_cu    = 2                 # Number of cores per Simulation Compute Units
        md_input_file           = './mdshort.in'    # Entire path to MD Input file - Do not use $HOME or the likes
        minimization_input_file = './min.in'        # Entire path to Minimization file - Do not use $HOME or the likes
        initial_crd_file        = './penta.crd'     # Entire path to Coordinates file - Do not use $HOME or the likes
        top_file                = './penta.top'     # Entire path to Topology file - Do not use $HOME or the likes
        logfile                 = 'coco.log'        # Name of the log file created by pyCoCo
        atom_selection          = None              # optional atom selection string that enables pyCoCo to work only on a subset of the biomolecular system

        #-------------------------Analysis--------------------------
        grid                    = '5'               # Number of points along each dimension of the CoCo histogram
        dims                    = '3'               # The number of projections to consider from the input pcz file


    .. note::
                
                All the parameters in the above example file are mandatory for amber-coco. There are no other parameters currently supported.


**Now you are can run the workload using :**

If your shell is BASH,

    ::

        EXTASY_DEBUG=True RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' extasy --RPconfig stampede.rcfg --Kconfig cocoamber.wcfg 2> extasy.log

If your shell is CSH,

    ::

        setenv EXTASY_DEBUG True
        setenv RADICAL_PILOT_VERBOSE 'debug'
        setenv SAGA_VERBOSE 'debug'
        extasy --RPconfig stampede.rcfg --Kconfig cocoamber.wcfg |& tee extasy.log

A **sample output** with expected callbacks and simulation/analysis can be found at `here <https://github.com/radical-cybertools/ExTASY/tree/extasy_0.1/sample_output_logs/coam-on-stampede>`_.

+------------------------+----------------+--------------+
|     Stage              |   Simulation   |   Analysis   |
+========================+================+==============+
| Expected TTC/iteration |     30-35 s    |    25-30 s   |
+------------------------+----------------+--------------+

There are two stages in the execution phase - Simulation and Analysis. Execution
starts with any Preprocessing that might be required on the input data and then
moves to Simulation stage. In the Simulation stage, a number of tasks (num_CUs)
are launched to execute on the target machine. The number of tasks set to execute
depends on the PILOTSIZE, num_CUs, num_cores_per_sim_cu, the number of tasks in
execution state simultaneously would be PILOTSIZE/num_cores_per_sim_cu. As each
task attains 'Done' (completed) state, the remain tasks are scheduled till all
the num_CUs tasks are completed.

This is followed by the Analysis stage, one task is scheduled on the target machine
which takes all the cores as the PILOTSIZE to perform the analysis and returns the
data required for the next iteration of the Simulation stage. As can be seen, per
iteration, there are (num_CUs+1) tasks executed.


Running on Archer
=================

Running using Example Workload Config and Resource Config
---------------------------------------------------------

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input
files:

    1. The resource configuration file sets the parameters of the HPC resource we want
       to run the workload on, in this case Archer.

    2. The workload configuration file defines the CoCo/Amber workload itself. The configuration file given in this example is strictly meant for the coco-amber usecase only.

**Step 1** : Create a new directory for the example,

    ::

        mkdir $HOME/extasy-tutorial/
        cd $HOME/extasy-tutorial/

**Step 2** : Download the config files and the input files directly using the following link.

    ::

        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.1/tarballs/coam-on-archer.tar.gz
        tar xvfz coam-on-archer.tar.gz

**Step 3** : In the coam-on-archer folder, a resource configuration file ``archer.rcfg`` exists. Details and modifications required are as follows:

    .. note:: 
                For the purposes of this example, you require to change only:

                    * UNAME
                    * ALLOCATION

                The other parameters in the resource configuration are already set up to successfully execute the workload in this example.
    ::

        REMOTE_HOST = 'epsrc.archer'              # Label/Name of the Remote Machine
        UNAME       = 'username'                  # Username on the Remote Machine
        ALLOCATION  = 'e290'                      # Allocation to be charged
        WALLTIME    = 60                          # Walltime to be requested for the pilot
        PILOTSIZE   = 24                          # Number of cores to be reserved
        WORKDIR     = None                        # Working directory on the remote machine
        QUEUE       = 'standard'                  # Name of the queue in the remote machine

        DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'


**Step 4** : In the coam-on-archer folder, a resource configuration file ``cocoamber.wcfg`` exists. Details and modifications required are as follows:

    ::

        #-------------------------Applications----------------------
        simulator                = 'Amber'          # Simulator to be loaded
        analyzer                 = 'CoCo'           # Analyzer to be loaded

        #-------------------------General---------------------------
        num_iterations          = 2                 # Number of iterations of Simulation-Analysis
        start_iter              = 0                 # Iteration number with which to start
        num_CUs                 = 8                 # Number of tasks or Compute Units
        nsave                   = 1                 # Iterations after which output is transfered to local machine
        checkfiles              = 4                 # Iterations after which to test if the expected files are present on remote/ does not download to local

        #-------------------------Simulation-----------------------
        num_cores_per_sim_cu    = 2                 # Number of cores per Simulation Compute Units
        md_input_file           = './mdshort.in'    # Entire path to MD Input file - Do not use $HOME or the likes
        minimization_input_file = './min.in'        # Entire path to Minimization file - Do not use $HOME or the likes
        initial_crd_file        = './penta.crd'     # Entire path to Coordinates file - Do not use $HOME or the likes
        top_file                = './penta.top'     # Entire path to Topology file - Do not use $HOME or the likes
        logfile                 = 'coco.log'        # Name of the log file created by pyCoCo
        atom_selection          = None              # optional atom selection string that enables pyCoCo to work only on a subset of the biomolecular system

        #-------------------------Analysis--------------------------
        grid                    = '5'               # Number of points along each dimension of the CoCo histogram
        dims                    = '3'               # The number of projections to consider from the input pcz file


    .. note::
                
                All the parameters in the above example file are mandatory for amber-coco. There are no other parameters currently supported.


**Now you are can run the workload using :**

If your shell is BASH,

    ::

        EXTASY_DEBUG=True RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' extasy --RPconfig archer.rcfg --Kconfig cocoamber.wcfg 2> extasy.log


If your shell is CSH,

    ::

        setenv EXTASY_DEBUG True
        setenv RADICAL_PILOT_VERBOSE 'debug'
        setenv SAGA_VERBOSE 'debug'
        extasy --RPconfig archer.rcfg --Kconfig cocoamber.wcfg |& tee extasy.log
        

A **sample output** with expected callbacks and simulation/analysis can be found at `here <https://github.com/radical-cybertools/ExTASY/tree/extasy_0.1/sample_output_logs/coam-on-archer>`_.

+------------------------+----------------+--------------+
|     Stage              |   Simulation   |   Analysis   |
+========================+================+==============+
| Expected TTC/iteration |     60-100 s   |   150-200 s  |
+------------------------+----------------+--------------+


There are two stages in the execution phase - Simulation and Analysis. Execution
starts with any Preprocessing that might be required on the input data and then
moves to Simulation stage. In the Simulation stage, a number of tasks (num_CUs)
are launched to execute on the target machine. The number of tasks set to execute
depends on the PILOTSIZE, num_CUs, num_cores_per_sim_cu, the number of tasks in
execution state simultaneously would be PILOTSIZE/num_cores_per_sim_cu. As each
task attains 'Done' (completed) state, the remain tasks are scheduled till all
the num_CUs tasks are completed.

This is followed by the Analysis stage, one task is scheduled on the target machine
which takes all the cores as the PILOTSIZE to perform the analysis and returns the
data required for the next iteration of the Simulation stage. As can be seen, per
iteration, there are (num_CUs+1) tasks executed.


Understanding the Output
========================

In the local machine, a "backup" folder is created and at the end of every checkpoint intervel (=nsave) an "iter*" folder is created which contains the necessary files to start the next iteration.


For example, in the case of CoCo-Amber on stampede, for 4 iterations with nsave=2:

::

    coam-on-stampede$ ls
    backup/  cocoamber.wcfg  mdshort.in  min.in  penta.crd  penta.top  stampede.rcfg

    coam-on-stampede/backup$ ls
    iter1/  iter3/



The "iter*" folder will not contain any of the initial files such as the topology file, minimization file, etc since they already exist on the local machine. In coco-amber, the "iter*" folder contains the NetCDF files required to start the next iteration and a logfile of the CoCo stage of the current iteration.


::

    coam-on-stampede/backup/iter1$ ls
    1_coco.log    md_0_11.ncdf  md_0_14.ncdf  md_0_2.ncdf  md_0_5.ncdf  md_0_8.ncdf  md_1_10.ncdf  md_1_13.ncdf  md_1_1.ncdf  md_1_4.ncdf  md_1_7.ncdf
    md_0_0.ncdf   md_0_12.ncdf  md_0_15.ncdf  md_0_3.ncdf  md_0_6.ncdf  md_0_9.ncdf  md_1_11.ncdf  md_1_14.ncdf  md_1_2.ncdf  md_1_5.ncdf  md_1_8.ncdf
    md_0_10.ncdf  md_0_13.ncdf  md_0_1.ncdf   md_0_4.ncdf  md_0_7.ncdf  md_1_0.ncdf  md_1_12.ncdf  md_1_15.ncdf  md_1_3.ncdf  md_1_6.ncdf  md_1_9.ncdf


It is important to note that since, in coco-amber, all the NetCDF files of previous and current iterations are transferred at each checkpoint, it might be useful to have longer checkpoint intervals. Since smaller intervals would lead to heavy data transfer of redundant data.


On the remote machine, inside the pilot-* folder you can find a folder called "staging_area". This location is used to exchange/link/move intermediate data. The shared data is kept in "staging_area/" and the iteration specific inputs/outputs can be found in their specific folders (="staging_area/iter*").

::

    $ cd staging_area/
    $ ls
    iter0/  iter1/  iter2/  iter3/  mdshort.in  min.in  penta.crd  penta.top  postexec.py



CoCo/Amber Restart Mechanism
============================

If the above examples were successful, you can go ahead try and the restart mechanism. The restart mechanism is designed to resume the experiment from one of the checkpoints that you might have made in the previous experiments. 


Therefor, for a valid/successful restart scenario, data from a previous experiment needs to exist in the backup/ folder on the local machine. Restart can only be done from a checkpoint (defined by nsave in the kernel config file) made in the previous experiment.


Example,

        **Experiment 1** : num_iterations = 4, start_iter = 0, nsave = 2

        **Backups created** : iter1/ (after 2 iterations) , iter3/ (after 4 iterations)

        **Experiment 2 (restart)** : num_iterations = 2, start_iter = 4 (=start from 5th iter), nsave = 2

        **Note** : start_iter should match one of the previous checkpoints and start_iter should be a multiple of nsave.

If, in the first experiment, you ran 4 iterations with nsave set to 2, you will have backups created after the 2nd and 4th iteration. Once this is successful, in the second experiment, you can resume from either of the backups/checkpoints. In the above example, the experiment is resumed from the 4th iteration.


In CoCo/Amber, at every checkpoint the ncdf files from all the iterations are transferred to the local machine in order to be able to restart. You could set nsave = num_iterations to make a one time transfer after all the iterations.


Having a small checkpoint interval increases redundant data. Example,

        **Experiment 1** : num_iterations = 8, start_iter = 0, nsave = 2

        **Backups created** :-

                                iter1/ (contains ncdf files for first 2 iters)

                                iter3/ (contains ncdf files for first 4 iters)

                                iter5/ (contains ncdf files for first 6 iters)

                                iter7/ (contains ncdf files for first 8 iters)

