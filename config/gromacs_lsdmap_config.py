__author__ = 'vivek'

#--------------------------General--------------------------------

num_CUs = 64 #num of CUs
num_iterations = 1
start_iter = 0
nsave = 2

#--------------------------Simulation--------------------------------

num_cores_per_sim_cu = 2

md_input_file = '/tmp/ExTASY/gromacs_lsdmap_example/input.gro'

mdp_file = '/tmp/ExTASY/gromacs_lsdmap_example/grompp.mdp'

top_file = '/tmp/ExTASY/gromacs_lsdmap_example/topol.top'

ndx_file = ''

grompp_options = ''
mdrun_options = ''

itp_file_loc = ''

md_output_file = 'tmp.gro'

#--------------------------Analysis----------------------------------

lsdm_config_file = '/tmp/ExTASY/gromacs_lsdmap_example/config.ini'

system_name = 'out'


outgrofile_name = '%s.gro' %system_name
egfile = '%s.eg' % system_name
evfile = '%s.ev' % system_name
nearest_neighbor_file = '%s.nn' %system_name

num_runs = 10000
num_clone_files = '%s.nc' % system_name

recovery_flag = 0

w_file = 'weight.w'

max_alive_neighbors = ''
max_dead_neighbors = ''
