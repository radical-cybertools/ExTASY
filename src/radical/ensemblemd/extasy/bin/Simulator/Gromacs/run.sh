#!/bin/bash

# this script was generated automatically by thread %(task)i
#default arguments - file_name=run.sh, directory_name=task directory, rank=task id, mdpfile_name, grofile_name, topfile_name,
# output_grofile_name, tprfile_name='topol.tpr', trrfile_name='traj.trr', edrfile_name='ener.edr'

#New arguments - grofile_name, mdpfile_name, topfile_name, output_grofile_name, tprfile_name ='topol.tpr'
# , trrfile_name='traj.trr', edrfile_name='ener.edr'

mdpfile_name=$1
grofile_name=$2
topfile_name=$3
output_grofile_name=$4
tprfile_name=topol.tpr
trrfile_name=traj.trr
edrfile_name=ener.edr


startgro=$grofile_name
tmpstartgro=tmpstart.gro
outgro=$output_grofile_name

natoms=$(sed -n '2p' $startgro)
nlines_per_frame=$((natoms+3))

#nlines=`wc -l %(directory_name)s/$startgro| cut -d' ' -f1`
nlines=`wc -l $startgro| cut -d' ' -f1`
nframes=$((nlines/nlines_per_frame))

PATH=$PATH:/opt/apps/intel13/mvapich2_1_9/gromacs/4.6.3/bin

rm -rf $outgro

for idx in `seq 1 $nframes`; do

  start=$(($nlines_per_frame*(idx-1)+1))
  end=$(($nlines_per_frame*idx))
  sed "$start"','"$end"'!d' $startgro > $tmpstartgro

  # gromacs preprocessing & MD
  grompp -f $mdpfile_name -c $tmpstartgro -p $topfile_name -o $tprfile_name 1>/dev/null 2>/dev/null
  mdrun -nt 1 -s $tprfile_name -o $trrfile_name -e $edrfile_name 1>/dev/null 2>/dev/null

  # store data
  cat confout.gro >> $outgro

done
