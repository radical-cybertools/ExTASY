''' User Configurations'''


#-------------------------------------------------------------------------------------------------
# Change the values below accordingly to choose the Simulator and Analyzer
Load_Simulator = 'Gromacs'                        # Simulator to be loaded. Can be 'Amber' or 'Gromacs'
Load_Analyzer = 'LSDMap'                          # Analyzer to be loaded. Can be 'CoCo' or 'LSDMap'
#-------------------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------------------
# Change the following Radical Pilot according to use requirements
REMOTE_HOST = 'stampede.tacc.utexas.edu'        # Label/Name of the Remote Machine
UNAME = 'vivek91'                               # Username on the Remote Machine
ALLOCATION = 'TG-MCB090174'                     # Allocation to be charged
WALLTIME = 60                                   # Walltime to be requested for the pilot
PILOTSIZE = 64                                  # Number of cores to be reserved
WORKDIR = None			                # Working directory on the remote machine
QUEUE = 'normal'                                # Name of the queue in the remote machine


#-------------------------------------------------------------------------------------------------
# MongoDB related parameters
DBURL = 'mongodb://ec2-184-72-89-141.compute-1.amazonaws.com:27017/'        # URL of the MongoDB link to be used
