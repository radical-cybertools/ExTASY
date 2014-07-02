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
outgrofile_name = 'out.gro'

sys = 'aladip_1000'

egfile = '%s.eg' % sys
evfile = '%s.ev' % sys
nearest_neighbor_file = '%s.nn' %sys

num_runs = 10000
num_clone_files = '%s.nc' % sys

recovery_flag = 0

temp_wfile = '%s_tmp.w' % sys