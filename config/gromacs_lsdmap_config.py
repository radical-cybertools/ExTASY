__author__ = 'vivek'

num_sims = 64 #num of CUs

num_iterations = 1

input_gro_loc = '/home/vivek/Research/ExTASY/gromacs_lsdmap_example'
input_gro = 'input.gro'


grompp_loc = '/home/vivek/Research/ExTASY/gromacs_lsdmap_example'
grompp_name = 'grompp.mdp'

topol_loc = '/home/vivek/Research/ExTASY/gromacs_lsdmap_example'
topol_name = 'topol.top'

tmp_grofile = 'tmp.gro'

lsdm_config = '/home/vivek/Research/ExTASY/gromacs_lsdmap_example'

system_name = 'out'


outgrofile_name = '%s.gro' %system_name
egfile = '%s.eg' % system_name
evfile = '%s.ev' % system_name
nearest_neighbor_file = '%s.nn' %system_name

num_runs = 10000
num_clone_files = '%s.nc' % system_name

recovery_flag = 0

wfile = 'weight.w'
