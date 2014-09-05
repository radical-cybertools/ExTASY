This is an initial implementation of COCO and Amber with RP.

Since the COCO repository is a private repository(password required to clone). Log into Stampede, clone and install extasy.


```
cd $HOME
git clone https://<user-name>@bitbucket.org/extasy-project/coco.git
module load python
cd $HOME/coco
python setup.py install --user
```

Also install scipy 14 or greater on python 2.7.3.

```
cd
git clone git://github.com/scipy/scipy.git scipy
cd scipy
python setup.py install --user
```

> You will have to install numpy and cython as well before installing scipy. For other scipy dependencies 
> ```
> http://stackoverflow.com/questions/7496547/python-scipy-needs-blas
> ```

RP on Stampede
----------------------

```
cd
git clone https://github.com/radical-cybertools/radical.pilot.git
cd radical.pilot
python setup.py install --user
```

Temporary fixes in COCO
------------------------

* Indentation error in line 209 in src/extasy/pcz.py
* In cocoUI.py, change from argh to argparse. Comment/Remove the argh statements.

```
parser=argparse.ArgumentParser()
parser.add_argument('-g','--grid', type=int, default=10, help="The grid dimensions to consider in coco.")
parser.add_argument('-p','--projs', type=int, default=3, help='The number of projections to consider from the input pcz file in coco that will also correspond to the number of dimensions of the grid.')
parser.add_argument('-f','--frontpoints', type=int, default=None, help="The number of new frontier points to select through coco.")
parser.add_argument('-c','--cycle', type=int, help='This parameter will specify the cycle id.')
parser.add_argument('-v','--verbosity', nargs='?', help="Increase output verbosity.")
args=parser.parse_args()
```

* In cocoUI.py, change ```def main():``` to '''if __name__ == '__main__':```


Running the workload on Stampede
--------------------------------
```
cd
wget https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/coco/runme.py
wget https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/coco/postexec.py
export ALLOCATION_ID = ''          #only if you have multiple allocations
python runme.py
```

To repeat the workload, please delete the rep0* folders in $HOME/coco/examples/.



