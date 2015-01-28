.. _coam:

*****************************
Running a Coco/Amber Workload
*****************************

This section will discuss details about the execution phase. The input to the tool
is given in terms of a resource configuration file and a workload configuration file.
The execution is started based on the parameters set in these configuration files.

Running on Stampede
===================

Running the Example Workload
----------------------------

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input
files:

    1. The resource configuration file sets the parameters of the HPC resource we want
       to run the workload on, in this case Stampede.

    2. The workload configuration file defines the CoCo/Amber workload itself.

**Step 1** : Create a new directory for the example,

    ::

        mkdir $HOME/coam-on-stampede/
        cd $HOME/coam-on-stampede/

**Step 2** : Create a new resource configuration file ``stampede.rcfg`` :

    (Download it `stampede.rcfg <https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/coam-on-stampede/stampede.rcfg>`_ directly.)


    .. note::   Change the following values according to your needs :

                * UNAME
                * ALLOCATION

    ::

        REMOTE_HOST = 'stampede.tacc.utexas.edu'  # Label/Name of the Remote Machine
        UNAME       = 'username'                  # Username on the Remote Machine
        ALLOCATION  = 'TG-MCB090174'              # Allocation to be charged
        WALLTIME    = 60                          # Walltime to be requested for the pilot
        PILOTSIZE   = 16                          # Number of cores to be reserved
        WORKDIR     = None                        # Working directory on the remote machine
        QUEUE       = 'normal'                    # Name of the queue in the remote machine

        DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'

**Step 3** : Download the sample input data:

    ::

        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-stampede/mdshort.in
        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-stampede/min.in
        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-stampede/penta.crd
        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-stampede/penta.top

**Step 4** : Create a new workload configuration file ``cocoamber.wcfg`` :

    (Download it `cocoamber.wcfg <https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/coam-on-stampede/cocoamber.wcfg>`_ directly.)

    ::

        #-------------------------Applications----------------------
        simulator                = 'Amber'          # Simulator to be loaded
        analyzer                 = 'CoCo'           # Analyzer to be loaded

        #-------------------------General---------------------------
        num_iterations          = 4                 # Number of iterations of Simulation-Analysis
        start_iter              = 0                 # Iteration number with which to start
        num_CUs         = 16                # Number of tasks or Compute Units
        nsave           = 2         # Iterations after which output is transfered to local machine

        #-------------------------Simulation-----------------------
        num_cores_per_sim_cu    = 2                 # Number of cores per Simulation Compute Units
        md_input_file           = './mdshort.in'    # Entire path to MD Input file - Do not use $HOME or the likes
        minimization_input_file = './min.in'        # Entire path to Minimization file - Do not use $HOME or the likes
        initial_crd_file        = './penta.crd'     # Entire path to Coordinates file - Do not use $HOME or the likes
        top_file                = './penta.top'     # Entire path to Topology file - Do not use $HOME or the likes
        logfile                 = 'coco.log'        # Name of the log file created by pyCoCo

        #-------------------------Analysis--------------------------
        grid                    = '5'               # Number of points along each dimension of the CoCo histogram
        dims                    = '3'               # The number of projections to consider from the input pcz file

**Now you are can run the workload using :**

    ::

        RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' extasy --RPconfig stampede.rcfg --Kconfig cocoamber.wcfg 2> extasy.log

A **sample output** with expected callbacks and simulation/analysis can be found at `here <https://github.com/radical-cybertools/ExTASY/tree/master/sample_output_logs/coam-on-stampede>`_.

+------------------------+----------------+--------------+
|     Stage              |   Simulation   |   Analysis   |
+========================+================+==============+
| Expected TTC/iteration |     30-35 s    |    25-30 s   |
+------------------------+----------------+--------------+

Running on Archer
=================

Running the Example Workload
----------------------------

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input
files:

    1. The resource configuration file sets the parameters of the HPC resource we want
       to run the workload on, in this case Archer.

    2. The workload configuration file defines the CoCo/Amber workload itself.

**Step 1** : Create a new directory for the example,

    ::

        mkdir $HOME/coam-on-archer/
        cd $HOME/coam-on-archer/

**Step 2** : Create a new resource configuration file ``archer.rcfg`` :

    (Download it `archer.rcfg <https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/coam-on-archer/archer.rcfg>`_ directly.)


    .. note::   Change the following values according to your needs :

                * UNAME
                * ALLOCATION

    ::

        REMOTE_HOST = 'archer.ac.uk'              # Label/Name of the Remote Machine
        UNAME       = 'username'                  # Username on the Remote Machine
        ALLOCATION  = 'e290'                      # Allocation to be charged
        WALLTIME    = 60                          # Walltime to be requested for the pilot
        PILOTSIZE   = 24                          # Number of cores to be reserved
        WORKDIR     = None                        # Working directory on the remote machine
        QUEUE       = 'standard'                  # Name of the queue in the remote machine

        DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'

**Step 3** : Download the sample input data:

    ::

        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-archer/mdshort.in
        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-archer/min.in
        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-archer/penta.crd
        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-archer/penta.top


**Step 4** : Create a new workload configuration file ``cocoamber.wcfg`` :

    (Download it `cocoamber.wcfg <https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/coam-on-archer/cocoamber.wcfg>`_ directly.)

    ::

        #-------------------------Applications----------------------
        simulator                = 'Amber'          # Simulator to be loaded
        analyzer                 = 'CoCo'           # Analyzer to be loaded

        #-------------------------General---------------------------
        num_iterations          = 2                 # Number of iterations of Simulation-Analysis
        start_iter              = 0                 # Iteration number with which to start
        num_CUs                 = 8                # Number of tasks or Compute Units
        nsave                   = 1                 # Iterations after which output is transfered to local machine

        #-------------------------Simulation-----------------------
        num_cores_per_sim_cu    = 2                 # Number of cores per Simulation Compute Units
        md_input_file           = './mdshort.in'    # Entire path to MD Input file - Do not use $HOME or the likes
        minimization_input_file = './min.in'        # Entire path to Minimization file - Do not use $HOME or the likes
        initial_crd_file        = './penta.crd'     # Entire path to Coordinates file - Do not use $HOME or the likes
        top_file                = './penta.top'     # Entire path to Topology file - Do not use $HOME or the likes
        logfile                 = 'coco.log'        # Name of the log file created by pyCoCo

        #-------------------------Analysis--------------------------
        grid                    = '5'               # Number of points along each dimension of the CoCo histogram
        dims                    = '3'               # The number of projections to consider from the input pcz file


**Now you are can run the workload using :**

    ::

        RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' extasy --RPconfig archer.rcfg --Kconfig cocoamber.wcfg 2> extasy.log

A **sample output** with expected callbacks and simulation/analysis can be found at `here <https://github.com/radical-cybertools/ExTASY/tree/master/sample_output_logs/coam-on-archer>`_.

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