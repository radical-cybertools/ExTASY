#!/bin/bash

<<<<<<< HEAD
nnout=$1
wfile=$2

lsdmap -f config.ini -c tmpha.gro -w $wfile -n $nnout
=======
outgro=$1
nnout=$2
wfile=$3

lsdmap -f config.ini -c $outgro -w $wfile -n $nnout
>>>>>>> origin/master




