.. _coam:

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


**Step 1**: Create a new directory for the example,

    ::

        mkdir $HOME/extasy-tutorial/
        cd $HOME/extasy-tutorial/


**Step 2**: Download the config files and the input files directly using the following link.

    ::

    	curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2-devel/tarballs/coam-on-stampede.tar.gz
        tar xvfz coam-on-stampede.tar.gz
        cd coam-on-stampede


**Step 3**: In the coam-on-stampede folder, a resource configuration file ``stampede.rcfg`` exists. Details and modifications required are as follows:

    .. note:: 
                For the purposes of this example, you require to change only:

                    * UNAME
                    * ALLOCATION

                The other parameters in the resource configuration are already set up to successfully execute the workload in this example.

    ::

        REMOTE_HOST = 'xsede.stampede'            # Label/Name of the Remote Machine
        UNAME       = 'username'                  # Username on the Remote Machine
        ALLOCATION  = 'TG-MCB090174'              # Allocation to be charged
        WALLTIME    = 60                          # Walltime to be requested for the pilot
        PILOTSIZE   = 16                          # Number of cores to be reserved
        WORKDIR     = None                        # Working directory on the remote machine
        QUEUE       = 'normal'                    # Name of the queue in the remote machine

        DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'


**Step 4**: In the coam-on-stampede folder, a workload configuration file ``cocoamber.wcfg`` exists. Details and modifications required are as follows:


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
        md_input_file           = './inp_files/mdshort.in'    # Entire path to MD Input file - Do not use $HOME or the likes
        minimization_input_file = './inp_files/min.in'        # Entire path to Minimization file - Do not use $HOME or the likes
        initial_crd_file        = './inp_files/penta.crd'     # Entire path to Coordinates file - Do not use $HOME or the likes
        top_file                = './inp_files/penta.top'     # Entire path to Topology file - Do not use $HOME or the likes
        logfile                 = 'coco.log'        # Name of the log file created by pyCoCo

        #-------------------------Analysis--------------------------
        grid                    = '5'               # Number of points along each dimension of the CoCo histogram
        dims                    = '3'               # The number of projections to consider from the input pcz file

        helper_scripts = './helper_scripts'


    .. note::
                
                All the parameters in the above example file are mandatory for amber-coco. There are no other parameters currently supported.

**Step 5**: You can find the executable script ```extasy_amber_coco.py``` in the coam-on-stampede folder.

**Now you are can run the workload using :**

If your shell is BASH,

    ::

        EXTASY_DEBUG=True RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' python extasy_amber_coco.py --RPconfig stampede.rcfg --Kconfig cocoamber.wcfg 2> extasy.log

If your shell is CSH,

    ::

        setenv EXTASY_DEBUG True
        setenv RADICAL_PILOT_VERBOSE 'debug'
        setenv SAGA_VERBOSE 'debug'
        python extasy_amber_coco.py --RPconfig stampede.rcfg --Kconfig cocoamber.wcfg |& tee extasy.log



Running on Archer
=================

Running using Example Workload Config and Resource Config
---------------------------------------------------------

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input
files:

    1. The resource configuration file sets the parameters of the HPC resource we want
       to run the workload on, in this case Archer.

    2. The workload configuration file defines the CoCo/Amber workload itself. The configuration file given in this example is strictly meant for the coco-amber usecase only.

**Step 1**: Create a new directory for the example,

    ::

        mkdir $HOME/extasy-tutorial/
        cd $HOME/extasy-tutorial/


**Step 2**: Download the config files and the input files directly using the following link.

    ::

    	curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2-devel/tarballs/coam-on-archer.tar.gz
        tar xvfz coam-on-archer.tar.gz
        cd coam-on-archer


**Step 3**: In the coam-on-archer folder, a resource configuration file ``archer.rcfg`` exists. Details and modifications required are as follows:

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


**Step 4**: In the coam-on-archer folder, a resource configuration file ``cocoamber.wcfg`` exists. Details and modifications required are as follows:

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
        md_input_file           = './inp_files/mdshort.in'    # Entire path to MD Input file - Do not use $HOME or the likes
        minimization_input_file = './inp_files/min.in'        # Entire path to Minimization file - Do not use $HOME or the likes
        initial_crd_file        = './inp_files/penta.crd'     # Entire path to Coordinates file - Do not use $HOME or the likes
        top_file                = './inp_files/penta.top'     # Entire path to Topology file - Do not use $HOME or the likes
        logfile                 = 'coco.log'        # Name of the log file created by pyCoCo

        #-------------------------Analysis--------------------------
        grid                    = '5'               # Number of points along each dimension of the CoCo histogram
        dims                    = '3'               # The number of projections to consider from the input pcz file

        helper_scripts = './helper_scripts'


    .. note::
                
                All the parameters in the above example file are mandatory for amber-coco. There are no other parameters currently supported.


**Step 5**: You can find the executable script ```extasy_amber_coco.py``` in the coam-on-archer folder.

**Now you are can run the workload using :**

If your shell is BASH,

    ::

        EXTASY_DEBUG=True RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' python extasy_amber_coco.py --RPconfig archer.rcfg --Kconfig cocoamber.wcfg 2> extasy.log


If your shell is CSH,

    ::

        setenv EXTASY_DEBUG True
        setenv RADICAL_PILOT_VERBOSE 'debug'
        setenv SAGA_VERBOSE 'debug'
        python extasy_amber_coco.py --RPconfig archer.rcfg --Kconfig cocoamber.wcfg |& tee extasy.log


Running on localhost
====================

The above two sections describes execution on XSEDE.Stampede and EPSRC.Archer, assuming you have access to these machines. This section describes the changes required to the EXISTING scripts in order to get CoCo-Amber running on your local machines (label to be used = ``local.localhost`` as in the generic examples).

**Step 1**: You might have already guessed the first step. You need to create a SingleClusterEnvironment object targetting the localhost machine. You can either directly make changes to the ``extasy_amber_coco.py`` script or create a separate resource configuration file and provide it as an argument.

**Step 2**: The MD tools require some tool specific environment variables to be setup (AMBERHOME, PYTHONPATH, GCC, GROMACS_DIR, etc). Along with this, you would require to set the PATH environment variable to point to the binary file (if any) of the MD tool. Once you determine all the environment variables to be setup, set them on the terminal and test it by executing the MD command (possibly for a sample case). For example, if you have amber installed in $HOME as $HOME/amber14. You probably have to setup AMBERHOME to $HOME/amber14 and append $HOME/amber14/bin to PATH. Please check official documentation of the MD tool.

**Step 3**: There are three options to proceed.

    * Once you tested the environment setup, next you need to add it to the particular kernel definition. You need to, first, locate the particular file to be modified. All the files related to EnsembleMD are located within the virtualenv (say "myenv"). Go into the following path: ``myenv/lib/python-2.7/site-packages/radical/ensemblemd/kernel_plugins/md``. This path contains all the kernels used for the MD examples. You can open the amber.py file and add an entry for local.localhost (in ``"machine_configs"``) as follows:

    .. parsed-literal::

        ..
        ..
        "machine_configs":
        {

            ..
            ..

            "local.localhost":
            {
                "pre_exec"    : ["export AMBERHOME=$HOME/amber14", "export PATH=$HOME/amber14/bin:$PATH"],
                "executable"  : ["sander"],
                "uses_mpi"    : False       # Could be True or False
            },

            ..
            ..

        }
        ..
        ..

    This would have to be repeated for all the kernels.

    * Another option is to perform the same above steps. But leave the ``"pre_exec"`` value as an empty list and set all the environment variables in your bashrc (``$HOME/.bashrc``). Remember that you would still need to set the executable as above.

    * The third option is to create your own kernel plugin as part of your user script. These avoids the entire procedure of locating the existing kernel plugin files. This would also get you comfortable in using kernels other than the ones currently available as part of the package. Creating your own kernel plugins are discussed `here <develop.html>`_


Understanding the Output of the Examples
========================================

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
