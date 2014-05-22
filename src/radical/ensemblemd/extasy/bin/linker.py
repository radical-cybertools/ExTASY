import sys
import os
import subprocess

if __name__ =="__main__":
    path = sys.argv[1]
    files = os.listdir(path)
    kernel_type = sys.argv[2]
    kernel = sys.argv[3]

    proc = subprocess.Popen(["which grompp"], stdout=subprocess.PIPE, shell=True)
    (which_path, err) = proc.communicate()
    print "path : ", which_path

    os.environ["PATH"] += os.pathsep + which_path

    for i in range(0,len(files)):
        os.system('/bin/bash -l -c "ln -s %s/%s ."'%(path,files[i]))
    os.system('/bin/bash -l -c "%s %s"' % (kernel_type,kernel))