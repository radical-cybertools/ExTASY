#!/home/jp43/local/bin/python

# module used to create the cste eps file from the mean of epsilon values of file epsfile_in


import sys
import os
import optparse
import numpy as np

def set_option_parser():

        usage = "%prog [options] epsfile_in epsfile_out "
        parser = optparse.OptionParser(usage + """
Convert user defined epsfile to constant epsfile""")

        parser.add_option("--average", action="store_true", dest="average", default=True)

        return parser


parser = set_option_parser()
options, args = parser.parse_args(sys.argv[1:])

args_required = ['epsfile_in', 'epsfile_out']

if len(args)!=len(args_required):
    parser.error("exactly %i arguments are required: %s (%i provided)" %(len(args_required), ' + '.join(args_required), len(args)))
else:
    files_required = args_required[:-1]
    for idx, file_required in enumerate(files_required):
        file_name = args[idx]
        if not os.path.exists(file_name):
            parser.error("%s does not exist: '%s'" %(file_require[:-len('_name')], file_name))



epsfile_in=args[0]
epsfile_out=args[1]

with open(epsfile_in,'r') as epsfile_in:
    eps_in=epsfile_in.read().splitlines()
    eps_in=np.array(map(float,eps_in))

npoints=len(eps_in)

if options.average: cste_eps=np.mean(eps_in)

with open(epsfile_out,'w') as epsfile_out:
    for idx in range(npoints): print >> epsfile_out, cste_eps

