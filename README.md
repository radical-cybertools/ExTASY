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
git clone -b devel https://github.com/radical-cybertools/ExTASY.git
cd ExTASY
python setup.py install
export PYTHONPATH=$PYTHONPATH:/tmp/ExTASY
```

To verify the installation, check the current version

```
python -c 'import radical.ensemblemd.extasy as extasy; print extasy.version'
```

USAGE
======


RP_config
-----------


Kernel_config
-----------



Running the workload
--------------------

To run the particular workload of your experiment. Setup the config_file and the parameters file and use the --workload argument

```
extasy --workload
```


