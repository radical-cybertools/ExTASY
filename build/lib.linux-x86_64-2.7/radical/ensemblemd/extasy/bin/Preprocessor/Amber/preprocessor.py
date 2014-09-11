__author__ = 'vivek'

import imp
import time
import shutil
import os
import sys
import radical.pilot


def Preprocessing(Kconfig,umgr,cycle):

    if (cycle==0):
        print "Creating initial setup"

        exp_loc = Kconfig.exp_loc

        mdshort_loc = Kconfig.mdshort_loc
        mdshortfile = Kconfig.mdshortfile

        min_loc = Kconfig.min_loc
        minfile = Kconfig.minfile

        crd_loc = Kconfig.crd_loc
        crdfile = Kconfig.crdfile

        top_loc = Kconfig.top_loc
        topfile = Kconfig.topfile

        cudesc = radical.pilot.ComputeUnitDescription()
        cudesc.executable = '/bin/bash'
        cudesc.cores = 1
        cudesc.pre_exec = ['(test ! -d "%s" || rm %s -rf)'%(exp_loc,exp_loc),'mkdir %s'%(exp_loc),'cp %s %s %s %s cocoUi.py %s'%(mdshortfile,minfile,crdfile,topfile,exp_loc), 'cd %s'%exp_loc, '( test ! -d "rep0*" || rm rep0* -rf)' , 'mkdir rep00 rep01 rep02 rep03 rep04 rep05 rep06 rep07' ]
        cudesc.arguments = ['-l','-c','tee rep00/min0.crd rep01/min0.crd rep02/min0.crd rep03/min0.crd rep04/min0.crd rep05/min0.crd rep06/min0.crd rep07/min0.crd < %s > /dev/null' % crdfile]
        cudesc.input_data = ['%s/%s'%(mdshort_loc,mdshortfile),'%s/%s'%(min_loc,minfile),'%s/%s'%(crd_loc,crdfile),'%s/%s'%(top_loc,topfile),'%s/cocoUi.py'%os.path.dirname(os.path.realpath(__file__))]
        unit = umgr.submit_units(cudesc)

        unit.wait()