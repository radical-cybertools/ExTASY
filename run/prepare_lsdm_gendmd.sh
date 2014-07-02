#!/bin/bash

set -e

##----option parser------

usage()
{
cat << EOF
usage: `basename $0` -n <nthreads> -p <prmfile> -x <xyzfile> -w <wfile> -m <nnfile>
This script is intended to prepare LSDMap input files:
EOF
}

while getopts "h?p:x:w:n:m:" opt
do
  case $opt in
    h|\?) usage; exit 0;;
    p) prmfile=$OPTARG;;
    x) xyzfile=$OPTARG;;
    w) wfile=$OPTARG;;
    n) nthreads=$OPTARG;;
    m) nnfile=$OPTARG;;
    \?)echo "Invalid option: -$OPTARG"; exit 1;;
  esac
done

if [ -z "$prmfile" ]; then
  echo -e "###Error: LSDMap parameter file is required! \n"
  usage
  exit 1
elif [ ! -f ${prmfile} ]; then
    echo "###Error: prmfile not found: ${prmfile}"
    exit 1
fi

if [ -z "$xyzfile" ]; then
  echo -e "###Error: xyzfile is required! \n"
  usage
  exit 1
elif [ ! -f ${xyzfile} ]; then
    echo -e "###Error: xyzfile not found: ${xyzfile}"
    exit 1
fi

if [ -z "$nnfile" ]; then
  echo -e "nnfile name not provided (-n option)!"
  echo -e "save nearest neighbors into data.nn.\n"
  nnfile=data.nn
fi

source $prmfile


## ---------------------------------

  # A) build up files for completion

rm -rf rmsd neighbor localscale input err
mkdir -p rmsd neighbor localscale input err

finalfile=neighbor/finalize.sh

echo "cat neighbor/${xyzfile}_neighbor_9* > neighbor/${xyzfile}_neighbor" > ${finalfile}
echo "rm -f neighbor/${xyzfile}_neighbor_9*" >> ${finalfile}

if [ $k -ne 0 ]; then
    echo "cat neighbor/${xyzfile}_eps_w_9*" \> ${xyzfile}_eps_w >> ${finalfile}
    echo "rm neighbor/${xyzfile}_eps_w_9*" >> ${finalfile}
    echo "cat neighbor/${xyzfile}_eps_9*" \> ${xyzfile}_eps >> ${finalfile}
    echo "rm neighbor/${xyzfile}_eps_9*" >> ${finalfile}
fi

echo "cat neighbor/${xyzfile}_nneighbor_9* > $nnfile" >> ${finalfile}
echo "rm neighbor/${xyzfile}_nneighbor_9*" >> ${finalfile}

chmod +x ${finalfile}

finalfile=localscale/finalize.sh

echo "cat localscale/${xyzfile}_eps_1* > ${xyzfile}_eps" > ${finalfile}
echo "rm localscale/${xyzfile}_eps_1*" >> ${finalfile}

chmod +x ${finalfile}

if [ $status_lsdmap -eq 1 ]; then
  if [ -z "${wfile}" ]; then
    echo -e "###Error: wfile not provided while status_lsdmap = 1!\n"
    usage 1
    exit
  elif [ ! -f "${wfile}" ]; then
    echo -e "###Error: wfile not found: ${wfile}"
    exit 1
  fi
fi


 # B) build up input file for neighbor search

npoints=`head -1 $xyzfile |awk '{print $1}'`
file_eps=${xyzfile}_eps_cste

echo $xyzfile > rmsd_neighbor.input
echo '1 ' $npoints >> rmsd_neighbor.input
echo $neighbor_number $cutoff_nneighbor >> rmsd_neighbor.input
echo $k >> rmsd_neighbor.input
echo $status_lsdmap $wfile >> rmsd_neighbor.input

 # C) build up input file for LSDMap computation

echo $status_lsdmap $status_localscale > wlsdmap.input
echo $npoints >> wlsdmap.input
echo ${xyzfile}_rmsd >> wlsdmap.input
if [ $status_lsdmap -eq 1 ]; then
  echo $wfile >> wlsdmap.input
else
  echo >> wlsdmap.input 
fi
echo ${xyzfile}_dif >> wlsdmap.input
echo 0.0 >> wlsdmap.input
if [ $status_localscale -eq 1 ] && [ $k -eq 0 ]; then
    echo $file_eps $eps_column_id >> wlsdmap.input
elif [ $status_localscale -eq 1 ] && [ $k -gt 0 ]; then
    echo $file_eps 1 >> wlsdmap.input
else
    echo $constant_eps >> wlsdmap.input
fi

 # D) write input files for local scale if needed

if [ $status_localscale -eq 1 ] && [ $k -eq 0 ]; then

norder=`python -c "from math import ceil;print int(ceil(float(${npoints})/${npoints_core}))"`
cmdfile=input/${xyzfile}.cmd
rm -rf $cmdfile

for ((i=0;i<$norder;i++));
do
    nstart=$(($i*${npoints_core}+1))
    if [ $(($i+1)) -eq $norder ] ; then
        nend=${npoints}
    else
        nend=$((($i+1)*${npoints_core}))
    fi
    # write input
    input=input/${xyzfile}_$(($i+1000)).input
    echo ${xyzfile} > $input
    echo ${xyzfile}_neighbor >> $input
    echo $nstart $nend >> $input
    echo $(($i+1000)) >> $input
    echo $neighbor_number $mds_dimension $mds_start $mds_step >> $input
    echo $cutoff_start $cutoff_step $cutoff_number >> $input
    echo $ncore >> $input
    # write command
    echo "mpiexec -n $nthreads -cpus-per-proc 4 p_local_mds < ${input} > ${xyzfile}_lmds_$(($i+1000)).log" >> $cmdfile
done
fi
