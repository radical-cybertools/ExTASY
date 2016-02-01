#!/usr/bin/env python

"""A kernel that creates a new ASCII file with a given size and name.
"""

__author__    = "Vivek <vivek.balasubramanian@rutgers.edu>"
__copyright__ = "Copyright 2014, http://radical.rutgers.edu"
__license__   = "MIT"

from copy import deepcopy

from radical.ensemblemd.exceptions import ArgumentError
from radical.ensemblemd.exceptions import NoKernelConfigurationError
from radical.ensemblemd.kernel_plugins.kernel_base import KernelBase

# ------------------------------------------------------------------------------
#
_KERNEL_INFO = {
    "name":         "custom.post_lsdmap",
    "description":  "Creates a new file of given size and fills it with random ASCII characters.",
    "arguments":   {"--num_runs=":
                        {
                            "mandatory": True,
                            "description": "Number of runs to be generated in output file"
                        },
                    "--out=":
                        {
                            "mandatory": True,
                            "description": "Output filename"
                        },
                    "--cycle=":
                        {
                            "mandatory": True,
                            "description": "Current iteration"
                        },
                    "--max_dead_neighbors=":
                        {
                            "mandatory": True,
                            "description": "Max dead neighbors to be considered"
                        },
                    "--max_alive_neighbors=":
                        {
                            "mandatory": True,
                            "description": "Max alive neighbors to be considered"
                        }

                    },
    "machine_configs":
    {
        "*": {
            "environment"   : {"FOO": "bar"},
            "pre_exec"      : [],
            "executable"    : ".",
            "uses_mpi"      : True
        },

        "xsede.stampede":
        {
            "environment" : {},
            "pre_exec" : ["module load TACC","module load python",
            "export PYTHONPATH=/home1/03036/jp43/.local/lib/python2.7/site-packages:$PYTHONPATH",
            "export PYTHONPATH=/home1/03036/jp43/.local/lib/python2.7/site-packages/lsdmap/rw:$PYTHONPATH",
            "export PYTHONPATH=/home1/03036/jp43/.local/lib/python2.7/site-packages/util:$PYTHONPATH"],
            "executable" : ["python"],
            "uses_mpi"   : False
        },

        "epsrc.archer":
        {
            "environment" : {},
            "pre_exec" : [  "module load python-compute/2.7.6",
                            "module load pc-numpy/1.9.2-libsci",
                            "module load pc-scipy/0.15.1-libsci",
                            "module load lsdmap",
                            "export PYTHONPATH=/work/y07/y07/cse/lsdmap/lsdmap-git-rc2:$PYTHONPATH",
                            "export PYTHONPATH=/work/y07/y07/cse/lsdmap/lsdmap-git-rc2/lsdmap/rw:$PYTHONPATH",
                            "export PYTHONPATH=/work/y07/y07/cse/lsdmap/lsdmap-git-rc2/util:$PYTHONPATH"],
            "executable" : ["python"],
            "uses_mpi"   : False
        },
    }
}


# ------------------------------------------------------------------------------
#
class kernel_post_lsdmap(KernelBase):

    # --------------------------------------------------------------------------
    #
    def __init__(self):
        """Le constructor.
        """
        super(kernel_post_lsdmap, self).__init__(_KERNEL_INFO)

    # --------------------------------------------------------------------------
    #
    @staticmethod
    def get_name():
        return _KERNEL_INFO["name"]

    # --------------------------------------------------------------------------
    #
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

        arguments = ['post_analyze.py','{0}'.format(self.get_arg("--num_runs=")),'tmpha.ev','ncopies.nc','tmp.gro'
                     ,'out.nn','weight.w','{0}'.format(self.get_arg("--out="))
                     ,'{0}'.format(self.get_arg("--max_alive_neighbors=")),'{0}'.format(self.get_arg("--max_dead_neighbors="))
                     ,'input.gro','{0}'.format(self.get_arg("--cycle="))]

        self._executable  = cfg["executable"]
        self._arguments   = arguments
        self._environment = cfg["environment"]
        self._uses_mpi    = cfg["uses_mpi"]
        self._pre_exec    = cfg["pre_exec"]
