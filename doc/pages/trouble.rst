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



Error: Permission denied (publickey,keyboard-interactive) in AGENT.STDERR
---------------------------------------------------------------------------

The Pilot does not start running and goes to the 'Done' state directly from 'PendingActive'. Please check the AGENT.STDERR file for  "Permission denied (publickey,keyboard-interactive)" .

	::

		Permission denied (publickey,keyboard-interactive).
		kill: 19932: No such process

You require to setup passwordless, intra-node SSH access. Although this is default in most HPC clusters, this might not be the case always.

On the head-node, run:

	::

		cd ~/.ssh/
		ssh-keygen -t rsa

**Do not enter a passphrase**. The result should look like this:

	::

		enerating public/private rsa key pair.
		Enter file in which to save the key (/home/e290/e290/oweidner/.ssh/id_rsa):
		Enter passphrase (empty for no passphrase):
		Enter same passphrase again:
		Your identification has been saved in /home/e290/e290/oweidner/.ssh/id_rsa.
		Your public key has been saved in /home/e290/e290/oweidner/.ssh/id_rsa.pub.
		The key fingerprint is:
		73:b9:cf:45:3d:b6:a7:22:72:90:28:0a:2f:8a:86:fd oweidner@eslogin001

Next, you need to add this key to the authorized_keys file.

	::

		cat id_rsa.pub >> ~/.ssh/authorized_keys

This should be all. Next time you run radical.pilot, you shouldn’t see that error message anymore.





Error: Couldn't create new session
-----------------------------------

If you get an error similar to,

::

	An error occurred: Couldn't create new session (database URL 'mongodb://extasy:extasyproject@extasy-db.epcc.ac.uk/radicalpilot' incorrect?): [Errno -2] Name or service not known
	Exception triggered, no session created, exiting now...

This means no session was created, mostly due to error in the MongoDB URL that is present in the resource configuration file. Please check the URL that you have used. If the URL is correct, you should check the system on which the MongoDB is hosted.


Error: Prompted for unkown password
------------------------------------

If you get an error similar to,

::

	An error occurred: prompted for unknown password (username@stampede.tacc.utexas.edu's password: ) (/experiments/extasy/local/lib/python2.7/site-packages/saga/utils/pty_shell_factory.py +306 (_initialize_pty)  :  % match))	

You should check the username that is present in the resource configuration file. If the username is correct, you should check if you have a passwordless login set up for the target machine. You can check this by simply attempting a login to the target machine, if this attempt requires a password, you need to set up a passwordless login to use ExTASY. 


Error: Pilot has FAILED. Can't recover
---------------------------------------

If you get an error similar to,

::

	ExTASY version :  0.1.3-beta-15-g9e16ce7
	Session UID: 55102e9023769c19e7c8a84e 
	Pilot UID       : 55102e9123769c19e7c8a850 
	[Callback]: ComputePilot '55102e9123769c19e7c8a850' state changed to Launching.
	Loading kernel configurations from /experiments/extasy/lib/python2.7/site-packages/radical/ensemblemd/mdkernels/configs/mmpbsa.json
	Loading kernel configurations from /experiments/extasy/lib/python2.7/site-packages/radical/ensemblemd/mdkernels/configs/coco.json
	Loading kernel configurations from /experiments/extasy/lib/python2.7/site-packages/radical/ensemblemd/mdkernels/configs/namd.json
	Loading kernel configurations from /experiments/extasy/lib/python2.7/site-packages/radical/ensemblemd/mdkernels/configs/lsdmap.json
	Loading kernel configurations from /experiments/extasy/lib/python2.7/site-packages/radical/ensemblemd/mdkernels/configs/amber.json
	Loading kernel configurations from /experiments/extasy/lib/python2.7/site-packages/radical/ensemblemd/mdkernels/configs/gromacs.json
	Loading kernel configurations from /experiments/extasy/lib/python2.7/site-packages/radical/ensemblemd/mdkernels/configs/sleep.json
	Loading kernel configurations from /experiments/extasy/lib/python2.7/site-packages/radical/ensemblemd/mdkernels/configs/test.json
	Preprocessing stage ....
	[Callback]: ComputePilot '55102e9123769c19e7c8a850' state changed to Failed.
	#######################
	##       ERROR       ##
	#######################
	Pilot 55102e9123769c19e7c8a850 has FAILED. Can't recover.
	Pilot log: [<radical.pilot.logentry.Logentry object at 0x7f41f8043a10>, <radical.pilot.logentry.Logentry object at 0x7f41f8043610>, <radical.pilot.logentry.Logentry object at 0x7f41f80433d0>, <radical.pilot.logentry.Logentry object at 0x7f41f8043750>, <radical.pilot.logentry.Logentry object at 0x7f41f8043710>, <radical.pilot.logentry.Logentry object at 0x7f41f8043690>]
	Execution was interrupted
	Closing session, exiting now ...


This generally means either the Allocation ID or Queue name present in the resource configuration file is incorrect. If this is not the case, please re-run the experiment with the environment variables EXTASY_DEBUG=True, SAGA_VERBOSE=DEBUG, RADICAL_PILOT_VERBOSE=DEBUG. Example,

:: 

	EXTASY_DEBUG=True SAGA_VERBOSE=DEBUG RADICAL_PILOT_VERBOSE=DEBUG extasy --RPconfig stampede.rcfg --Kconfig gromacslsdmap.wcfg 2> output.log

This should generate a more verbose output. You may look at this verbose output for errors or create a ticket with this log `here <https://github.com/radical-cybertools/ExTASY/issues>`_ )


Couldn't send packet: Broken pipe
---------------------------------

If you get an error similar to,

::

	2015:03:30 16:05:07 radical.pilot.MainProcess: [DEBUG   ] read : [   19] [  159] ( ls /work/e290/e290/e290ib/radical.pilot.sandbox/pilot-55196431d7bf7579ecc ^H3f080/unit-551965f7d7bf7579ecc3f09b/lsdmap.log\nCouldn't send packet: Broken pipe\n)
	2015:03:30 16:05:08 radical.pilot.MainProcess: [ERROR   ] Output transfer failed: read from process failed '[Errno 5] Input/output error' : (s   --:-- ETA/home/h012/ibethune/testlsdmap2/input.gro     100%  105KB 104.7KB/s   00:00
	sftp>  ls /work/e290/e290/e290ib/radical.pilot.sandbox/pilot-55196431d7bf7579ecc ^H3f080/unit-551965f7d7bf7579ecc3f09b/lsdmap.log
	Couldn't send packet: Broken pipe

This is mostly because of an older version of sftp/scp being used. This can be fixed by setting an environment variable ``SAGA_PTY_SSH_SHAREMODE`` to ``no``.

::
	
	export SAGA_PTY_SSH_SHAREMODE=no

	

