# ExTASY 0.2
============

ExTASY 0.2 is a tool to build and run multiple Molecular Dynamics simulations 
which can be coupled to an Analysis stage. This forms a simulation-analysis loop 
which can be made to iterate multiple times. It uses EnsembleMD Toolkit, which
provides the individual building blocks to create each of the simulation and 
analysis stages and to execute the workflow in heterogeneous machines.

# Introduction
==============

ExTASY is a tool to run multiple Molecular Dynamics simulations which can be coupled to an Analysis stage. This forms a simulation-analysis loop which can be made to iterate multiple times. It uses a pilot framework, namely Radical Pilot to run a large number of these ensembles concurrently on most of the commonly used supercomputers. The complications of resource allocation, data management and task execution are performed using Radical Pilot and handled by the ExTASY.

ExTASY provides a command line interface, that along with specific configuration files, keeps the user’s job minimal and free of the underlying execution methods and data management that is resource specific.

The coupled simulation-analysis execution pattern (aka ExTASY pattern) currently supports two usecases:

* Gromacs as the “Simulator” and LSDMap as the “Analyzer”
* AMBER as the “Simulator” and CoCo as the “Analyzer”


# Installation
==============

To install the Ensemble MD Toolkit Python modules in a virtual environment,
open a terminal and run:

```
export ENMD_INSTALL_VERSION="master"
virtualenv $HOME/EnMDToolkit
source $HOME/EnMDToolkit/bin/activate
pip install --upgrade git+https://github.com/radical-cybertools/radical.ensemblemd.git@$ENMD_INSTALL_VERSION#egg=radical.ensemblemd
```

You can check the version of Ensemble MD Toolkit with the `ensemblemd-version` command-line tool.
```
    ensemblemd-version
```
 

Running a Gromacs/LSDMap Workload
=================================

This section will discuss details about the execution phase. The input to the tool
is given in terms of a resource configuration file and a workload configuration file.
The execution is started based on the parameters set in these configuration files.

Running on Stampede
-------------------

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input
files:

* The resource configuration file sets the parameters of the HPC resource we want to run the workload on, in this case Stampede.

* The workload configuration file defines the GROMACS/LSDMap workload itself. The configuration file given in this example is strictly meant for the gromacs-lsdmap usecase only.


**Step 1** : Download the config files and the input files directly using the following link.

```
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/tarballs/grlsd-on-stampede.tar.gz
tar xvfz grlsd-on-stampede.tar.gz
```

**Step 2** : In the grlsd-on-stampede folder, a resource configuration file ``stampede.rcfg`` exists. Details and modifications required are as follows:

For the purposes of this example, you require to change only:

* UNAME
* ALLOCATION

The other parameters in the resource configuration are already set up to successfully execute the workload in this example.

```
REMOTE_HOST = 'stampede.tacc.utexas.edu'  # Label/Name of the Remote Machine
UNAME       = 'username'                  # Username on the Remote Machine
ALLOCATION  = 'TG-MCB090174'              # Allocation to be charged
WALLTIME    = 60                          # Walltime to be requested for the pilot
PILOTSIZE   = 16                          # Number of cores to be reserved
WORKDIR     = None                        # Working directory on the remote machine
QUEUE       = 'normal'                    # Name of the queue in the remote machine

DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'
```

**Step 3** : In the grlsd-on-stampede folder, a workload configuration file ``gromacslsdmap.wcfg`` exists. Details and modifications are as follows:

```
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
```

All the parameters in the above example file are mandatory for gromacs-lsdmap. If *ndxfile*, *grompp_options*, *mdrun_options* and *itp_file_loc* are not required, they should be set to None; but they still have to mentioned in the configuration file. There are no other parameters currently supported.

**Step 4**: Download the script using:

```
cd grlsd-on-stampede/
curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/example/gromacs_lsdmap/extasy_gromacs_lsdmap.py
```

**Now you can run the workload using:**

```
python extasy_gromacs_lsdmap.py --RPconfig stampede.rcfg --Kconfig gromacslsdmap.wcfg
```

Running on Archer
-----------------

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input
files:

    1. The resource configuration file sets the parameters of the HPC resource we want to
       run the workload on, in this case Archer.

    2. The workload configuration file defines the GROMACS/LSDMap workload itself. The configuration file given in this example is strictly meant for the gromacs-lsdmap usecase only.


**Step 1** : Download the config files and the input files directly using the following link.

    ::

        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/tarballs/grlsd-on-archer.tar.gz
        tar xvfz grlsd-on-archer.tar.gz

**Step 2** : In the grlsd-on-archer folder, a resource configuration file ``archer.rcfg`` exists. Details and modifications required are as follows:

    .. note:: 
                For the purposes of this example, you require to change only:

                    * UNAME
                    * ALLOCATION

                The other parameters in the resource configuration are already set up to successfully execute the workload in this example.

    ::

        REMOTE_HOST = 'archer.ac.uk'  # Label/Name of the Remote Machine
        UNAME       = 'username'                  # Username on the Remote Machine
        ALLOCATION  = 'e290'              		  # Allocation to be charged
        WALLTIME    = 60                          # Walltime to be requested for the pilot
        PILOTSIZE   = 16                          # Number of cores to be reserved
        WORKDIR     = None                        # Working directory on the remote machine
        QUEUE       = 'standard'                    # Name of the queue in the remote machine

        DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'


**Step 3** : In the grlsd-on-archer folder, a workload configuration file ``gromacslsdmap.wcfg`` exists. Details and modifications are as follows:


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

**Step 4**: Download the script using:

	::
		cd grlsd-on-archer/
		curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/example/gromacs_lsdmap/extasy_gromacs_lsdmap.py

**Now you can run the workload using:**

	::

		python extasy_gromacs_lsdmap.py --RPconfig archer.rcfg --Kconfig gromacslsdmap.wcfg


Running a Amber/CoCo Workload
=================================

This section will discuss details about the execution phase. The input to the tool
is given in terms of a resource configuration file and a workload configuration file.
The execution is started based on the parameters set in these configuration files.

Running on Stampede
-------------------

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input
files:

    1. The resource configuration file sets the parameters of the HPC resource we want to
       run the workload on, in this case Stampede.

    2. The workload configuration file defines the Amber/CoCo workload itself. The configuration file given in this example is strictly meant for the gromacs-lsdmap usecase only.


**Step 1** : Download the config files and the input files directly using the following link.

    ::

        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/tarballs/coam-on-stampede.tar.gz
        tar xvfz coam-on-stampede.tar.gz

**Step 2** : In the grlsd-on-stampede folder, a resource configuration file ``stampede.rcfg`` exists. Details and modifications required are as follows:

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


**Step 3** : In the coam-on-stampede folder, a workload configuration file ``cocoamber.wcfg`` exists. Details and modifications are as follows:


    ::

        #-------------------------Applications----------------------
		simulator                = 'Amber'          # Simulator to be loaded
		analyzer                 = 'CoCo'           # Analyzer to be loaded

		#-------------------------General---------------------------
		num_iterations          = 2                 # Number of iterations of Simulation-Analysis
		start_iter              = 0                 # Iteration number with which to start
		num_CUs 		= 16                # Number of tasks or Compute Units
		nsave			= 2		    # Iterations after which output is transferred to local machine

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

		#-------------------------Misc--------------------------
		misc_loc = './misc_files'                  # Location of miscellaneous files

**Step 4**: Download the script using:

	::
		cd coam-on-stampede/
		curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/example/amber-coco/extasy_amber_coco.py

**Now you can run the workload using:**

	::

		python extasy_amber_coco.py --RPconfig stampede.rcfg --Kconfig cocoamber.wcfg

Running on Archer
-----------------

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input
files:

    1. The resource configuration file sets the parameters of the HPC resource we want to
       run the workload on, in this case Archer.

    2. The workload configuration file defines the Amber/CoCo workload itself. The configuration file given in this example is strictly meant for the gromacs-lsdmap usecase only.


**Step 1** : Download the config files and the input files directly using the following link.

    ::

        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/tarballs/coam-on-archer.tar.gz
        tar xvfz coam-on-archer.tar.gz

**Step 2** : In the coam-on-archer folder, a resource configuration file ``archer.rcfg`` exists. Details and modifications required are as follows:

    .. note:: 
                For the purposes of this example, you require to change only:

                    * UNAME
                    * ALLOCATION

                The other parameters in the resource configuration are already set up to successfully execute the workload in this example.

    ::

        REMOTE_HOST = 'archer.ac.uk'  # Label/Name of the Remote Machine
        UNAME       = 'username'                  # Username on the Remote Machine
        ALLOCATION  = 'e290'              		  # Allocation to be charged
        WALLTIME    = 60                          # Walltime to be requested for the pilot
        PILOTSIZE   = 16                          # Number of cores to be reserved
        WORKDIR     = None                        # Working directory on the remote machine
        QUEUE       = 'standard'                    # Name of the queue in the remote machine

        DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'


**Step 3** : In the grlsd-on-archer folder, a workload configuration file ``cocoamber.wcfg`` exists. Details and modifications are as follows:


    ::

        #-------------------------Applications----------------------
		simulator                = 'Amber'          # Simulator to be loaded
		analyzer                 = 'CoCo'           # Analyzer to be loaded

		#-------------------------General---------------------------
		num_iterations          = 2                 # Number of iterations of Simulation-Analysis
		start_iter              = 0                 # Iteration number with which to start
		num_CUs 		= 16                # Number of tasks or Compute Units
		nsave			= 2		    # Iterations after which output is transferred to local machine

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

		#-------------------------Misc--------------------------
		misc_loc = './misc_files'                  # Location of miscellaneous files

**Step 4**: Download the script using:

	::
		cd coam-on-archer/
		curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2/example/amber-coco/extasy_amber_coco.py

**Now you can run the workload using:**

	::

		python extasy_amber_coco.py --RPconfig archer.rcfg --Kconfig cocoamber.wcfg



# Mailing List

* Users : https://groups.google.com/forum/#!forum/extasy-project
* Developers : https://groups.google.com/forum/#!forum/extasy-devel

