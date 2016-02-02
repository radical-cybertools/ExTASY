#!/usr/bin/env python

__author__        = "Vivek <vivek.balasubramanian@rutgers.edu>"
__copyright__     = "Copyright 2014, http://radical.rutgers.edu"
__license__       = "MIT"
__use_case_name__ = "'Gromacs + LSDMap' simulation-analysis proof-of-concept (ExTASY)."
  
  
from radical.ensemblemd import Kernel
from radical.ensemblemd import SimulationAnalysisLoop
from radical.ensemblemd import EnsemblemdError
from radical.ensemblemd import SimulationAnalysisLoop
from radical.ensemblemd import SingleClusterEnvironment
import sys
import imp
import argparse
import os
import json

from radical.ensemblemd.engine import get_engine

# ------------------------------------------------------------------------------
# Set default verbosity

if os.environ.get('RADICAL_ENMD_VERBOSE') == None:
    os.environ['RADICAL_ENMD_VERBOSE'] = 'REPORT'

# ------------------------------------------------------------------------------
#Load all custom Kernels

from kernel_defs.pre_grlsd_loop import kernel_pre_grlsd_loop
get_engine().add_kernel_plugin(kernel_pre_grlsd_loop)

from kernel_defs.gromacs import kernel_gromacs
get_engine().add_kernel_plugin(kernel_gromacs)

from kernel_defs.pre_lsdmap import kernel_pre_lsdmap
get_engine().add_kernel_plugin(kernel_pre_lsdmap)

from kernel_defs.lsdmap import kernel_lsdmap
get_engine().add_kernel_plugin(kernel_lsdmap)

from kernel_defs.post_lsdmap import kernel_post_lsdmap
get_engine().add_kernel_plugin(kernel_post_lsdmap)
# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------
#
class Gromacs_LSDMap(SimulationAnalysisLoop):
  # TODO Vivek: add description.

    def __init__(self, maxiterations, simulation_instances=1, analysis_instances=1):
        SimulationAnalysisLoop.__init__(self, maxiterations, simulation_instances, analysis_instances)
    
    def pre_loop(self):
        '''
        function : transfers input files and intermediate executables

        pre_grlsd_loop :-
                Purpose : Transfers files, Split the input file into smaller files to be used by each of the
                            gromacs instances in the first iteration.

                Arguments : --inputfile = file to be split
                            --numCUs    = number of simulation instances/ number of smaller files
        '''
        k = Kernel(name="custom.pre_grlsd_loop")
        k.arguments = ["--inputfile={0}".format(os.path.basename(Kconfig.md_input_file)),"--numCUs={0}".format(Kconfig.num_CUs)]
        k.copy_input_data = [  '$SHARED/{0}'.format(os.path.basename(Kconfig.md_input_file)),
                               '$SHARED/spliter.py',
                               '$SHARED/gro.py'
                            ]
        
        return k

    def simulation_step(self, iteration, instance):

        '''
        function : In iter=1, use the input files from pre_loop, else use the outputs of the analysis stage in the
        previous iteration. Run gromacs in each instance using these files.

        gromacs :-

                Purpose : Run the gromacs simulation on each of the smaller files. Parameter files and executables are input
                            from pre_loop. There are 'numCUs' number of instances of gromacs per iteration.

                Arguments : --grompp    = gromacs parameters filename
                            --topol     = topology filename
        '''

        gromacs = Kernel(name="custom.gromacs")
        gromacs.arguments = ["--grompp={0}".format(os.path.basename(Kconfig.mdp_file)),
                             "--topol={0}".format(os.path.basename(Kconfig.top_file))]
        gromacs.link_input_data = ['$SHARED/{0} > {0}'.format(os.path.basename(Kconfig.mdp_file)),
                                   '$SHARED/{0} > {0}'.format(os.path.basename(Kconfig.top_file)),
                                   '$SHARED/run.py > run.py']

        if (iteration-1==0):
            gromacs.link_input_data.append('$PRE_LOOP/temp/start{0}.gro > start.gro'.format(instance-1))

        else:
            gromacs.link_input_data.append('$ANALYSIS_ITERATION_{0}_INSTANCE_1/temp/start{1}.gro > start.gro'.format(iteration-1,instance-1))

        if Kconfig.grompp_options is not None:
            gromacs.environment = {'grompp_options':Kconfig.grompp_options}
        if Kconfig.mdrun_options is not None:
            gromacs.environment = {'mdrun_options':Kconfig.mdrun_options}
        if Kconfig.ndx_file is not None:
            gromacs.environment = {'ndxfile',os.path.basename(Kconfig.ndx_file)}
            gromacs.link_input_data.append('$SHARED/{0}'.format(os.path.basename(Kconfig.ndx_file)))


        return gromacs
    
    def analysis_step(self, iteration, instance):
        '''
        function : Merge the results of each of the simulation instances and run LSDMap analysis to generate the
        new coordinate file. Split this new coordinate file into smaller files to be used by the simulation stage
        in the next iteration.

        If a step as multiple kernels (say k1, k2), data generated in k1 is implicitly moved to k2 (if k2 requires).
        Data which needs to be moved between the various steps (pre_loop, simulation_step, analysis_step) needs to
        be mentioned by the user.

        pre_lsdmap :-

                Purpose : The output of each gromacs instance in the simulation_step is a small coordinate file. Concatenate
                            such files from each of the gromacs instances to form a larger file. There is one instance of pre_lsdmap per
                            iteration.

                Arguments : --numCUs = number of simulation instances / number of small files to be concatenated

        lsdmap :-

                Purpose : Perform LSDMap on the large coordinate file to generate weights and eigen values. There is one instance
                            of lsdmap per iteration (MSSA : Multiple Simulation Single Analysis model).

                Arguments : --config = name of the config file to be used during LSDMap

        post_lsdmap :-


                Purpose : Use the weights, eigen values generated in lsdmap along with other parameter files from pre_loop
                            to generate the new coordinate file to be used by the simulation_step in the next iteration. There is one
                            instance of post_lsdmap per iteration.
post_ana.arguments = ["--num_runs={0}".format(Kconfig.num_runs),
                              "--out=out.gro",
                              "--cycle={0}".format(iteration-1),
                              "--max_dead_neighbors={0}".format(Kconfig.max_dead_neighbors),
                              "--max_alive_neighbors={0}".format(Kconfig.max_alive_neighbors),
                              "--numCUs={0}".format(Kconfig.num_CUs)]

                Arguments : --num_runs              = number of configurations to be generated in the new coordinate file
                            --out                   = output filename
                            --cycle                 = iteration number
                            --max_dead_neighbors    = max dead neighbors to be considered
                            --max_alive_neighbors   = max alive neighbors to be considered
                            --numCUs                = number of simulation instances/ number of smaller files
        '''

        pre_ana = Kernel(name="custom.pre_lsdmap")
        pre_ana.arguments = ["--numCUs={0}".format(Kconfig.num_CUs)]
        pre_ana.link_input_data = ["$SHARED/pre_analyze.py > pre_analyze.py"]
        for i in range(1,Kconfig.num_CUs+1):
            pre_ana.link_input_data = pre_ana.link_input_data + ["$SIMULATION_ITERATION_{2}_INSTANCE_{0}/out.gro > out{1}.gro".format(i,i-1,iteration)]
        pre_ana.copy_output_data = ['tmpha.gro > $SHARED/iter_{0}/tmpha.gro'.format(iteration-1),'tmp.gro > $SHARED/iter_{0}/tmp.gro'.format(iteration-1)]

        lsdmap = Kernel(name="md.lsdmap")
        lsdmap.arguments = ["--config={0}".format(os.path.basename(Kconfig.lsdm_config_file))]
        lsdmap.link_input_data = ['$SHARED/{0} > {0}'.format(os.path.basename(Kconfig.lsdm_config_file)),'$SHARED/iter_{0}/tmpha.gro > tmpha.gro'.format(iteration-1)]
        lsdmap.cores = 1
        if iteration > 1:
            lsdmap.link_input_data += ['$ANALYSIS_ITERATION_{0}_INSTANCE_1/weight.w > weight.w'.format(iteration-1)]
            lsdmap.copy_output_data = ['weight.w > $SHARED/iter_{0}/weight.w'.format(iteration-1)]
        lsdmap.copy_output_data = ['tmpha.ev > $SHARED/iter_{0}/tmpha.ev'.format(iteration-1),'out.nn > $SHARED/iter_{0}/out.nn'.format(iteration-1)]
        
        if(iteration%Kconfig.nsave==0):
          lsdmap.download_output_data=['lsdmap.log > output/iter{0}/lsdmap.log'.format(iteration-1)]

        post_ana = Kernel(name="custom.post_lsdmap")
        post_ana.link_input_data = ["$SHARED/post_analyze.py > post_analyze.py",
                                    "$SHARED/selection.py > selection.py",
                                    "$SHARED/reweighting.py > reweighting.py",
                                    "$SHARED/spliter.py > spliter.py",
                                    "$SHARED/gro.py > gro.py",
                                    "$SHARED/iter_{0}/tmp.gro > tmp.gro".format(iteration-1),
                                    "$SHARED/iter_{0}/tmpha.ev > tmpha.ev".format(iteration-1),
                                    "$SHARED/iter_{0}/out.nn > out.nn".format(iteration-1),
                                    "$SHARED/input.gro > input.gro"]

        post_ana.arguments = ["--num_runs={0}".format(Kconfig.num_runs),
                              "--out=out.gro",
                              "--cycle={0}".format(iteration-1),
                              "--max_dead_neighbors={0}".format(Kconfig.max_dead_neighbors),
                              "--max_alive_neighbors={0}".format(Kconfig.max_alive_neighbors),
                              "--numCUs={0}".format(Kconfig.num_CUs)]


        if iteration > 1:
            post_ana.link_input_data += ['$ANALYSIS_ITERATION_{0}_INSTANCE_1/weight.w > weight_new.w'.format(iteration-1)]

        if(iteration%Kconfig.nsave==0):
            post_ana.download_output_data = ['out.gro > output/iter{0}/out.gro'.format(iteration),
                                             'weight.w > output/iter{0}/weight.w'.format(iteration)]

        return [pre_ana,lsdmap,post_ana]

# ------------------------------------------------------------------------------
#
if __name__ == "__main__":

  try:

      parser = argparse.ArgumentParser()
      parser.add_argument('--RPconfig', help='link to Radical Pilot related configurations file')
      parser.add_argument('--Kconfig', help='link to Kernel configurations file')

      args = parser.parse_args()

      if args.RPconfig is None:
          parser.error('Please enter a RP configuration file')
          sys.exit(1)
      if args.Kconfig is None:
          parser.error('Please enter a Kernel configuration file')
          sys.exit(0)

      RPconfig = imp.load_source('RPconfig', args.RPconfig)
      Kconfig = imp.load_source('Kconfig', args.Kconfig)



      # Create a new static execution context with one resource and a fixed
      # number of cores and runtime.
      cluster = SingleClusterEnvironment(
            resource=RPconfig.REMOTE_HOST,
            cores=RPconfig.PILOTSIZE,
            walltime=RPconfig.WALLTIME,
            username = RPconfig.UNAME, #username
            project = RPconfig.ALLOCATION, #project
            queue = RPconfig.QUEUE,
            database_url = RPconfig.DBURL
      )

      cluster.shared_data = [
                                Kconfig.md_input_file,
                                Kconfig.lsdm_config_file,
                                Kconfig.top_file,
                                Kconfig.mdp_file,
                                '{0}/spliter.py'.format(Kconfig.helper_scripts),
                                '{0}/gro.py'.format(Kconfig.helper_scripts),
                                '{0}/run.py'.format(Kconfig.helper_scripts),
                                '{0}/pre_analyze.py'.format(Kconfig.helper_scripts),
                                '{0}/post_analyze.py'.format(Kconfig.helper_scripts),
                                '{0}/selection.py'.format(Kconfig.helper_scripts),
                                '{0}/reweighting.py'.format(Kconfig.helper_scripts)
                            ]

      if Kconfig.ndx_file is not None:
          cluster.shared_data.append(Kconfig.ndx_file)

      cluster.allocate()

      # We set the 'instances' of the simulation step to 16. This means that 16
      # instances of the simulation are executed every iteration.
      # We set the 'instances' of the analysis step to 1. This means that only
      # one instance of the analysis is executed for each iteration
      randomsa = Gromacs_LSDMap(maxiterations=Kconfig.num_iterations, simulation_instances=Kconfig.num_CUs, analysis_instances=1)

      cluster.run(randomsa)

      cluster.deallocate()

  except EnsemblemdError, er:

    print "Ensemble MD Toolkit Error: {0}".format(str(er))
    raise # Just raise the execption again to get the backtrace
