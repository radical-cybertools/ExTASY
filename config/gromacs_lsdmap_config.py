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

num_runs = 10000

recovery_flag = 0

w_file = 'weight.w'

max_alive_neighbors = ''
max_dead_neighbors = ''
