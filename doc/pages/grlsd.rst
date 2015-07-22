.. _grlsd:

:tocdepth: 4

*********************************
Running a Gromacs/LSDMap Workload
*********************************

This section will discuss details about the execution phase. The input to the tool
is given in terms of a resource configuration file and a workload configuration file.
The execution is started based on the parameters set in these configuration files. In 
section 4.1, we discuss execution on Stampede and in section 4.2, we discuss execution 
on Archer.

Running on Stampede
===================

Running using Example Workload Config and Resource Config
---------------------------------------------------------

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input
files:

    1. The resource configuration file sets the parameters of the HPC resource we want to
       run the workload on, in this case Stampede.

    2. The workload configuration file defines the GROMACS/LSDMap workload itself. The configuration file given in this example is strictly meant for the gromacs-lsdmap usecase only.

**Step 1**: Create a new directory for the example,

    ::

        mkdir $HOME/extasy-tutorial/
        cd $HOME/extasy-tutorial/


**Step 2**: Download the config files and the input files directly using the following link.

    ::

    	curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/tarballs/grlsd-on-stampede.tar.gz
        tar xvfz grlsd-on-stampede.tar.gz
        cd grlsd-on-stampede


**Step 3**: In the grlsd-on-stampede folder, a resource configuration file ``stampede.rcfg`` exists. Details and modifications required are as follows:

    .. note:: 
                For the purposes of this example, you require to change only:

                    * UNAME
                    * ALLOCATION

                The other parameters in the resource configuration are already set up to successfully execute the workload in this example.

    ::

        REMOTE_HOST = 'stampede.tacc.utexas.edu'  # Label/Name of the Remote Machine
        UNAME       = 'username'                  # Username on the Remote Machine
        ALLOCATION  = 'TG-MCB090174'              # Allocation to be charged
        WALLTIME    = 60                          # Walltime to be requested for the pilot
        PILOTSIZE   = 16                          # Number of cores to be reserved
        WORKDIR     = None                        # Working directory on the remote machine
        QUEUE       = 'normal'                    # Name of the queue in the remote machine

        DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'


**Step 4**: In the grlsd-on-stampede folder, a workload configuration file ``gromacslsdmap.wcfg`` exists. Details and modifications are as follows:


    ::

        #-------------------------Applications----------------------
        simulator             = 'Gromacs'           # Simulator to be loaded
        analyzer              = 'LSDMap'            # Analyzer to be loaded

        #--------------------------General--------------------------------
        num_CUs              = 16                   # Number of tasks or Compute Units
        num_iterations       = 3                    # Number of iterations of Simulation-Analysis
        start_iter           = 0                    # Iteration number with which to start
        nsave                = 2                    # # Iterations after which output is transfered to local machine

        #--------------------------Simulation--------------------------------
        num_cores_per_sim_cu = 1                    # Number of cores per Simulation Compute Units
        md_input_file        = './input.gro'        # Entire path to the MD Input file - Do not use $HOME or the likes
        mdp_file             = './grompp.mdp'       # Entire path to the MD Parameters file - Do not use $HOME or the likes
        top_file             = './topol.top'        # Entire path to the Topology file - Do not use $HOME or the likes
        ndx_file             = None                   # Entire path to the Index file - Do not use $HOME or the likes
        grompp_options       = None                   # Command line options for when grompp is used
        mdrun_options        = None                   # Command line options for when mdrun is used
        itp_file_loc         = None                   # Entire path to the location of .itp files - Do not use $HOME or the likes
        md_output_file       = 'tmp.gro'            # Filename to be used for the simulation output

        #--------------------------Analysis----------------------------------
        lsdm_config_file     = './config.ini'       # Entire path to the LSDMap configuration file - Do not use $HOME or the likes
        num_runs             = 1000                # Number of runs to be performed in the Selection step in Analysis
        w_file               = 'weight.w'           # Filename to be used for the weight file
        max_alive_neighbors  = '10'                 # Maximum alive neighbors to be considered while reweighting
        max_dead_neighbors   = '1'                  # Maximum dead neighbors to be considered while reweighting

    .. note:: 

                All the parameters in the above example file are mandatory for gromacs-lsdmap. If *ndxfile*, *grompp_options*, *mdrun_options* and *itp_file_loc* are not required, they should be set to None; but they still have to mentioned in the configuration file. There are no other parameters currently supported.


**Step 5**: Download the script using:

	::

		curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/example/gromacs_lsdmap/extasy_gromacs_lsdmap.py


**Now you are can run the workload using :**


If your shell is BASH,

    ::

        EXTASY_DEBUG=True RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' python extasy_gromacs_lsdmap.py --RPconfig stampede.rcfg --Kconfig gromacslsdmap.wcfg 2> extasy.log

If your shell is CSH,

    ::

        setenv EXTASY_DEBUG True
        setenv RADICAL_PILOT_VERBOSE 'debug'
        setenv SAGA_VERBOSE 'debug'
        python extasy_gromacs_lsdmap.py --RPconfig stampede.rcfg --Kconfig gromacslsdmap.wcfg |& tee extasy.log



Running on Archer
=================

Running using Example Workload Config and Resource Config
---------------------------------------------------------

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input
files:

    1. The resource configuration file sets the parameters of the HPC resource we want
       to run the workload on, in this case Archer.

    2. The workload configuration file defines the CoCo/Amber workload itself. The configuration file given in this example is strictly meant for the gromacs-lsdmap usecase only.

**Step 1**: Create a new directory for the example,

    ::

        mkdir $HOME/extasy-tutorial/
        cd $HOME/extasy-tutorial/

**Step 2**: Download the config files and the input files directly using the following link.

    ::
    	curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/tarballs/grlsd-on-archer.tar.gz
        tar xvfz grlsd-on-archer.tar.gz
        cd grlsd-on-archer

**Step 3**: In the grlsd-on-archer folder, a resource configuration file ``archer.rcfg`` exists. Details and modifications required are as follows:


    .. note:: 
                For the purposes of this example, you require to change only:

                    * UNAME
                    * ALLOCATION

                The other parameters in the resource configuration are already set up to successfully execute the workload in this example.

    ::

        REMOTE_HOST = 'archer.ac.uk'              # Label/Name of the Remote Machine
        UNAME       = 'username'                  # Username on the Remote Machine
        ALLOCATION  = 'e290'                      # Allocation to be charged
        WALLTIME    = 60                          # Walltime to be requested for the pilot
        PILOTSIZE   = 24                          # Number of cores to be reserved
        WORKDIR     = None                        # Working directory on the remote machine
        QUEUE       = 'standard'                  # Name of the queue in the remote machine

        DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'


**Step 4**: In the grlsd-on-archer folder, a workload configuration file ``gromacslsdmap.wcfg`` exists. Details and modifications required are as follows:

    ::

        #-------------------------Applications----------------------
        simulator             = 'Gromacs'           # Simulator to be loaded
        analyzer              = 'LSDMap'            # Analyzer to be loaded

        #--------------------------General--------------------------------
        num_CUs              = 24                   # Number of tasks or Compute Units
        num_iterations       = 2                    # Number of iterations of Simulation-Analysis
        start_iter           = 0                    # Iteration number with which to start
        nsave                = 1                    # # Iterations after which output is transfered to local machine

        #--------------------------Simulation--------------------------------
        num_cores_per_sim_cu = 1                    # Number of cores per Simulation Compute Units
        md_input_file        = './input.gro'        # Entire path to the MD Input file - Do not use $HOME or the likes
        mdp_file             = './grompp.mdp'       # Entire path to the MD Parameters file - Do not use $HOME or the likes
        top_file             = './topol.top'        # Entire path to the Topology file - Do not use $HOME or the likes
        ndx_file             = None                   # Entire path to the Index file - Do not use $HOME or the likes
        grompp_options       = None                   # Command line options for when grompp is used
        mdrun_options        = None                   # Command line options for when mdrun is used
        itp_file_loc         = None                   # Entire path to the location of .itp files - Do not use $HOME or the likes
        md_output_file       = 'tmp.gro'            # Filename to be used for the simulation output

        #--------------------------Analysis----------------------------------
        lsdm_config_file     = './config.ini'       # Entire path to the LSDMap configuration file - Do not use $HOME or the likes
        num_runs             = 100                # Number of runs to be performed in the Selection step in Analysis
        w_file               = 'weight.w'           # Filename to be used for the weight file
        max_alive_neighbors  = '10'                 # Maximum alive neighbors to be considered while reweighting
        max_dead_neighbors   = '1'                  # Maximum dead neighbors to be considered while reweighting


    .. note:: 

                All the parameters in the above example file are mandatory for gromacs-lsdmap. If *ndxfile*, *grompp_options*, *mdrun_options* and *itp_file_loc* are not required, they should be set to None; but they still have to mentioned in the configuration file. There are no other parameters currently supported.

**Step 5**: Download the script using:

	::
    
		curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/example/gromacs_lsdmap/extasy_gromacs_lsdmap.py


**Now you are can run the workload using :**

If your shell is BASH,

    ::

        EXTASY_DEBUG=True RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' python extasy_gromacs_lsdmap.py --RPconfig archer.rcfg --Kconfig gromacslsdmap.wcfg 2> extasy.log


If your shell is CSH,

    ::

        setenv EXTASY_DEBUG True
        setenv RADICAL_PILOT_VERBOSE 'debug'
        setenv SAGA_VERBOSE 'debug'
        python extasy_gromacs_lsdmap.py --RPconfig archer.rcfg --Kconfig gromacslsdmap.wcfg |& tee extasy.log

Understanding the Output
========================

In the local machine, a "backup" folder is created and at the end of every checkpoint intervel (=nsave) an "iter*" folder is created which contains the necessary files to start the next iteration.


For example, in the case of gromacs-lsdmap on stampede, for 4 iterations with nsave=2:

::

    grlsd-on-stampede$ ls
    backup/  config.ini  gromacslsdmap.wcfg  grompp.mdp  input.gro  stampede.rcfg  topol.top

    grlsd-on-stampede/backup$ ls
    iter1/  iter3/



The "iter*" folder will not contain any of the initial files such as the topology file, minimization file, etc since they already exist on the local machine. In gromacs-lsdmap, the "iter*" folder contains the coordinate file and weight file required in the next iteration. It also contains a logfile about the lsdmap stage of the current iteration.

::

    grlsd-on-stampede/backup/iter1$ ls
    2_input.gro  lsdmap.log  weight.w



On the remote machine, inside the pilot-* folder you can find a folder called "staging_area". This location is used to exchange/link/move intermediate data. The shared data is kept in "staging_area/" and the iteration specific inputs/outputs can be found in their specific folders (="staging_area/iter*").

::

    $ cd staging_area/
    $ ls
    config.ini  gro.py   input.gro   iter1/  iter3/    post_analyze.py  reweighting.py   run.py     spliter.py
    grompp.mdp  gro.pyc  iter0/      iter2/  lsdm.py   pre_analyze.py   run_analyzer.sh  select.py  topol.top

