# ExTASY Coupled Simulation-Analysis Execution
==============================================

Provides a command line interface to run multiple Molecular Dynamics (MD) simulations, which can be coupled to an analysis tool. The coupled simulation-analysis execution pattern (aka ExTASY pattern) currently supports two examples: 
(a) Gromacs as the "Simulator" and LSDMap as the "Analyzer"; (b) AMBER as the "Simulator" and COCO as the "Analyzer". Due to the plugin-based architecture, this execution pattern, will be 
expandable as to support more Simulators and Analyzers.

### Table of Contents

* **1. Installation**
* **2. Running a Coco/Amber Workload**
* **2.1 ... on Stampede**
* **2.2 ... on Archer**
* **3. Running a Gromacs/LSDMap Workload**
* **3.1 ... on Stampede**
* **3.2 ... on Archer**
* **4.0 Troubleshooting**


# 1. Installation

> **!! Requirements !!**
>
> The following are the minimal requirements to install the ExTASY module.
> 
> * python >= 2.7
> * virtualenv >= 1.11
> * pip >= 1.5
> * Password-less ssh login to **Stampede** and/or **Archer** machine
>   (see e.g., http://www.linuxproblem.org/art_9.html)


The easiest way to install ExTASY is to create virtualenv. This way, ExTASY and 
its dependencies can easily be installed in user-space without clashing with 
potentially incompatible system-wide packages. 

> If the virtualenv command is not availble (e.g., on Stampede):
>
> ```
> wget --no-check-certificate https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.9.tar.gz
> tar xzf virtualenv-1.9.tar.gz
> python virtualenv-1.9/virtualenv.py --system-site-packages $HOME/ExTASY-tools/
> source $HOME/ExTASY-tools/
> ```


**Step 1:** Create the virtualenv:

```
virtualenv $HOME/ExTASY-tools/
```

If your shell is **BASH**:

```
source $HOME/ExTASY-tools/bin/activate 
```

If your shell is **CSH**:

```
source $HOME/ExTASY-tools/bin/activate.csh 
```

**Step 2:** Install ExTASY's dependencies:

```
pip install radical.pilot
pip install --upgrade git+https://github.com/radical-cybertools/radical.ensemblemd.mdkernels.git@master#egg=radical.ensemblemd.mdkernels
```

**Step 3:** Install ExTASY:

```
pip install --upgrade git+https://github.com/radical-cybertools/ExTASY.git@master#egg=radical.ensemblemd.extasy
```

Now you should be able to print the installed version of the ExTASY module:

```
python -c 'import radical.ensemblemd.extasy as extasy; print extasy.version'
```

If your shell is **CSH**:

```
rehash 
```
This will reset the PATH variable to also point to the packages which were just installed.


**Installation is complete!**


==========

# 2. Running a Coco/Amber Workload 

  This section will discuss details about the execution phase. The input to the tool is given in terms of
  a resource configuration file and a workload configuration file. The execution is started based on the parameters set in
  these configuration files. 

## 2.1 Running on Stampede

> CoCo is already installed on Stampede so you don't need to install it yourself.

### 2.1.1 Running the Example Workload

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input files:

1. The resource configuration file sets the parameters of the HPC resource we want to run the workload on, in this case **Stampede**.
2. The workload configuration file defines the CoCo/Amber workload itself.

**Step 1:** Create a new directory for the example:

```
mkdir $HOME/coam-on-stampede/
cd $HOME/coam-on-stampede/
```

**Step 2:** Create a new resource configuration file ``stampede.rcfg``:

(Download it [stampede.rcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/coam-on-stampede/stampede.rcfg) directly.)

> Change the following values according to your needs:
> 
> * UNAME
> * ALLOCATION

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

**Step 3:** Download the sample input data:

```
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-stampede/mdshort.in
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-stampede/min.in
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-stampede/penta.crd
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-stampede/penta.top
```

**Step 4:** Create a new workload configuration file ``cocoamber.wcfg``:

(Download it [cocoamber.wcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/coam-on-stampede/cocoamber.wcfg
) directly.)

```
#-------------------------Applications----------------------
simulator                = 'Amber'          # Simulator to be loaded
analyzer                 = 'CoCo'           # Analyzer to be loaded

#-------------------------General---------------------------
num_iterations          = 4                 # Number of iterations of Simulation-Analysis
start_iter              = 0                 # Iteration number with which to start
num_CUs 		= 16                # Number of tasks or Compute Units
nsave			= 2		    # Iterations after which output is transfered to local machine

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

```

Now you are can run the workload:

```
RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' extasy --RPconfig stampede.rcfg --Kconfig cocoamber.wcfg 2> extasy.log
```

A **sample output** with expected callbacks and simulation/analysis can be found at [here](https://github.com/radical-cybertools/ExTASY/tree/master/sample_output_logs/coam-on-stampede)

-------------------------------------------------
|           Stage --->> | Simulation | Analysis |
|-----------------------|------------|----------|
|Expected TTC/iteration |   30-35 s  |  25-30s  |
-------------------------------------------------
<!-- 
===================================================================
===================================================================
-->

## 2.2 Running on Archer

> CoCo is already installed as a module on Archer so you don't need to install it yourself.

### 2.2.1 Running the Example Workload

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input files:

1. The resource configuration file sets the parameters of the HPC resource we want to run the workload on, in this case **Archer**.
2. The workload configuration file defines the CoCo/Amber workload itself.

**Step 1:** Create a new directory for the example:

```
mkdir $HOME/coam-on-archer/
cd $HOME/coam-on-archer/
```

**Step 2:** Create a new resource configuration file ``archer.rcfg``:

(Download it [archer.rcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/coam-on-archer/archer.rcfg) directly.)

> Change the following values according to your needs:
> 
> * UNAME
> * ALLOCATION

```
REMOTE_HOST = 'archer.ac.uk'              # Label/Name of the Remote Machine
UNAME       = 'username'                  # Username on the Remote Machine
ALLOCATION  = 'e290'                      # Allocation to be charged
WALLTIME    = 60                          # Walltime to be requested for the pilot
PILOTSIZE   = 24                          # Number of cores to be reserved
WORKDIR     = None                        # Working directory on the remote machine
QUEUE       = 'standard'                  # Name of the queue in the remote machine

DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'        
```

**Step 3:** Download the sample input data:

```
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-archer/mdshort.in
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-archer/min.in
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-archer/penta.crd
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/coam-on-archer/penta.top
```

**Step 4:** Create a new workload configuration file ``cocoamber.wcfg``:

(Download it [cocoamber.wcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/coam-on-archer/cocoamber.wcfg) directly.)


```
#-------------------------Applications----------------------
simulator                = 'Amber'          # Simulator to be loaded
analyzer                 = 'CoCo'           # Analyzer to be loaded

#-------------------------General---------------------------
num_iterations          = 2                 # Number of iterations of Simulation-Analysis
start_iter              = 0                 # Iteration number with which to start
num_CUs 		= 8                # Number of tasks or Compute Units
nsave			= 1		    # Iterations after which output is transfered to local machine

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
```


Now you can run the workload:

```
RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' extasy --RPconfig archer.rcfg --Kconfig cocoamber.wcfg 2> extasy.log
```

A **sample output** with expected callbacks and simulation/analysis can be found at [here](https://github.com/radical-cybertools/ExTASY/tree/master/sample_output_logs/coam-on-archer)

-------------------------------------------------
|           Stage --->> | Simulation | Analysis |
|-----------------------|------------|----------|
|Expected TTC/iteration |  60-100 s  | 150-200s |
-------------------------------------------------

There are two stages in the execution phase - Simulation and Analysis. Execution starts with any Preprocessing that 
might be required on the input data and then moves to Simulation stage. In the Simulation stage, a number of tasks (num_CUs)
are launched to execute on the target machine. The number of tasks set to execute depends on the **PILOTSIZE, num_CUs, 
num_cores_per_sim_cu**, the number of tasks in execution state simultaneously would be **PILOTSIZE/num_cores_per_sim_cu**.
As each task attains 'Done' (completed) state, the remain tasks are scheduled till all the **num_CUs** tasks are completed.
 
This is followed by the Analysis stage, one task is scheduled on the target machine which takes all the cores as the 
PILOTSIZE to perform the analysis and returns the data required for the next iteration of the Simulation stage. As can
be seen, per iteration, there are **(num_CUs+1)** tasks executed.



<!-- 
===================================================================
===================================================================
-->



# 3. Runing a Gromacs/LSDMap Workload

This section will discuss details about the execution phase. The input to the tool is given in terms of
a resource configuration file and a workload configuration file. The execution is started based on the parameters set in
these configuration files. 


<!-- LSDMAP / STAMPEDE
===================================================================
===================================================================
-->

## 3.1 Running on Stampede

> LSDMap is already installed on Stampede so you don't need to install it yourself.


### 3.1.1 Running the Example Workload

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input files:

1. The resource configuration file sets the parameters of the HPC resource we want to run the workload on, in this case **Stampede**.
2. The workload configuration file defines the GROMACS/LSDMap workload itself.

**Step 1:** Create a new directory for the example:

```
mkdir $HOME/grlsd-on-stampede/
cd $HOME/grlsd-on-stampede/
```

**Step 2:** Create a new resource configuration file ``stampede.rcfg``:

(Download it [stampede.rcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/grlsd-on-stampede/stampede.rcfg) directly.)


> Change the following values according to your needs:
> 
> * UNAME
> * ALLOCATION


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


**Step 3:** Download the sample input data:

```
curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/grlsd-on-stampede/config.ini
curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/grlsd-on-stampede/grompp.mdp
curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/grlsd-on-stampede/input.gro
curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/grlsd-on-stampede/topol.top
```

**Step 4:** Create a new workload configuration file ``gromacslsdmap.wcfg``:

(Download it [gromacslsdmap.wcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/grlsd-on-stampede/gromacslsdmap.wcfg) directly.)

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

**Step 5:** Run the workload:

```
RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' extasy --RPconfig stampede.rcfg --Kconfig gromacslsdmap.wcfg 2> extasy.log
```

A **sample output** with expected callbacks and simulation/analysis can be found at [here](https://github.com/radical-cybertools/ExTASY/tree/master/sample_output_logs/grlsd-on-stampede)

-------------------------------------------------
|           Stage --->> | Simulation | Analysis |
|-----------------------|------------|----------|
|Expected TTC/iteration |  50-100 s  |  ~30s    |
-------------------------------------------------


<!-- LSDMAP / ARCHER
===================================================================
===================================================================
-->
## 3.2 Running on Archer

> LSDMap is already installed as a module on Archer so you don't need to install it yourself.


### 3.2.1 Running the Example Workload

This section is to be done entirely on your **laptop**. The ExTASY tool expects two input files:

1. The resource configuration file sets the parameters of the HPC resource we want to run the workload on, in this case **Archer**.
2. The workload configuration file defines the GROMACS/LSDMap workload itself.

**Step 1:** Create a new directory for the example:

```
mkdir $HOME/grlsd-on-archer/
cd $HOME/grlsd-on-archer/
```

**Step 2:** Create a new resource configuration file ``archer.rcfg``:

(Download it [archer.rcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/grlsd-on-archer/archer.rcfg) directly.)

> Change the following values according to your needs:
> 
> * UNAME
> * ALLOCATION

```
REMOTE_HOST = 'archer.ac.uk'              # Label/Name of the Remote Machine
UNAME       = 'username'                  # Username on the Remote Machine
ALLOCATION  = 'e290'                      # Allocation to be charged
WALLTIME    = 60                          # Walltime to be requested for the pilot
PILOTSIZE   = 24                          # Number of cores to be reserved
WORKDIR     = None                        # Working directory on the remote machine
QUEUE       = 'standard'                  # Name of the queue in the remote machine

DBURL       = 'mongodb://extasy:extasyproject@extasy-db.epcc.ed.ac.uk/radicalpilot'
```


**Step 3:** Download the sample input data:

```
curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/grlsd-on-archer/config.ini
curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/grlsd-on-archer/grompp.mdp
curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/grlsd-on-archer/input.gro
curl -k -O https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/input_files/grlsd-on-archer/topol.top
```

**Step 4:** Create a new workload configuration file ``gromacslsdmap.wcfg``:

(Download it [gromacslsdmap.wcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/config_files/grlsd-on-archer/gromacslsdmap.wcfg) directly.)


```
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


```


**Step 5:** Run the workload:

```
RADICAL_PILOT_VERBOSE='debug' SAGA_VERBOSE='debug' extasy --RPconfig archer.rcfg --Kconfig gromacslsdmap.wcfg 2> extasy.log
```

A **sample output** with expected callbacks and simulation/analysis can be found at [here](https://github.com/radical-cybertools/ExTASY/tree/master/sample_output_logs/grlsd-on-archer)

-------------------------------------------------
|           Stage --->> | Simulation | Analysis |
|-----------------------|------------|----------|
|Expected TTC/iteration |  200-350 s |  ~30s    |
-------------------------------------------------


There are two stages in the execution phase - Simulation and Analysis. Execution starts with any Preprocessing that 
might be required on the input data and then moves to Simulation stage. In the Simulation stage, a number of tasks (num_CUs)
are launched to execute on the target machine. The number of tasks set to execute depends on the **PILOTSIZE, num_CUs, 
num_cores_per_sim_cu**, the number of tasks in execution state simultaneously would be **PILOTSIZE/num_cores_per_sim_cu**.
As each task attains 'Done' (completed) state, the remain tasks are scheduled till all the **num_CUs** tasks are completed.
 
This is followed by the Analysis stage, one task is scheduled on the target machine which takes all the cores as the 
PILOTSIZE to perform the analysis and returns the data required for the next iteration of the Simulation stage. As can
be seen, per iteration, there are **(num_CUs+1)** tasks executed.

# 4. Troubleshooting

## Execution fails with "Couldn't read packet: Connection reset by peer" 

You encounter the following error when running any of the extasy workflows:

```
...
#######################
##       ERROR       ##
#######################
Pilot 54808707f8cdba339a7204ce has FAILED. Can't recover.
Pilot log: [u'Pilot launching failed: Insufficient system resources: Insufficient system resources: read from process failed \'[Errno 5] Input/output error\' : (Shared connection to stampede.tacc.utexas.edu closed.\n)
...
```

TO fix this, create a file `~/.saga/cfg` in your home directory and add the following two lines:

```
[saga.utils.pty]
ssh_share_mode = no
```

This switches the SSH transfer layer into "compatibility" mode which should address the "Connection reset by peer" problem. 
