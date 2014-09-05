__author__ = 'vivek'

#--------------------------General--------------------------------

num_CUs = 64 #num of CUs
num_iterations = 1

#--------------------------Simulation--------------------------------

input_gro_loc = '/tmp/ExTASY/gromacs_lsdmap_example'
input_gro = 'input.gro'


grompp_loc = '/tmp/ExTASY/gromacs_lsdmap_example'
grompp_name = 'grompp.mdp'

topol_loc = '/tmp/ExTASY/gromacs_lsdmap_example'
topol_name = 'topol.top'

tmp_grofile = 'tmp.gro'

#--------------------------Analysis----------------------------------

lsdm_config_loc = '/tmp/ExTASY/gromacs_lsdmap_example'
lsdm_config_name = 'config.ini'

system_name = 'out'


outgrofile_name = '%s.gro' %system_name
egfile = '%s.eg' % system_name
evfile = '%s.ev' % system_name
nearest_neighbor_file = '%s.nn' %system_name

num_runs = 10000
num_clone_files = '%s.nc' % system_name

recovery_flag = 0

wfile = 'weight.w'
