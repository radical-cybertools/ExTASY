#!/home/jp43/modules/Python-2.7.3/bin/python

# save new walkers from ncopies file and input database and update Boltzmann weights from ncopies file and file of weights
# option max_alive_neighbors used to specify the maximum number of alive neighbors you want to consider when spreading the weight of a dead walker
# option max_dead_neighbors used to specify the maximum number of dead neighbors for a dead walker to be removed, if the number of dead nneighbors is larger
# than that value, it is kept!

import sys
import os
import math
import random
import optparse
import linecache
import numpy as np

from copy import copy
import coord_util.gro as gro

def set_option_parser():

    usage = "%prog [options] configuration_file"
    parser = optparse.OptionParser(usage + """
Perform reweighting step of DMdMD algorithm""")

    parser.add_option("--recovery", action="store_true", dest="recovery", default=False)
    parser.add_option("--max_alive_neighbors", action="store", type="int", dest="max_alive_neighbors", default=0)
    parser.add_option("--max_dead_neighbors", action="store", type="int", dest="max_dead_neighbors", default=0)

    return parser


def get_nnneighbors(rmsd_config_file, options):

    f = open(rmsd_config_file)
    lines = f.readlines()
    nnneighbors = int(lines[2])

    return nnneighbors


def get_nneighbors(file_name, idx, options):

    line = linecache.getline(file_name, idx+1)
    nneighbors = line.replace('\n','').split()
    nneighbors = map(int, nneighbors)
    nneighbors = np.array(nneighbors)-1

    return nneighbors


def get_ncopies(file_name, options):

    with open(file_name, "r") as file:
        ncopies = map(int, file.read().splitlines())

    return ncopies


def get_weights(file_name, options):

    if not options.recovery:
        weights = [1.0 for idx in range(grofile_obj.nruns)]
    else:
        with open(file_name, "r") as file: 
            weights = map(float, file.read().splitlines())

    return weights

parser = set_option_parser()
options, args = parser.parse_args(sys.argv[1:])

args_required = ['input_grofile_name', 'nnfile_name', 'ncfile_name', 'wfile_name', 'output_grofile_name']

if len(args)!=len(args_required):
    parser.error("exactly %i arguments are required: %s (%i provided)" %(len(args_required), ' + '.join(args_required), len(args)))
else:
    files_required = args_required[:-2]
    for idx, file_required in enumerate(files_required):
        file_name = args[idx]
        if not os.path.exists(file_name):
            parser.error("%s does not exist: '%s'" %(file_require[:-len('_name')], file_name))

input_grofile_name = args[0]
nnfile_name = args[1]
ncfile_name = args[2] # ncfile: input text file containing the number of copies that should be made for each walker
wfile_name = args[3] # wfile : input and output text file containing the Boltzmann Weights of each walker
output_grofile_name = args[4]

grofile_obj=gro.GroFile(input_grofile_name)
if os.path.exists(output_grofile_name): os.remove(output_grofile_name)

weights = get_weights(wfile_name, options)
ncopiess = get_ncopies(ncfile_name, options)

dead_walkers_idxs = []
for idx, ncopies in enumerate(ncopiess):
    if ncopies==0: dead_walkers_idxs.append(idx)

print "number of dead walkers: %i" %len(dead_walkers_idxs)
ndead_walkers_kept=0

# look for dead walkers that are finally kept because their x first nneighbors are all dead walkers.
for idx in dead_walkers_idxs:
    nneighbors = get_nneighbors(nnfile_name, idx, options)
    if options.max_dead_neighbors>0:
        nnneighbors = min(len(nneighbors), options.max_dead_neighbors+1)
    else: nnneighbors = len(nneighbors)
    if nnneighbors>1: #the first element of nneighbors is the point itself
        jdx=1; nneighbor_idx = nneighbors[jdx]
        while ncopiess[nneighbor_idx]==0:
            jdx+=1
            if jdx==nnneighbors: break
            else: nneighbor_idx = nneighbors[jdx]
        if jdx==nnneighbors: # all nneighbors are dead within the range fixed
            ncopiess[idx]=1 # do not kill this walker 
            ndead_walkers_kept+=1
    else: #the point has no nneighbor within the range fixed
        ncopiess[idx]=1 # do not kill this walker 
        ndead_walkers_kept+=1

print "number of dead walkers kept: %i" %ndead_walkers_kept
if ndead_walkers_kept>0:
    # build the matrix of dead walkers again if some dead walkers have been kept.
    dead_walkers_idxs = []
    for idx, ncopies in enumerate(ncopiess):
        if ncopies==0: dead_walkers_idxs.append(idx)

print "add weights of dead walkers to their nneighbor among new_walkers... ",
sys.stdout.flush()
# redristribute the weights of dead walkers to their first nneighbors which include dead walkers that were kept previously.
for idx in dead_walkers_idxs: #every idx has at least one nneighbor alive within the range fixed and its first options.max_dead_neighbors nneighbors are not all dead
    nneighbors = get_nneighbors(nnfile_name, idx, options)
    assert len(nneighbors)>1, "###ERROR: the number of nnearest neighbors should be greater than 1."
    nneighbors = nneighbors[1:] # exclude the first neighbor which is the point itself
    nalive_nneighbors=0 # count up the number of nneighbors still alive within the range fixed
    if options.max_alive_neighbors==0: # if options.max_alive_neighbors=0, spread the weight of the dead walker over all their nearest neighbors available
        for nneighbor_idx in nneighbors: nalive_nneighbors+=ncopiess[nneighbor_idx]
        for nneighbor_idx in nneighbors: weights[nneighbor_idx] += weights[idx]*ncopiess[nneighbor_idx]/nalive
    else: # if options.max_alive_neighbors>0, spread the weight of dead walkers over the first "options.max_alive_neighbors" neighbors
        for jdx, nneighbor_idx in enumerate(nneighbors):
            nalive_nneighbors+=ncopiess[nneighbor_idx]
            if nalive_nneighbors>=options.max_alive_neighbors: break
        last_nneighbor_idx=jdx
        for nneighbor_idx in nneighbors[:last_nneighbor_idx+1]: weights[nneighbor_idx] += weights[idx]*ncopiess[nneighbor_idx]/nalive_nneighbors
    weights[idx]=0.0

new_weights=[]
cutoff=1e-6
with open(input_grofile_name, 'r') as input_grofile:
    with open(output_grofile_name, 'w') as output_grofile:
        for idx, ncopies in enumerate(ncopiess):
            weight=weights[idx]
            if ncopies>=1 and weight>cutoff:
                new_weight = weight/ncopies
                start=grofile_obj.nlines_per_run*idx+1
                end=grofile_obj.nlines_per_run*(idx+1)+1
                for num_copy in range(ncopies):
                    new_weights.append(new_weight)
                    for jdx in range(start,end):
                        print >> output_grofile, linecache.getline(input_grofile_name, jdx).replace("\n", "")
print "done."

sum_old_weights=int(round(np.sum(weights)))
sum_new_weights=int(round(np.sum(new_weights)))
assert sum_new_weights==sum_old_weights, "sum of the weights differs from old number: sum_new_weights/sum_old_weights: %i/%i" %(sum_new_weights,sum_old_weights)

if not options.recovery: print "build wfile...",
else: print "update wfile...",
sys.stdout.flush()

with open('/'.join((os.getcwd(), wfile_name)), 'w') as wfile:
    for new_weight in new_weights: print >> wfile, '%e' % new_weight
print "done."

