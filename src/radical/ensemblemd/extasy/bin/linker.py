import sys
import os
import subprocess

if __name__ =="__main__":
    path = sys.argv[1]
    files = os.listdir(path)
    kernel_type = sys.argv[2]
    kernel = sys.argv[3]
    module_path = sys.argv[4]

    os.environ["PATH"] += os.pathsep + module_path

    os.system('/bin/bash -l -c "module load gromacs"')

    for i in range(0,len(files)):
        os.system('/bin/bash -l -c "ln -s %s/%s ."'%(path,files[i]))
    os.system('/bin/bash -l -c "%s %s"' % (kernel_type,kernel))