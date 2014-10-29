#!/bin/bash

# Load python/2.7.3
module load intel/13.0.2.146
module load python

#--------------------------------------------------------------------------------------------
# Cython -- Local installtion -- will get installed in .local/lib/python2.7/site-packages/  |
#--------------------------------------------------------------------------------------------
wget cython.org/release/Cython-0.21.tar.gz
tar xvfz Cython-0.21.tar.gz
cd Cython-0.21
python setup.py install --user
cd ..
# Remove Cython folders after installation
rm Cython-0.21* -rf
#--------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------
# Numpy -- Local installtion -- will get installed in .local/lib/python2.7/site-packages/  |
#--------------------------------------------------------------------------------------------
git clone git://github.com/numpy/numpy.git numpy
cd numpy
python setup.py install --user
cd ..
# Remove Numpy folders after installation
rm numpy -rf
#--------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------
# Scipy -- Local installtion -- will get installed in .local/lib/python2.7/site-packages/  |
#--------------------------------------------------------------------------------------------

# BLAS Installation
# ==================

mkdir -p src/
cd src/
wget http://www.netlib.org/blas/blas.tgz
tar xzf blas.tgz
cd BLAS
gfortran -O3 -std=legacy -m64 -fno-second-underscore -fPIC -c *.f
ar r libfblas.a *.o
ranlib libfblas.a
rm -rf *.o
export BLAS=$PWD/libfblas.a
cd ..

# LAPACK Installation
# ==================

wget http://www.netlib.org/lapack/lapack.tgz
tar xzf lapack.tgz
cd lapack-*/
cp INSTALL/make.inc.gfortran make.inc

# edit the make.inc file
perl -pi -e 's/frecursive/fPIC/g' make.inc

make lapacklib
make clean
export LAPACK=$PWD/liblapack.a            #assuming 3.5.0 was downloaded
cd ..

# Scipy Installation
# ==================

cd ..
git clone git://github.com/scipy/scipy.git scipy
cd scipy
python setup.py install --user
cd ..
# Remove Scipy, lapack and BLAS folders after installation
rm scipy src -rf
#--------------------------------------------------------------------------------------------

clear

echo "Numpy and Scipy Installation successful !"