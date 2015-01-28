.. _trouble:

***************
Troubleshooting
***************

Some issues that you might face during the execution are discussed here.


Execution fails with "Couldn't read packet: Connection reset by peer"
---------------------------------------------------------------------

You encounter the following error when running any of the extasy workflows:

::

    ...
    #######################
    ##       ERROR       ##
    #######################
    Pilot 54808707f8cdba339a7204ce has FAILED. Can't recover.
    Pilot log: [u'Pilot launching failed: Insufficient system resources: Insufficient system resources: read from process failed \'[Errno 5] Input/output error\' : (Shared connection to stampede.tacc.utexas.edu closed.\n)
    ...

TO fix this, create a file ``~/.saga/cfg`` in your home directory and add the following two lines:

::

    [saga.utils.pty]
    ssh_share_mode = no

This switches the SSH transfer layer into "compatibility" mode which should address the "Connection reset by peer" problem.