**********
ExTASY 0.2
**********

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

.. parsed-literal::

    export ENMD_INSTALL_VERSION="master"
    virtualenv $HOME/EnMDToolkit
    source $HOME/EnMDToolkit/bin/activate
    pip install --upgrade git+https://github.com/radical-cybertools/radical.ensemblemd.git@$ENMD_INSTALL_VERSION#egg=radical.ensemblemd

You can check the version of Ensemble MD Toolkit with the `ensemblemd-version` command-line tool.

.. parsed-literal::

    ensemblemd-version
 

Running a Gromacs/LSDMap Workload
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

    2. The workload configuration file defines the GROMACS/LSDMap workload itself. The configuration file given in this example is strictly meant for the gromacs-lsdmap usecase only.

**Step 1** : Create a new directory for the example,

    ::

        mkdir $HOME/grlsd-on-stampede/
        cd $HOME/grlsd-on-stampede/



Configuring SSH Access
----------------------

From a terminal from your local machine, setup a key pair with your email address.

::
	$ ssh-keygen -t rsa -C "name@email.com"

	Generating public/private rsa key pair.
	Enter file in which to save the key (/home/user/.ssh/id_rsa): [Enter]
	Enter passphrase (empty for no passphrase): [Passphrase]
	Enter same passphrase again: [Passphrase]
	Your identification has been saved in /home/user/.ssh/id_rsa.
	Your public key has been saved in /home/user/.ssh/id_rsa.pub.
	The key fingerprint is:
	03:d4:c4:6d:58:0a:e2:4a:f8:73:9a:e8:e3:07:16:c8 your@email.ac.uk
	The key's randomart image is:
	+--[ RSA 2048]----+
	|    . ...+o++++. |
	| . . . =o..      |
	|+ . . .......o o |
	|oE .   .         |
	|o =     .   S    |
	|.    +.+     .   |
	|.  oo            |
	|.  .             |
	| ..              |
	+-----------------+


Next you need to transfer it to the remote machine.


To transfer to Stampede,

	::

		$cat ~/.ssh/id_rsa.pub | ssh username@stampede.tacc.utexas.edu 'cat - >> ~/.ssh/authorized_keys'


To transfer to Archer,

	::

		cat ~/.ssh/id_rsa.pub | ssh username@login.archer.ac.uk 'cat - >> ~/.ssh/authorized_keys'


# Mailing List

* Users : https://groups.google.com/forum/#!forum/extasy-project
* Developers : https://groups.google.com/forum/#!forum/extasy-devel

