__author__ = 'vivek'

import sys
import pyximport
pyximport.install()
import pickle
import numpy as np
import os

if __name__ =="__main__":

    idxs_task_file = sys.argv[1]
    shared_input_url = sys.argv[2]

    print shared_input_url

    files = os.listdir(shared_input_url)

    print files

    with open(idxs_task_file,'rb') as f:
        idxs_task,coords,weights,metric,status_epsilon,k,epsilon = pickle.load(f)

    for i in range(0,len(files)):
        os.system('/bin/bash -l -c "ln -s %s/%s ."'%(shared_input_url,files[i]))

    npoints_task=len(idxs_task)

    coords_task = np.array([coords[idx] for idx in idxs_task])
    weights_task = np.array([weights[idx] for idx in idxs_task])

    import metric as mt

    DistanceMatrix = mt.DistanceMatrix(coords_task,coords, metric=metric)
    distance_matrix_thread = DistanceMatrix.distance_matrix
    print("distance matrix computed")

    if status_epsilon == 'kneighbor':
        epsilon_task = DistanceMatrix.neighbor_matrix(k=k+1)[:,-1]
        epsilon = np.hstack(all)



