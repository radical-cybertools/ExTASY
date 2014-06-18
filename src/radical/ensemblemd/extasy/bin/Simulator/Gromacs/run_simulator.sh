#!/bin/bash

path=$1
grompp_name=$2
topol_name=$3
outgro_filename=$4

module load python
ln -s $path/$grompp_name .
ln -s $path/$topol_name .
. run.sh $grompp_name start.gro $topol_name $outgro_filename

