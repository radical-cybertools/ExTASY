#!/bin/bash
if [ -e "start.gro" ]
then
echo "start.gro exists"
fi
if [ -e "run.sh" ]
then
echo "run.sh exists"
fi
if [ -e "grompp.mdp" ]
then
echo "grompp exists"
fi
if [ -e "topol.top" ]
then
echo "topol exists"
fi