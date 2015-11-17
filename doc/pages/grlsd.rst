.. _grlsd:


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

.. code-block:: bash

        mkdir $HOME/extasy-tutorial/
        cd $HOME/extasy-tutorial/


**Step 2**: Download the config files and the input files directly using the following link.

.. code-block:: bash

        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2-devel/tarballs/grlsd-on-stampede.tar.gz
        tar xvfz grlsd-on-stampede.tar.gz
        cd grlsd-on-stampede


**Step 3**: In the grlsd-on-stampede folder, a resource configuration file ``stampede.rcfg`` exists. Details and modifications required are as follows:

    .. note:: 
                For the purposes of this example, you require to change only:

                    * UNAME
                    * ALLOCATION

                The other parameters in the resource configuration are already set up to successfully execute the workload in this example.

.. literalinclude:: ../../examples/groamcs_lsdmap/stampede.rcfg


**Step 4**: In the grlsd-on-stampede folder, a workload configuration file ``gromacslsdmap.wcfg`` exists. Details and modifications are as follows:


.. literalinclude:: ../../examples/gromacs_lsdmap/gromacslsdmap_on_stampede.wcfg

.. note:: 

        All the parameters in the above example file are mandatory for gromacs-lsdmap. If *ndxfile*, *grompp_options*, *mdrun_options* and *itp_file_loc* are not required, they should be set to None; but they still have to mentioned in the configuration file. There are no other parameters currently supported for these examples.


**Step 5**: You can find the executable script ```extasy_gromacs_lsdmap.py``` in the grlsd-on-stampede folder.

**Now you are can run the workload using :**

.. code-block:: bash

        python extasy_gromacs_lsdmap.py --RPconfig stampede.rcfg --Kconfig gromacslsdmap.wcfg



.. note:: Environment variable RADICAL_ENMD_VERBOSE is set to REPORT in the python script. This specifies the verbosity of the output. For more verbose output, you can use INFO or DEBUG.


.. note::
            Time to completion: ~13 mins (from the time job goes through LRMS)

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

.. code-block:: bash

        mkdir $HOME/extasy-tutorial/
        cd $HOME/extasy-tutorial/

**Step 2**: Download the config files and the input files directly using the following link.

.. code-block:: bash
    
        curl -k -O  https://raw.githubusercontent.com/radical-cybertools/ExTASY/extasy_0.2-devel/tarballs/grlsd-on-archer.tar.gz
        tar xvfz grlsd-on-archer.tar.gz
        cd grlsd-on-archer

**Step 3**: In the grlsd-on-archer folder, a resource configuration file ``archer.rcfg`` exists. Details and modifications required are as follows:


    .. note:: 
                For the purposes of this example, you require to change only:

                    * UNAME
                    * ALLOCATION

                The other parameters in the resource configuration are already set up to successfully execute the workload in this example.

.. literalinclude:: ../../examples/gromacs_lsdmap/archer.rcfg

**Step 4**: In the grlsd-on-archer folder, a workload configuration file ``gromacslsdmap.wcfg`` exists. Details and modifications required are as follows:

.. literalinclude:: ../../examples/gromacs_lsdmap/gromacslsdmap_on_archer.wcfg

.. note:: 

        All the parameters in the above example file are mandatory for gromacs-lsdmap. If *ndxfile*, *grompp_options*, *mdrun_options* and *itp_file_loc* are not required, they should be set to None; but they still have to mentioned in the configuration file. There are no other parameters currently supported.


**Step 5**: You can find the executable script ```extasy_gromacs_lsdmap.py``` in the grlsd-on-archer folder.

**Now you are can run the workload using :**

.. code-block:: bash

        python extasy_gromacs_lsdmap.py --RPconfig archer.rcfg --Kconfig gromacslsdmap.wcfg


.. note:: Environment variable RADICAL_ENMD_VERBOSE is set to REPORT in the python script. This specifies the verbosity of the output. For more verbose output, you can use INFO or DEBUG.

.. note::
            Time to completion: ~15 mins (from the time job goes through LRMS)
            

Running on localhost
====================

The above two sections describes execution on XSEDE.Stampede and EPSRC.Archer, assuming you have access to these machines. This section describes the changes required to the EXISTING scripts in order to get Gromacs-LSDMap running on your local machines (label to be used = ``local.localhost`` as in the generic examples).

**Step 1**: You might have already guessed the first step. You need to create a SingleClusterEnvironment object targetting the localhost machine. You can either directly make changes to the ``extasy_gromacs_lsdmap.py`` script or create a separate resource configuration file and provide it as an argument.

**Step 2**: The MD tools require some tool specific environment variables to be setup (``AMBERHOME``, ``PYTHONPATH``, ``GCC``, ``GROMACS_DIR``, etc). Along with this, you would require to set the ``PATH`` environment variable to point to the binary file (if any) of the MD tool. Once you determine all the environment variables to be setup, set them on the terminal and test it by executing the MD command (possibly for a sample case). For example, if you have gromacs installed in ``$HOME`` as ``$HOME/gromacs_5``. You probably have to setup ``GROMACS_DIR`` to ``$HOME/gromacs-5`` and append ``$HOME/gromacs-5/bin`` to ``PATH``. Please check official documentation of the MD tool.

**Step 3**: There are three options to proceed.

    * Once you tested the environment setup, next you need to add it to the particular kernel definition. You need to, first, locate the particular file to be modified. All the files related to EnsembleMD are located within the virtualenv (say "myenv"). Go into the following path: ``myenv/lib/python-2.7/site-packages/radical/ensemblemd/kernel_plugins/md``. This path contains all the kernels used for the MD examples. You can open the ``gromacs.py`` file and add an entry for local.localhost (in ``"machine_configs"``) as follows:

    .. parsed-literal::

        ..
        ..
        "machine_configs":
        {

            ..
            ..

            "local.localhost":
            {
                "pre_exec"    : ["export GROMACS_DIR=$HOME/gromacs-5", "export PATH=$HOME/gromacs-5/bin:$PATH"],
                "executable"  : ["mdrun"],
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

In the local machine, a "output" folder is created and at the end of every checkpoint intervel (=nsave) an "iter*" folder is created which contains the necessary files to start the next iteration.


For example, in the case of gromacs-lsdmap on stampede, for 4 iterations with nsave=2:

::

    grlsd-on-stampede$ ls
    output/  config.ini  gromacslsdmap.wcfg  grompp.mdp  input.gro  stampede.rcfg  topol.top

    grlsd-on-stampede/output$ ls
    iter1/  iter3/



The "iter*" folder will not contain any of the initial files such as the topology file, minimization file, etc since they already exist on the local machine. In gromacs-lsdmap, the "iter*" folder contains the coordinate file and weight file required in the next iteration. It also contains a logfile about the lsdmap stage of the current iteration.

::

    grlsd-on-stampede/output/iter1$ ls
    2_input.gro  lsdmap.log  weight.w



On the remote machine, inside the pilot-* folder you can find a folder called "staging_area". This location is used to exchange/link/move intermediate data. The shared data is kept in "staging_area/" and the iteration specific inputs/outputs can be found in their specific folders (="staging_area/iter*").

::

    $ cd staging_area/
    $ ls
    config.ini  gro.py   input.gro   iter1/  iter3/    post_analyze.py  reweighting.py   run.py     spliter.py
    grompp.mdp  gro.pyc  iter0/      iter2/  lsdm.py   pre_analyze.py   run_analyzer.sh  select.py  topol.top

