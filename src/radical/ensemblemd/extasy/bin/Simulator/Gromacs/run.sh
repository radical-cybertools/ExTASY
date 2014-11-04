#!/bin/bash


mdpfile_name=$1
grofile_name=$2
topfile_name=$3
output_grofile_name=$4
N=$5
tprfile_name=topol.tpr
trrfile_name=traj.trr
edrfile_name=ener.edr

if [ -n "$grompp_options" ]; then
    grompp_options=$grompp_options
else
    grompp_options=''
fi

if [ -n "$mdrun_options" ]; then
    mdrun_options=$mdrun_options
else
    mdrun_options=''
fi

if [ -n "$ndxfile" ]; then
    ndxfile_option="-n "$ndxfile
else
    ndxfile_option=''
fi

startgro=$grofile_name
tmpstartgro=tmpstart.gro
outgro=$output_grofile_name

natoms=$(sed -n '2p' $startgro)
nlines_per_frame=$((natoms+3))

#nlines=`wc -l %(directory_name)s/$startgro| cut -d' ' -f1`
nlines=`wc -l $startgro| cut -d' ' -f1`
nframes=$((nlines/nlines_per_frame))

rm -rf $outgro

for idx in `seq 1 $nframes`; do

  start=$(($nlines_per_frame*(idx-1)+1))
  end=$(($nlines_per_frame*idx))
  sed "$start"','"$end"'!d' $startgro > $tmpstartgro

  # gromacs preprocessing & MD
  grompp $grompp_options $ndxfile_option -f $mdpfile_name -c $tmpstartgro -p $topfile_name -o $tprfile_name 1>/dev/null 2>/dev/null
  mdrun -nt $N $mdrun_options -s $tprfile_name -o $trrfile_name -e $edrfile_name 1>/dev/null 2>/dev/null

  # store data
  cat confout.gro >> $outgro

done

