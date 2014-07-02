#!/bin/sh

prmfile=parameters
lsdm_prmfile=parameters_lsdm

sed -i 's/recovery=.*/recovery=0/g' $prmfile
sed -i 's/startime=.*/startime=0.0/g' $prmfile
sed -i 's/status_lsdmap=.*/status_lsdmap=0/g' $lsdm_prmfile

jobname=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 6 | head -n 1)
sed -i 's/#PBS.*-N.*/#PBS -N '"$jobname"'/g' run.pbs
