
## this program is used to preform the selection step of extended DMdMD algorithm the first diffusion coordinates of each endpoint are loaded, 
## then we select a new set of points from the endpoints according to a uniform distribution along the first dc
## Note that the number of points selected is always the same (given by the option --np) but the number of endpoints (input) can vary as in the reweighting step, killed endpoints with no immediate nearest neighbor are kept (see update_weights.py used for the reweighting step).

## what's new: after sampling a random point along the first dc, we do not select the new starting point as random among the nearest enpoints but we select the new point so as to get a flat distribution along the second dc

import os
import sys
import ConfigParser
import optparse

import math
import numpy as np

import coord_util.sampling as sampling


class LSDMapSampling(object):


    def set_option_parser(self):

        usage = "%prog [options] <dc_file> <output_file>"
        parser = optparse.OptionParser(usage + """
Selection of new points from input database using accept-reject algorithm based on DC values""")

        parser.add_option("--np", action="store", type="int", dest="npoints_out")

        return parser


    def get_dcs(self, file_name, dc_number, options):

        # load the k^th dcs from file_name (should be a ".ev" file), with k=dc_number, 
        # dcks is the column containing all the k^th dcs. 

        dcks = []
        with open(file_name, "r") as file:
            for line in iter(file):
                dcs = line.split()
                dck = float(dcs[dc_number].replace('D','E'))
                dcks.append(dck)
        dcks = np.array(dcks)

        return dcks


    def run(self, argv=[]):

        parser = self.set_option_parser()
        options, args = parser.parse_args(sys.argv[1:])

        if not options.npoints_out:
            parser.error('###ERROR: number of samples not given!')


        args_required = ['dcfile_name', 'ncfile_name']
        if len(args)!=len(args_required):
	    parser.error("exactly %i arguments are required: %s (%i provided)" %(len(args_required), ' + '.join(args_required), len(args)))
        else:
            files_required = args_required[:-1]
            for idx, file_required in enumerate(files_required):
                file_name = args[idx]
                if not os.path.exists(file_name):
	            parser.error("%s does not exist: '%s'" %(file_required[:-len('_name')], file_name))

            dcfile_name = args[0] # dcfile: input text file containing the Diffusion Coordinates of each walker
            ncfile_name = args[1] # ncfile: output text file containing the Number of Copies that should be made for each walker

        dc1s=self.get_dcs(dcfile_name, 1, options) # get first dcs from the .ev file.
        dc2s=self.get_dcs(dcfile_name, 2, options) # get second dcs from the .ev file.
        npoints_in=len(dc1s)

        # values used for the distribution
        mindc1s=np.amin(dc1s) # minimum of the distribution = min of dc1s
        maxdc1s=np.amax(dc1s)  # maximum of the distribution = max of dc1s
        #if maxdc1s<0.001: print "Problem with DC file max(DC1)<0.001"; sys.exit(2) # used to check if anything went wrong with LSDMap computation
        print "minimum probability at %.5f" %mindc1s
        print "maximum probability at %.5f" %maxdc1s

        # create a histogram with the values of the first dcs
        nbins=int(math.sqrt(npoints_in)/2)
        bins=mindc1s+np.array(range(nbins+1))*(maxdc1s-mindc1s)/nbins; bins[-1]+=1e-6 # slightly change the size of the last bin to include maxdc1s
        inds=np.digitize(dc1s, bins)-1 # inds contains the idx of the bin of each point.
        hist=[[] for i in range(nbins)]
        for idx, ind in enumerate(inds): hist[ind].append(idx) # create histogram with the idx of each point

        print "construct the vector of ncopies...",
        sys.stdout.flush()
        ncopiess = np.zeros(npoints_in, dtype='i')

        for jdx in range(options.npoints_out):
            # sample a random number according to a uniform distribution between mindc1s and maxdc1s
            sample=sampling.get_sample('uniform', mindc1s, maxdc1s)
            ind=np.digitize([sample],bins)-1; ind = ind[0] # find the idx of the bin the sample falls into
            while len(hist[ind])==0: # while there is no endpoints in the bin...
                sample=sampling.get_sample('uniform', mindc1s, maxdc1s) # ... pick another sample
                ind=np.digitize([sample], bins)-1; ind = ind[0] # find the idx of the bin the sample falls into
            # idx=np.random.choice(hist[ind]) # choose the new starting point as random inside the bin
            # choose the new starting point so as to have a flat distribution of points along DC2 within the bin
            dc2s_bin=[dc2s[idx] for idx in hist[ind]]
            mindc2s=np.amin(dc2s_bin); maxdc2s=np.amax(dc2s_bin)
            sample2=sampling.get_sample('uniform', mindc2s, maxdc2s)
            jdx=(np.abs(dc2s_bin-sample2)).argmin()
            idx=hist[ind][jdx] 
            ncopiess[idx]+=1

        print "done."

        print "build nc file...",
        sys.stdout.flush()
        with open(ncfile_name, 'w') as ncfile:
            for ncopies in ncopiess: print >> ncfile, ncopies

        print "done."

if __name__ == "__main__":
    LSDMapSampling().run(sys.argv[1:])
