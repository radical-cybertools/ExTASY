import subprocess

resource_dict = {	'xsede.stampede': 'stampede.tacc.utexas.edu',
					'epsrc.archer': 'login.archer.ac.uk'
					}

simulator_dict = {	'Gromacs': 'grompp --version',
					'Amber': 'sander --version'
					}

analyzer_dict = {	'LSDMap': '',
					'CoCo': ''
					}

def resource_config_check(RPconfig,Kconfig):
	uname = RPconfig.UNAME
	target_resource = RPconfig.REMOTE_HOST
	app_simulator = Kconfig.simulator
	app_analyzer = Kconfig.analyzer

	sim_check = subprocess.Popen(["ssh","{0}@{1}".format(uname,resource_dict[target_resource]),
							simulator_dict[app_simulator]],
							stderr=subprocess.PIPE,
							stdout=subprocess.PIPE)

	sim_check_op,sim_check_err = sim_check.communicate()
	print sim_check_op

	ana_check = subprocess.Popen(["ssh","{0}@{1}".format(uname,resource_dict[target_resource]),
							analyzer_dict[app_analyzer]],
							stderr=subprocess.PIPE,
							stdout=subprocess.PIPE)

	ana_check_op,ana_check_err = ana_check.communicate()
	print ana_check_op