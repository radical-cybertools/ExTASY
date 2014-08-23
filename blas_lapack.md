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

mkdir -p ~/src
cd ~/src/
wget http://www.netlib.org/lapack/lapack.tgz
tar xzf lapack.tgz
cd lapack-*/
cp INSTALL/make.inc.gfortran make.inc          # on Linux with lapack-3.2.1 or newer
```


edit the make.inc file by setting OPTS = -O2 -fPIC and NOOPT = -O0 -fPIC

```
make lapacklib
make clean
export LAPACK=~/src/lapack-3.5.0/liblapack.a
```