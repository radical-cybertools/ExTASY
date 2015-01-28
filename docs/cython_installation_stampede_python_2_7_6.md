Before installing scipy, you will have to install numpy, cython, BLAS + LAPACK. This is a one time procedure, i.e
it does not have to be done everytime you log into Stampede. Please use the same session/terminal during the 
entire installation to avoid possible errors.

Its better to create a different directories for each of the following packages.

Cython
------

```
module load -intel intel/14.0.1.106
module load python
wget cython.org/release/Cython-0.21.tar.gz
tar xvfz Cython-0.21.tar.gz
cd Cython-0.21
python setup.py install --user                  #make sure python/2.7.6 is being used
```

