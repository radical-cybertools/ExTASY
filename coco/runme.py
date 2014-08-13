__author__ = 'vivek'
import os
import sys
import radical.pilot

DBURL = "mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017"
RCONF  = ["https://raw.github.com/radical-cybertools/radical.pilot/master/configs/xsede.json"]

#------------------------------------------------------------------------------
#
def pilot_state_cb(pilot, state):
    """pilot_state_change_cb() is a callback function. It gets called very
    time a ComputePilot changes its state.
    """
    print "[Callback]: ComputePilot '{0}' state changed to {1}.".format(
        pilot.uid, state)

    if state == radical.pilot.states.FAILED:
        sys.exit(1)

#------------------------------------------------------------------------------
#
def unit_state_change_cb(unit, state):
    """unit_state_change_cb() is a callback function. It gets called very
    time a ComputeUnit changes its state.
    """
    print "[Callback]: ComputeUnit '{0}' state changed to {1}.".format(
        unit.uid, state)
    if state == radical.pilot.states.FAILED:
        print "            Log: %s" % unit.log[-1]


#------------------------------------------------------------------------------
#

if __name__ == '__main__':
    print "Starting pilot-job..."
    session = radical.pilot.Session(database_url=DBURL)
    print "Session UID: {0} ".format(session.uid)

    # Add an ssh identity to the session.
    cred = radical.pilot.Context('ssh')
    cred.user_id = 'vivek91'
    session.add_context(cred)

    # Add a Pilot Manager. Pilot managers manage one or more ComputePilots.
    pmgr = radical.pilot.PilotManager(session=session)

    pmgr.register_callback(pilot_state_cb)

    # Start a pilot at the remote host as per the configs
    pdesc = radical.pilot.ComputePilotDescription()
    pdesc.resource = 'stampede.tacc.utexas.edu'
    pdesc.runtime = 20
    pdesc.cores = 16
    pdesc.project = os.getenv('ALLOCATION_ID','None')

    pilot = pmgr.submit_pilots(pdesc)

    print "Pilot UID       : {0} ".format(pilot.uid )


    umgr = radical.pilot.UnitManager(session=session, scheduler=radical.pilot.SCHED_DIRECT_SUBMISSION)
    # Register our callback with the UnitManager. This callback will get
    # called every time any of the units managed by the UnitManager
    # change their state.
    umgr.register_callback(unit_state_change_cb)

    # Add the previously created ComputePilot to the UnitManager.
    umgr.add_pilots(pilot)


    #------------------------------------------------------------------------------
    #

    #
    # All simulations use the same mdin file.
    #
    dict = {}
    dict['crdfile'] = 'penta.crd'
    dict['topfile'] = 'penta.top'
    dict['mdin']    = 'mdshort.in'
    dict['minin']   = 'min.in'

    # set number of cycles, and number of replicates
    maxcycles = 10
    nreps = 8
    coco_loc = '$HOME/coco/'
    #
    # Main loop begins here:
    #rep00/md0.crd
    for cycle in range(maxcycles):
        dict['cycle'] = str(cycle)
        if cycle == 0:
    #
    # cycle 0: we begin with a single coordinate and topology file.
    # Copy it into the separate rep0? directories ready to run the MD simulations.
    #
            print 'Cycle : %s' % cycle
            print "Creating initial setup"
            #cp = script.Script()
            #for rep in range(nreps):
            #    dict['rep'] = str(rep)
            ##    dict['path'] = os.getcwd()
             #   cp.append('cp {crdfile} {path}/rep0{rep}/md0.crd'.format(**dict))
            #    cp.run('tcsh -f {}')

            cudesc = radical.pilot.ComputeUnitDescription()
            cudesc.executable = '/bin/bash'
            cudesc.cores = 1
            cudesc.pre_exec = ['cd %s/examples' % coco_loc, '( test -d "rep0*" || rm rep0* -rf)' , 'mkdir rep00 rep01 rep02 rep03 rep04 rep05 rep06 rep07' ]
            cudesc.arguments = ['-l','-c','tee rep00/md0.crd rep01/md0.crd rep02/md0.crd rep03/md0.crd rep04/md0.crd rep05/md0.crd rep06/md0.crd rep07/md0.crd < %s > /dev/null' % dict['crdfile']]

            unit = umgr.submit_units(cudesc)

            unit.wait()

        else:

            print 'Cycle : %s' % cycle
            print 'Submitting COCO Compute Unit'

            cudesc = radical.pilot.ComputeUnitDescription()
            cudesc.executable = '/bin/bash'
            cudesc.cores = 16
            cudesc.pre_exec = ['module load python','cp postexec.py %s/examples'% coco_loc,'cd %s/examples' % coco_loc,'module load mpi4py','module load amber']
            cudesc.arguments = ['-l','-c','python cocoUi.py --grid 5 --projs 3 --frontpoints 8 --cycle %s -vvv' % cycle ]
            cudesc.input_data = ['postexec.py']
            cudesc.post_exec = ['python postexec.py %s %s' % (nreps,cycle)]
            cudesc.mpi = True
            #cs.append('mpiexec -mca btl ^openib -n 4 python cocoUi.py --grid 5 --projs 3  --frontpoints 8 --cycle {cycle} -vvv'.format(**dict))
            #cs.append('python cocoUi.py --grid 5 --projs 3  --frontpoints 8 --cycle {cycle} -vvv'.format(**dict))

            unit = umgr.submit_units(cudesc)

            unit.wait()

            #try:
            #    cs.run('tcsh -f {}')
            #except IOError as e:
            #    print "I/O error({0}): {1}".format(e.errno, e.strerror)

            #print 'creating new crd files...'
            #for rep in range(nreps):
            #    dict['rep'] = rep
            #    dict['path'] = os.getcwd()
            #    tl = script.Script()
            #    tl.append('source leaprc.ff99SB')
            #    tl.append('x = loadpdb {path}/rep0{rep}/pentaopt{cycle}.pdb'.format(**dict))
            #    tl.append('saveamberparm x {path}/rep0{rep}/delete.me {path}/rep0{rep}/min{cycle}.crd'.format(**dict))
            #    tl.append('quit')
            #    tl.run('tleap -f {}')
#
    # now run the MD
    #
        compute_units = []
        for i in range(nreps):
            print "Submitting new 'pmemd' compute unit"
            dict['rep'] = str(i)
            dict['path'] = coco_loc + '/examples'
            # output files that need to be transferred back: *.mdcrd

            step_1 = 'pmemd -O -i {path}/{minin} -o {path}/rep0{rep}/min{cycle}.out -inf {path}/rep0{rep}/min{cycle}.inf -r {path}/rep0{rep}/md{cycle}.crd -p {path}/{topfile} -c {path}/rep0{rep}/min{cycle}.crd -ref {path}/rep0{rep}/min{cycle}.crd'.format(**dict)
            step_2 = 'pmemd -O -i {path}/{mdin} -o {path}/rep0{rep}/md{cycle}.out -inf {path}/rep0{rep}/md{cycle}.inf -x {path}/rep0{rep}/md{cycle}.mdcrd -r {path}/rep0{rep}/md{cycle}.rst -p {path}/{topfile} -c {path}/rep0{rep}/md{cycle}.crd'.format(**dict)

            cu = radical.pilot.ComputeUnitDescription()
            cu.executable = "/bin/bash"
            cu.cores      = 1
            cu.pre_exec = ['module load TACC ','module load amber','cd %s/examples' % coco_loc]
            cu.arguments  = ['-l', '-c', " %s && %s" % (step_1, step_2)]
            compute_units.append(cu)

        units = umgr.submit_units(compute_units)
        umgr.wait_units()

        #print 'running md cycle {cycle}'.format(**dict)
        #try:
    #    out = md0.run("tcsh -f {}")
        #except IOError as e:
    #    print "I/O error({0}): {1}".format(e.errno, e.strerror)

    session.close()
