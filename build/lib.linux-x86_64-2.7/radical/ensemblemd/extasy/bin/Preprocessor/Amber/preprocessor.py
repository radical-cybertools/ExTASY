__author__ = 'vivek'

import imp
import time
import shutil
import os
import sys
import radical.pilot


def Preprocessing(Kconfig_url,umgr):

    Kconfig = imp.load_source('Kconfig',Kconfig_url)

    from Kconfig import *

    print 'Cycle : 0'
    print "Creating initial setup"

    cudesc = radical.pilot.ComputeUnitDescription()
    cudesc.executable = '/bin/bash'
    cudesc.cores = 1
    cudesc.pre_exec = ['(test ! -d "%s" || rm %s -rf)'%(exp_loc,exp_loc),'mkdir %s'%(exp_loc),'cp %s %s %s %s cocoUi.py %s'%(mdshortfile,minfile,crdfile,topfile,exp_loc), 'cd %s'%exp_loc, '( test ! -d "rep0*" || rm rep0* -rf)' , 'mkdir rep00 rep01 rep02 rep03 rep04 rep05 rep06 rep07' ]
    cudesc.arguments = ['-l','-c','tee rep00/md0.crd rep01/md0.crd rep02/md0.crd rep03/md0.crd rep04/md0.crd rep05/md0.crd rep06/md0.crd rep07/md0.crd < %s > /dev/null' % crdfile]
    cudesc.input_data = ['%s/%s'%(mdshort_loc,mdshortfile),'%s/%s'%(min_loc,minfile),'%s/%s'%(crd_loc,crdfile),'%s/%s'%(top_loc,topfile),'%s/cocoUi.py'%os.path.dirname(os.path.realpath(__file__))]
    unit = umgr.submit_units(cudesc)

    unit.wait()