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

To install the Ensemble MD Toolkit Python modules in the virtual environment, run:

.. parsed-literal::	export ENMD_INSTALL_VERSION="devel"
					pip install --upgrade git+https://github.com/radical-cybertools/radical.ensemblemd.git@$ENMD_INSTALL_VERSION#egg=radical.ensemblemd


You can check the version of Ensemble MD Toolkit with the `ensemblemd-version` command-line tool.
.. parsed-literal:: ensemblemd-version


.. tip::   If your shell is CSH you would need to do,

    .. parsed-literal:: rehash

    This will reset the PATH variable to also point to the packages which were just installed.

**Installation is complete !**