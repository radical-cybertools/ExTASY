#!/bin/bash



grompp  -n index.ndx # &> grompp_${RunID}.out
mdrun   #&> mdrun.out

