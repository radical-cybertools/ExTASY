.. _installation:

************
Installation
************

This page describes the requirements and procedure to be followed to install the
ExTASY package.

   .. note:: Pre-requisites.The following are the minimal requirements to install the ExTASY module.

                * python >= 2.7
                * virtualenv >= 1.11
                * pip >= 1.5
                * Password-less ssh login to Stampede and/or Archer machine (`help <http://extasy.readthedocs.org/en/latest/pages/trouble.html#configuring-ssh-access>`_ )

The easiest way to install ExTASY is to create virtualenv. This way, ExTASY and its
dependencies can easily be installed in user-space without clashing with potentially
incompatible system-wide packages.

.. tip:: If the virtualenv command is not available, try the following set of commands,

    .. parsed-literal:: wget --no-check-certificate https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.11.tar.gz
                        tar xzf virtualenv-1.11.tar.gz
                        python virtualenv-1.11/virtualenv.py --system-site-packages $HOME/ExTASY-tools/
                        source $HOME/ExTASY-tools/bin/activate

**Step 1** : Create the virtualenv,

.. parsed-literal:: virtualenv $HOME/ExTASY-tools/

If your shell is BASH,

.. parsed-literal:: source $HOME/ExTASY-tools/bin/activate

If your shell is CSH,

Setuptools might not get installed with virtualenv and hence using pip would fail. Please look at `https://pypi.python.org/pypi/setuptools <https://pypi.python.org/pypi/setuptools>`_ for installation instructions.

.. parsed-literal:: source $HOME/ExTASY-tools/bin/activate.csh


**Step 2** : Install ExTASY,

.. parsed-literal:: pip install --upgrade git+https://github.com/radical-cybertools/ExTASY.git@extasy_0.1#egg=radical.ensemblemd.extasy


To install the development version (unstable),

.. parsed-literal:: pip install --upgrade git+https://github.com/radical-cybertools/ExTASY.git@extasy_0.1#egg=radical.ensemblemd.extasy

.. parsed-literal:: pip install --upgrade git+https://github.com/radical-cybertools/radical.ensemblemd.mdkernels.git@master#egg=radical.ensemblemd.mdkernels


Now you should be able to print the installed version of the ExTASY module using,

.. parsed-literal:: python -c 'import radical.ensemblemd.extasy as extasy; print extasy.version'

.. tip::   If your shell is CSH you would need to do,

    .. parsed-literal:: rehash

    This will reset the PATH variable to also point to the packages which were just installed.

**Installation is complete !**
