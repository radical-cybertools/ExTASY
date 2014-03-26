import sys
import os

if __name__ =="__main__":
    path = sys.argv[1]
    files = os.listdir(path)
    kernel = sys.argv[2]
    for i in range(0,len(files)):
        os.system('/bin/bash -l -c "ln -s %s/%s ."'%(path,files[i]))
    os.system('/bin/bash -l -c "python %s"'%kernel)