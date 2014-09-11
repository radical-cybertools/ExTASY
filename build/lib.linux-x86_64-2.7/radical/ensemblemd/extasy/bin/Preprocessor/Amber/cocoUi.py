#!/usr/bin/python 
from extasy import pcz
from extasy import cofasu
from extasy import script
from extasy import optimizer
from extasy import coco

#import argh
import logging as log
import sys
import os.path as op
import numpy as np
import MDAnalysis as mda
import argparse

def coco_ui(args):
	if args.verbosity:
		log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
		log.info("Verbose output.")
	else:
		log.basicConfig(format="%(levelname)s: %(message)s")

	log.info('Performing coco analysis!')

	''' Generate new start structures through COCO analysis of all trajectory data so far. '''
	
	dict = {}
	dict['topfile'] = 'penta.top'
	
	print 'creating cofasu...'
	f = []
	ls = script.Script()
	ls.append('ls -1 rep0?/*.mdcrd')
	a = ls.run("tcsh -f {}")
	for trj in a.split():
		f.append(cofasu.Fasu(dict['topfile'],trj,stop=99))
	
	cf = cofasu.Cofasu(f)

	print 'cofasu contains ',cf.natoms,' and ',cf.numframes(),' frames'
	# Create the optimizer for every cycle since cocoUi will be called 
	# for every cycle separately.

	print 'creating optimizer...'
	o = optimizer.Optimizer(cf, tol=0.01)
	
	print 'running pcazip...'
	p = pcz.Pcz(cf)
	        
	# Lets decide the parameters to instantiate an instance of the coco 
	# class: projs=the first three projections and grid=10 for default.
	
	dim = int(args.projs)
	projsSel = np.zeros((p.nframes,dim))
	for i in range(dim):
		projsSel[:,i] = p.proj(i)
	
	# Build the COCO map from the selected projection data.
	coco_instance = coco.Coco(projsSel)
	# Find the COCO points.
	nreps = int(args.frontpoints)
	cp = coco_instance.cpoints(nreps)
	
	dict['cycle'] = str(args.cycle)
	
	for rep in range(nreps):
		dict['rep'] = rep
		# Convert the point to a crude structure.
		e = p.expand(cp[rep,:])
		crude = p.unmap(e)
		cf.writepdb('rep0{rep}/penta{cycle}.pdb'.format(**dict),crude)
		# Optimise the crude structure.
		opt = o.optimize(crude, dtol=0.005)
		cf.writepdb('rep0{rep}/pentaopt{cycle}.pdb'.format(**dict),opt)
			
#########################################################################################
#																						#
#									ENTRY POINT											#
#																						#
#########################################################################################
#@argh.dispatch_command

# Optional arguments related to coco analysis
#@argh.arg('-g','--grid', type=int, default=10, help="The grid dimensions to consider in coco.")
#@argh.arg('-p','--projs', type=int, default=3, help='''The number of projections to consider from the input pcz
#file in coco that will also correspond to the number of dimensions of the grid.''')
# @ardi
# Decide how to set the number of new frontier points in relation with the number of frames given in input.
# As the things are implemented, for the moment lets assume that the nr of new frontier points will
# coincide with the number of frames.
#@argh.arg('-f','--frontpoints', type=int, default=None, help="The number of new frontier points to select through coco.")
#@argh.arg('-o','--output', type=str, default=None, help='''Specify name of outputfile to store the
#coco generated pcz file. This argument is an optional argument.''')
#@argh.arg('-c','--cycle', type=int, help='''This parameter will specify the cycle id.''')

#@argh.arg('-v','--verbosity', nargs='?', help="Increase output verbosity.")

if __name__ == '__main__':
	parser=argparse.ArgumentParser()
	parser.add_argument('-g','--grid', type=int, default=10, help="The grid dimensions to consider in coco.")
	parser.add_argument('-p','--projs', type=int, default=3, help='The number of projections to consider from the input pcz file in coco that will also correspond to the number of dimensions of the grid.')
	parser.add_argument('-f','--frontpoints', type=int, default=None, help="The number of new frontier points to select through coco.")
	parser.add_argument('-c','--cycle', type=int, help='This parameter will specify the cycle id.')
	parser.add_argument('-v','--verbosity', nargs='?', help="Increase output verbosity.")
	args=parser.parse_args()
	coco_ui(args)
