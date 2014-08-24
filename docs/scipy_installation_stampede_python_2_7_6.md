Before installing scipy, you will have to install numpy, cython, BLAS + LAPACK. This is a one time procedure, i.e
it does not have to be done everytime you wish to you Stampede. Please use the same session/terminal during the 
entire installation to avoid possible errors.

Cython
------

```
module load -intel intel/14.0.1.106
module load python
wget cython.org/release/Cython-0.20.2.tar.gz
cd Cython-0.20.2
python setup.py install --user                  #make sure python/2.7.6 is being used
```

Numpy
-----

```
wget https://pypi.python.org/packages/source/n/numpy/numpy-1.8.2.tar.gz#md5=cdd1a0d14419d8a8253400d8ca8cba42
tar xvfz numpy-1.8.2.tar.gz
cd numpy-1.8.2
python setup.py install --user                  #make sure python/2.7.6 is being used
```

BLAS
-----

```
mkdir -p ~/src/
cd ~/src/
wget http://www.netlib.org/blas/blas.tgz
tar xzf blas.tgz
cd BLAS
gfortran -O3 -std=legacy -m64 -fno-second-underscore -fPIC -c *.f
ar r libfblas.a *.o
ranlib libfblas.a
rm -rf *.o
export BLAS=~/src/BLAS/libfblas.a
```


LAPACK
-------

```
mkdir -p ~/src
cd ~/src/
wget http://www.netlib.org/lapack/lapack.tgz
tar xzf lapack.tgz
cd lapack-*/
cp INSTALL/make.inc.gfortran make.inc
```

edit the make.inc file to change two variables to ``` OPTS = -O2 -fPIC ``` and ``` NOOPT = -O0 -fPIC ```

```
make lapacklib
make clean
export LAPACK=~/src/lapack-3.5.0/liblapack.a            #assuming 3.5.0 was downloaded
```

Scipy
------

```
wget https://pypi.python.org/packages/source/s/scipy/scipy-0.14.0.tar.gz#md5=d7c7f4ccf8b07b08d6fe49d5cd51f85d
tar xvfz scipy-0.14.0.tar.gz
cd scipy-0.14.0
python setup.py install --user              #make sure python/2.7.6 is being used
```