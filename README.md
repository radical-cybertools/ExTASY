Coupled Simulation-Analysis Execution (ExTASY)
===============================================

Provides a command line interface to run multiple Molecular Dynamics (MD) simulations, which can be coupled to an analysis tool. The coupled simulation-analysis execution pattern (aka ExTASY pattern) currently supports two examples: 
(a) Gromacs as the "Simulator" and LSDMap as the "Analyzer"; (b) AMBER as the simulation engine and COCO as the analyzer. Due to the plugin-based architecture, this execution pattern, will be 
expandable as to support more Simulators and Analyzers.


Requirements
============

* python >= 2.7
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
pip install --upgrade git+https://github.com/radical-cybertools/radical.pilot.git@master#egg=radical.pilot
pip install --upgrade git+https://github.com/radical-cybertools/radical.ensemblemd.mdkernels.git@master#egg=radical.ensemblemd.mdkernels
pip install --upgrade git+https://github.com/radical-cybertools/ExTASY.git@devel#egg=radical.ensemblemd.extasy
export PYTHONPATH=$PYTHONPATH:/tmp/ExTASY
```
> If you have multiple allocations on the same system, set the environment variable PROJECT_ID 
> to your allocation number 
>
> ```
> export PROJECT_ID = 'ABCXYZ123'
> ```

To verify the installation, check the current version

```
python -c 'import radical.ensemblemd.extasy as extasy; print extasy.version'
```

USAGE
======


RP_config
-----------

The RP_config file is used for defining the parameters related to Radical Pilot.

* UPreprocessor : The preprocessor to be used. Can be 'Gromacs' or 'Namd'
* USimulator    : The Simulator to be loaded. Can be 'Gromacs' or 'Namd'
* UAnalyzer     : The Analyzer to be loaded. Can be 'LSDMap' or 'CoCo'

* UNAME         : Username to access the remote machine
* REMOTE_HOST   : URL of remote machine
* WALLTIME      : Walltime for the complete job
* PILOTSIZE     : No. of cores to reserved for the entire job
* DBURL         : MongoDB URL


Kernel_config
-----------

The Kernel_config file is used for defining the parameters related to the Simulation and Analysis phases.

* num_sims                  : Number of CUs. The input.gro file is divided such that each CU gets equal number of molecules 
* num_iterations            : Number of times the entire Sim-Analysis chain has to be performed
* input_gro_loc, input_gro  : Location and name of the input file
* grompp_loc, grompp_name   : Location and name of the mdp file
* topol_loc, topol_name     : Location and name of the top file
* tmp_grofile               : Name of the temporary gro file
* outgrofile_name           : Name of the output file of the Simulation Stage
* sys                       : System name
* egfile                    : Name of the eigen vector file
* evfile                    : Name of the eigen value file
* nearest_neighbor_file     : Name of the nearest neighbour file 
* num_runs                  : Number of runs during Analysis stage
* num_clone_files           : Name of clone file


Running the tests
------------------



Running the workload
--------------------

To run the particular workload of your experiment. Setup the config_file and the parameters file and run extasy.

```
extasy
```


