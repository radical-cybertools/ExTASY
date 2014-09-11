__author__ = 'vivek'

<<<<<<< HEAD
=======
#from config.kernel_config import *
import imp
>>>>>>> origin/master
import time
import shutil
import os
import sys
<<<<<<< HEAD
import gro

def Preprocessing(Kconfig,umgr,i):

    p1 = time.time()

    if(i==0):
        grofile_name_loc = Kconfig.input_gro_loc
        grofile_name = Kconfig.input_gro
        if os.path.exists(grofile_name_loc + '/' + grofile_name) is True:
            shutil.copy(grofile_name_loc + '/' + grofile_name,os.path.dirname(os.path.realpath(__file__)))
        if os.path.exists(os.getcwd() + '/' + Kconfig.wfile):
            os.remove('%s/%s'%(os.getcwd(),Kconfig.wfile))
        if os.path.exists(os.getcwd() + '/backup'):
            shutil.rmtree('%s/backup' % os.getcwd())

    else:
        grofile_name='%s_%s'%(i,Kconfig.input_gro)

    num_tasks = Kconfig.num_CUs

=======
import coord_util.gro as gro

def Preprocessing(Kconfig,umgr):

    p1 = time.time()

    grofile_name_loc = Kconfig.input_gro_loc
    grofile_name = Kconfig.input_gro
    num_tasks = Kconfig.num_CUs

    if os.path.exists(grofile_name_loc + '/' + grofile_name) is True:
        shutil.copy(grofile_name_loc + '/' + grofile_name,os.path.dirname(os.path.realpath(__file__)))
>>>>>>> origin/master


    print 'Prepare grofiles..'

    grofile_obj = gro.GroFile(os.path.dirname(os.path.realpath(__file__)) + '/' + grofile_name)

    if grofile_obj.nruns<num_tasks:
        print "###ERROR: number of runs should be greater or equal to the number of tasks."
        sys.exit(1)

    nruns_per_task = [grofile_obj.nruns/num_tasks for _ in xrange(num_tasks)]
    nextraruns=grofile_obj.nruns%num_tasks

    for idx in xrange(nextraruns):
        nruns_per_task[idx] += 1

    if os.path.isdir('%s/temp' % os.getcwd()) is True:
        shutil.rmtree('%s/temp' % os.getcwd())
    os.mkdir('%s/temp' % os.getcwd())

    with open(grofile_obj.filename, 'r') as grofile:
        for idx in xrange(num_tasks):
            start_grofile_name =  os.getcwd() + '/temp/start%s.gro'%idx
            with open(start_grofile_name, 'w') as start_grofile:
                nlines_per_task = nruns_per_task[idx]*grofile_obj.nlines_per_run
                for jdx in xrange(nlines_per_task):
                    line=grofile.readline()
                    if line:
                        line = line.replace("\n", "")
                        print >> start_grofile, line
                    else:
                        break

    p2 = time.time()

    print 'Preprocessing time : ', (p2-p1)


