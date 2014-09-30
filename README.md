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


**Step 1:** Create the virtualenv:

```
virtualenv /tmp/ExTASY-tools/
source /tmp/ExTASY-tools/bin/activate
```

**Step 2:** Install ExTASY's dependencies:

```
pip install radical.pilot
pip install --upgrade git+https://github.com/radical-cybertools/radical.ensemblemd.mdkernels.git@master#egg=radical.ensemblemd.mdkernels
```

> **TODO OLE/VIVEK: CHANGE 'devel' to release tag in the line below!

**Step 3:** Install ExTASY:

```
pip install --upgrade git+https://github.com/radical-cybertools/ExTASY.git@devel#egg=radical.ensemblemd.extasy
```

Now you should be able to print the installed version of the ExTASY module:

```
python -c 'import radical.ensemblemd.extasy as extasy; print extasy.version'
```

**Installation is complete!**

==========

# 2. Running a Coco/Amber Workload 

> **[TODO Vivek: Improve paragraph below - hard to understand. Avoid 'jargon'. Don't reference things that are not defined yet, e.g. PILOTSIZE]**

This example allocates ``PILOTSIZE`` cores on ``REMOTE_HOST``. Once the core allocation request goes through the queue, there is no Preprocessor for these combination of kernels. The Simulator is loaded which transfers the required files (``.crd``, ``.top``, ``.in``) and performs the Amber simulation on the provided input. After all the simulations are done, the Analysis stage kicks in and performs analysis using the CoCo method. The output of the Analysis stage is fed back as the input of the Simulation in the next iteration.

> **[TODO Vivek: Put bullet points below into perspective?]**
> 
> * Number of CUs in the simulation stage = ``num_CUs``
> * Number of CUs in the analysis stage = ``1``
> * Total number of CUs in N iterations of ASA =`` N*(num_CUs + 1)`` 

## 2.1 Running on Stampede

### 2.1.1 Installing CoCo on Stampede

> You can skip this step if you have done this already.

CoCo is currently **not installed** on Stampede. In order to run the CoCo/Amber
example, you need to install it yourself. This also requires you to install **scipy 0.14** (or greater) using the Stampede **python/2.7.3** and **intel/13.0.2.146** modules. Please follow [THIS LINK](https://github.com/radical-cybertools/ExTASY/blob/devel/docs/scipy_installation_stampede_python_2_7_3.md) for installation instructions. 

Once you have installed numpy/scipy, double-check the version of scipy and numpy:

```
python -c "import scipy; scipy.__version__"
python -c "import numpy; numpy.__version__"
```

Now you can install CoCo itself. Log-on to Stampede check out the CoCo repository and install it:

```
cd $HOME
git clone https://bitbucket.org/extasy-project/coco.git
module load python
cd $HOME/coco
python setup.py install --user
```

### 2.1.2 Running the Example Workload

The ExTASY tool expects two input files:

1. The resource configuration file sets the parameters of the HPC resource we want to run the workload on, in this case **Stampede**.
2. The workload configuration file defines the CoCo/Amber workload itself.

**Step 1:** Create a new directory for the example:

```
mkdir $HOME/coam-on-stampede/
cd $HOME/coam-on-stampede/
```

**Step 2:** Create a new resource configuration file ``stampede.rcfg``:

(Download it [stampede.rcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/config/stampede.rcfg) directly.)

> Change the following values according to your needs:
> 
> * UNAME
> * ALLOCATION

```
REMOTE_HOST = 'stampede.tacc.utexas.edu'  # Label/Name of the Remote Machine
UNAME       = 'username'                  # Username on the Remote Machine
ALLOCATION  = 'TG-MCB090174'              # Allocation to be charged
WALLTIME    = 60                          # Walltime to be requested for the pilot
PILOTSIZE   = 64                          # Number of cores to be reserved
WORKDIR     = None                        # Working directory on the remote machine
QUEUE       = 'normal'                    # Name of the queue in the remote machine

DBURL       = 'mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/'        
```

**Step 3:** Download the sample input data:

```
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/coco_examples/mdshort.in
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/coco_examples/min.in
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/coco_examples/penta.crd
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/coco_examples/penta.top
```

**Step 4:** Create a new workload configuration file ``cocoamber.wcfg``:

(Download it [cocoamber.wcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/config/cocoamber.wcfg) directly.)

```
#-------------------------Applications----------------------
simulator                = 'Amber'
analyzer                 = 'CoCo'

#-------------------------General---------------------------
num_iterations          = 2  # Number of iterations of Simulation-Analysis
start_iter              = 0  # Iteration number with which to start
nreps = 8

#-------------------------Simulation-----------------------
num_cores_per_sim_cu    = 2
md_input_file           = './mdshort.in'
minimization_input_file = './min.in'
initial_crd_file        = './penta.crd'
top_file                = './penta.top'

#-------------------------Analysis--------------------------
grid                    = '5'
dims                    = '3'
frontpoints             = '8'
```

Now you are can run the workload:

```
extasy --RPconfig stampede.rcfg --Kconfig cocoamber.wcfg
```

<!-- 
===================================================================
===================================================================
-->

## 2.2 Running on Archer

> CoCo is already installed as a module on Archer so you don't need to install it yourself.

### 2.2.1 Running the Example Workload

The ExTASY tool expects two input files:

1. The resource configuration file sets the parameters of the HPC resource we want to run the workload on, in this case **Archer**.
2. The workload configuration file defines the CoCo/Amber workload itself.

**Step 1:** Create a new directory for the example:

```
mkdir $HOME/coam-on-archer/
cd $HOME/coam-on-archer/
```

**Step 2:** Create a new resource configuration file ``archer.rcfg``:

(Download it [archer.rcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/config/archer.rcfg) directly.)

> Change the following values according to your needs:
> 
> * UNAME
> * ALLOCATION

```
REMOTE_HOST = 'archer.ac.uk'              # Label/Name of the Remote Machine
UNAME       = 'username'                  # Username on the Remote Machine
ALLOCATION  = 'e290'                      # Allocation to be charged
WALLTIME    = 10                          # Walltime to be requested for the pilot
PILOTSIZE   = 24                          # Number of cores to be reserved
WORKDIR     = None                        # Working directory on the remote machine
QUEUE       = 'debug'                     # Name of the queue in the remote machine

DBURL       = 'mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/'        
```

**Step 3:** Download the sample input data:

```
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/coco_examples/mdshort.in
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/coco_examples/min.in
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/coco_examples/penta.crd
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/master/coco_examples/penta.top
```

**Step 4:** Create a new workload configuration file ``cocoamber.wcfg``:

> The file is identical with the one in 2.1 Running on Stampede.

(Download it [cocoamber.wcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/config/cocoamber.wcfg) directly.)



Now you can run the workload:

```
extasy --RPconfig archer.rcfg --Kconfig cocoamber.wcfg
```

<!-- 
===================================================================
===================================================================
-->
# 3. Runing a Gromacs/LSDMap Workload

> **[TODO Vivek: Improve paragraph below - hard to understand. Avoid 'jargon'.]**

This example allocates ``PILOTSIZE`` cores on ``REMOTE_HOST``. Once the pilot goes through the queue, the Preprocessor splits the ``input.gro`` file as defined by ``input_gro`` into
temporary smaller files based on ``num_CUs``. The Simulator is then launched which takes as input the temporary files, an ``mdp`` file and a ``top`` file and runs the MD. The output is aggregated into one ``gro`` file that is used during the Analysis phase. The Analyzer is then loaded which looks for a ``gro`` file as defined in ``tmp_grofile``
in the workload configuration.

> **[TODO Vivek: Put bullet points below into perspective?]**

> * Number of CUs in the simulation stage = ``num_CUs``
> * Number of CUs in the analysis stage = ``1``
> * Total number of CUs in N iterations of ASA = ``N*(num_CUs + 1)``

<!-- LSDMAP / STAMPEDE
===================================================================
===================================================================
-->
## 3.1 Running on Stampede

### 3.1.1 Installing LSDMap on Stampede

LSDMap is currently **not installed** on Stampede. In order to run the Gromacs/LSDMap
example, you need to install it yourself. This also requires you to install **scipy 0.10.0** (or greater) and **numpy 1.4.1** using the Stampede **python/2.7.6** and **intel/14.0.1.106** modules. Please follow [THIS LINK](https://github.com/radical-cybertools/ExTASY/blob/devel/docs/scipy_installation_stampede_python_2_7_6.md) for installation instructions. 

```
python -c "import scipy; scipy.__version__"
python -c "import numpy; numpy.__version__"
```

Now you can install LSDMap itself. Log-on to Stampede check out the LSDMap repository and install it:

```
module load -intel intel/14.0.1.106
module load python
git clone git://git.code.sf.net/p/lsdmap/git lsdmap
cd lsdmap
python setup.py install --user
```

**Installation is complete!** 

### 3.1.2 Running the Example Workload

The ExTASY tool expects two input files:

1. The resource configuration file sets the parameters of the HPC resource we want to run the workload on, in this case **Stampede**.
2. The workload configuration file defines the GROMACS/LSDMap workload itself.

**Step 1:** Create a new directory for the example:

```
mkdir $HOME/grlsd-on-stampede/
cd $HOME/grlsd-on-stampede/
```

**Step 2:** Create a new resource configuration file ``stampede.rcfg``:

> This file is identical with the resource configuration file used in "Running CoCo/Amber on Stampede"

(Download it [stampede.rcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/config/stampede.rcfg) directly.)

> Change the following values according to your needs:
> 
> * UNAME
> * ALLOCATION

**Step 3:** Download the sample input data:

```
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/gromacs_lsdmap_example/config.ini
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/gromacs_lsdmap_example/grompp.mdp
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/gromacs_lsdmap_example/input.gro
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/gromacs_lsdmap_example/topol.top
```

**Step 4:** Create a new workload configuration file ``gromacslsdmap.wcfg``:

(Download it [gromacslsdmap.wcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/config/gromacslsdmap.wcfg) directly.)

```
#-------------------------Applications----------------------
simulator             = 'Gromacs'
analyzer              = 'LSDMap'

#--------------------------General--------------------------------
num_CUs              = 64 #num of CUs
num_iterations       = 1
start_iter           = 0
nsave                = 2

#--------------------------Simulation--------------------------------
num_cores_per_sim_cu = 2
md_input_file        = './input.gro'
mdp_file             = './grompp.mdp'
top_file             = './topol.top'
ndx_file             = ''
grompp_options       = ''
mdrun_options        = ''
itp_file_loc         = ''
md_output_file       = 'tmp.gro'

#--------------------------Analysis----------------------------------
lsdm_config_file     = './config.ini'
num_runs             = 10000
w_file               = 'weight.w'
max_alive_neighbors  = ''
max_dead_neighbors   = ''

```
**Step 5a:** Install NumPy:

The LSDMap update stage currently requires a local installation of numpy. 

```
pip install numpy
```

**Step 5:** Run the workload:

```
extasy --RPconfig stampede.rcfg --Kconfig gromacslsdmap.wcfg
```

<!-- LSDMAP / ARCHER
===================================================================
===================================================================
-->
## 3.2 Running on Archer

### 3.2.1 Running the Example Workload

The ExTASY tool expects two input files:

1. The resource configuration file sets the parameters of the HPC resource we want to run the workload on, in this case **Archer**.
2. The workload configuration file defines the GROMACS/LSDMap workload itself.

**Step 1:** Create a new directory for the example:

```
mkdir $HOME/grlsd-on-archer/
cd $HOME/grlsd-on-archer/
```

**Step 2:** Create a new resource configuration file ``archer.rcfg``:

> The resource configuration file is identical with the one used in "Running CoCo/Amber on Archer"

(Download it [archer.rcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/config/archer.rcfg) directly.)

> Change the following values according to your needs:
> 
> * UNAME
> * ALLOCATION

**Step 3:** Download the sample input data:

```
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/gromacs_lsdmap_example/config.ini
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/gromacs_lsdmap_example/grompp.mdp
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/gromacs_lsdmap_example/input.gro
curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/gromacs_lsdmap_example/topol.top
```

**Step 4:** Create a new workload configuration file ``gromacslsdmap.wcfg``:

> The file is identical with the workload configuration file used in "Running GROMACS/LSDMap on Stampede"

(Download it [gromacslsdmap.wcfg](https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/config/gromacslsdmap.wcfg) directly.)

**Step 5a:** Install NumPy:

The LSDMap update stage currently requires a local installation of numpy. 

```
pip install numpy
```

**Step 5:** Run the workload:

```
extasy --RPconfig archer.rcfg --Kconfig gromacslsdmap.wcfg
```


































<!--
Setting up the Kernel configuration file : Gromacs-LSDMap
----------------------------------------------------------

As described before, the other input file to the tool is the file containing all required parameters for the
Kernel execution. The following are the parameters required for the Gromacs-LSDMap kernel combinations. An 
example/demo can be found in ``` /tmp/ExTASY/config/gromacs_lsdmap_config.py```.

----------------------------------------------------------General-------------------------------------------------------------------------

* num_CUs           : Number of Compute Units to be submitted to the pilot
* num_iterations    : Number of iterations of Simulation-Analysis
* nsave             : Number of iterations after which backup is to be created
* start_iter        : Iteration number with which to start

-----------------------------------------------------Simulation(Gromacs)--------------------------------------------------------------

* input_gro_loc & input_gro : location and name of the input(gro) file
* grompp_loc & grompp_name  : location and name of the grompp(mdp) file
* topol_loc & topol_name    : location and name of the topol(top) file
* tmp_grofile               : name of the intermediate file used as input for LSDMap
* ndxfile_name & ndxfile_loc: name and location of index file
* grompp_options            : grompp options to be added during runtime
* mdrun_options             : mdrun options to be added during runtime
* itpfile_loc               : location of itpfiles to be transfered

-------------------------------------------------------Analysis(LSDMap)---------------------------------------------------------------

* lsdm_config_loc & lsdm_config_name : location and name of the lsdm configuration file
* wfile     : name of the weight file to be used in LSDMap
* max_alive_neighbors : maximum alive neighbors to be considered during reweighting step
* max_dead_neighbors  : maximum dead neighbors to be considered during reweighting step

------------------------------------------------------------Update--------------------------------------------------------------------------

* num_runs : number of replicas

-------------------------------------------------------------Auto---------------------------------------------------------------------------

These parameters are automatically assigned based on the values above. These are mainly for the 
propagation of filenames throughout the tool.

* system_name
* outgrofile_name
* egfile 
* evfile 
* nearest_neighbor_file 
* num_clone_files 
-->



