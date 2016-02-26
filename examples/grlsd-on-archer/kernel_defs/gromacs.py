#!/usr/bin/env python

"""A kernel that creates a new ASCII file with a given size and name.
"""

__author__    = "The ExTASY project <vivek.balasubramanian@rutgers.edu>"
__copyright__ = "Copyright 2015, http://www.extasy-project.org/"
__license__   = "MIT"

from copy import deepcopy

from radical.ensemblemd.exceptions import ArgumentError
from radical.ensemblemd.exceptions import NoKernelConfigurationError
from radical.ensemblemd.engine import get_engine
from radical.ensemblemd.kernel_plugins.kernel_base import KernelBase

# ------------------------------------------------------------------------------

_KERNEL_INFO = {
    "name":         "custom.gromacs",
    "description":  "Creates a new file of given size and fills it with random ASCII characters.",
    "arguments":   {"--grompp=":
                        {
                            "mandatory": True,
                            "description": "Input parameter filename"
                        },
                    "--topol=":
                        {
                            "mandatory": True,
                            "description": "Topology filename"
                        }
                    },
    "machine_configs":
    {
        "*": {
            "environment"   : {"FOO": "bar"},
            "pre_exec"      : [],
            "executable"    : "python",
            "uses_mpi"      : True
        },

        "xsede.stampede":
        {
            "environment" : {},
            "pre_exec" : ["module load TACC","module load intel/15.0.2","module load boost","module load cxx11","module load gromacs","module load python"],
            "executable" : ["python"],
            "uses_mpi"   : True
        },

        "epsrc.archer":
        {
            "environment" : {},
            "pre_exec" : ["module load packages-archer","export PATH=$PATH:/work/z01/shared/gromacs-5.1.2/bin","module load python-compute/2.7.6"],
            "executable" : ["python"],
            "uses_mpi"   : True
        },
    
    }
}


# ------------------------------------------------------------------------------
#
class kernel_gromacs(KernelBase):

    def __init__(self):

        super(kernel_gromacs, self).__init__(_KERNEL_INFO)
     	"""Le constructor."""
        		
    # --------------------------------------------------------------------------
    #
    @staticmethod
    def get_name():
        return _KERNEL_INFO["name"]
        

    def _bind_to_resource(self, resource_key):
        
        """(PRIVATE) Implements parent class method.
        """
        if resource_key not in _KERNEL_INFO["machine_configs"]:
            if "*" in _KERNEL_INFO["machine_configs"]:
                # Fall-back to generic resource key
                resource_key = "*"
            else:
                raise NoKernelConfigurationError(kernel_name=_KERNEL_INFO["name"], resource_key=resource_key)

        cfg = _KERNEL_INFO["machine_configs"][resource_key]

        #change to pmemd.MPI when cores can be set
        arguments = ['run.py','--mdp','%s'%self.get_arg("--grompp="),'--gro','start.gro','--top','%s'%self.get_arg('--topol='),'--out','out.gro']

        self._executable  = cfg["executable"]
        self._arguments   = arguments
        self._environment = cfg["environment"]
        self._uses_mpi    = cfg["uses_mpi"]
        self._pre_exec    = cfg["pre_exec"] 

# ------------------------------------------------------------------------------
