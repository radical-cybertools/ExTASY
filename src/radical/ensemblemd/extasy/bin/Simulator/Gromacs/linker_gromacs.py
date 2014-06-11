__author__ = 'vivek'
import sys
import os
import subprocess

if __name__ =="__main__":
    path = sys.argv[1]
    grompp_name = sys.argv[2]
    topol_name = sys.argv[3]
    outgro_filename = sys.argv[4]
    os.system('/bin/bash -l -c "ln -s %s/%s ."'%(path,grompp_name))
    os.system('/bin/bash -l -c "ln -s %s/%s ."'%(path,topol_name))
    os.system('/bin/bash -l -c "run.sh %s %s %s %s"' % (grompp_name , 'start.gro', topol_name , outgro_filename))