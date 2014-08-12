This is an initial implementation of COCO and Amber with RP.

Since the COCO repository is a private repository(password required to clone). Log into Stampede, clone and install extasy.

Installing COCO on Stampede
---------------------------

```
cd $HOME
git clone https://<user-name>@bitbucket.org/extasy-project/coco.git $
module load python
cd $HOME/coco
python setup.py install --user
```

Virtualenv/RP on Stampede
----------------------

```
cd
curl -O https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.11.tar.gz
tar xvfz virtualenv-1.11.tar.gz
module load python
cd virtualenv-1.11
python virtualenv.py $HOME/rp
source $HOME/rp/bin/activate
pip install radical.pilot
```


Running the workload on Stampede
--------------------------------
```
cd
wget https://raw.githubusercontent.com/radical-cybertools/ExTASY/devel/coco/runme.py
wget https://github.com/radical-cybertools/ExTASY/blob/devel/coco/postexec.py
python runme.py
```



