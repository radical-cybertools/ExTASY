__author__ = 'vivek'

num_sims = 64 #num of CUs

num_iterations = 1

input_gro_loc = '/tmp/ExTASY/run'
input_gro = 'input.gro'


grompp_loc = '/tmp/ExTASY/run'
grompp_name = 'grompp.mdp'

topol_loc = '/tmp/ExTASY/run'
topol_name = 'topol.top'

tmp_grofile = 'tmp.gro'

lsdm_config = '/tmp/ExTASY/config'

system_name = 'aladip_1000'


outgrofile_name = '%s.gro' %system_name
egfile = '%s.eg' % system_name
evfile = '%s.ev' % system_name
nearest_neighbor_file = '%s.nn' %system_name

num_runs = 10000
num_clone_files = '%s.nc' % system_name

recovery_flag = 0

temp_wfile = '%s_tmp.w' % system_name