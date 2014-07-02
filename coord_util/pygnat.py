# geometric near neighbors access tree module

# to find nearest neighbor : build gnat with build_gnat function, then use query_nneighbor

import sys
import os
from random import shuffle
import numpy as np

sys.setrecursionlimit(10000)

def euclidean_metric(x,y):
    return np.linalg.norm(x-y)


class GNATNode(object):

    def __init__(self, center, metric=euclidean_metric, k=10, rmax=0.):

        assert len(center)==2 

        self.metric = metric # metric used to find the nearest neighbor
        self.center = center # center point of the current node
        self.k = k # degree of the current node = number of (direct) subnodes
        self.free_points = [] # list of points (with index) of the current node that do not belong to any of its subnodes
        self.subnodes = [] # list of (direct) subnodes of the current node


    def add_points(self, new_points):

        if new_points == []:
            return

        metric = self.metric
        center = self.center

        self.free_points.extend(new_points) # first add new points to free points
        self.split() # then use them to split the current node into k subnodes 


    def split(self):

        free_points = self.free_points

        if self.subnodes == []:
            k = self.k
            if len(free_points) > 3*k: # if there is not enough points do not build subnodes, leave the new points as free points instead.
                self.subnodes, free_points = choose_subnodes(free_points, self.metric, k) # choose subnodes (split points) according to GNAT approach

        if self.subnodes != [] and free_points != []:
            ranges_between_subnodes = initialize_ranges_between_nodes(self.metric, self.subnodes)
            subnodes_points, self.ranges_between_subnodes = partition_and_get_ranges_between_nodes(free_points, self.metric, self.subnodes, ranges_between_subnodes)
            for (points, subnode) in zip(subnodes_points, self.subnodes):
                subnode.add_points(points)
            self.free_points = []


    def query_nneighbor(self, target, r=1e100):
        """Find the nearest neighbor of target.

        Returns the idx (in the samples with build_gnat function) of the nearest neighbor, and the distance r to that neighbor.
        
        Works recursively, only looking for a neighbor closer than all previously seen neighbors.

        """

        nneighbor = None

        metric = self.metric
        unused_subnodes = []

        distance_from_center = metric(target, self.center[0])

        if distance_from_center < r:
            nneighbor = self.center
            r = distance_from_center

        for free_point in self.free_points:
            distance_from_free_point = metric(target, free_point[0])
            if distance_from_free_point < r:
                nneighbor = free_point
                r = distance_from_free_point

        if self.subnodes != []:

            for idx, subnodei in enumerate(self.subnodes):
                distance_from_subnode = metric(target, subnodei.center[0])

                for jdx, subnodej in enumerate(self.subnodes): 
                    if idx!= jdx and \
   min(distance_from_subnode + r, self.ranges_between_subnodes[idx][jdx][1]) < max(distance_from_subnode - r, self.ranges_between_subnodes[idx][jdx][0]):
 
                        unused_subnodes.append(jdx)

            for idx, subnode in enumerate(self.subnodes):

                if idx not in unused_subnodes:
                    subnode_nneighbor, subnode_r = subnode.query_nneighbor(target, r)

                    if subnode_nneighbor is not None:
                        assert subnode_r < r
                        r = subnode_r
                        nneighbor = subnode_nneighbor
                
        return nneighbor, r


def get_distance_from_nodes_and_find_nearest_node(nodes, sample, metric):
    min_r = 1.e1000
    rs = [[] for n in nodes]
    for idx, node in enumerate(nodes):
        r = metric(node.center[0], sample)
        rs[idx] = r 
        if r <= min_r:
            min_r = r
            min_idx = idx
    return rs, min_idx


def partition_and_get_ranges_between_nodes(samples, metric, nodes, ranges):

    nodes_free_points = [[] for n in nodes]

    for [sample, idx_sample] in samples:
        rs, min_idx = get_distance_from_nodes_and_find_nearest_node(nodes, sample, metric)
        for idx, r in enumerate(rs):
            if idx!=min_idx:
                if r<=ranges[idx][min_idx][0]: ranges[idx][min_idx][0] = r
                if r>=ranges[idx][min_idx][1]: ranges[idx][min_idx][1] = r
        nodes_free_points[min_idx].append([sample, idx_sample])

    return nodes_free_points, ranges


def initialize_ranges_between_nodes(metric, nodes):

    ranges = [[[[],[]] for n in nodes] for m in nodes]

    for idx, nodei in enumerate(nodes):
        for jdx, nodej in enumerate(nodes):
            if idx != jdx:
                r = metric(nodei.center[0], nodej.center[0])
                ranges[idx][jdx][0] = r
                ranges[idx][jdx][1] = r

    return ranges


def choose_subnodes(samples, metric, k):
    num = len(samples)

    num_possible = min(num, 3*k)
    possible_sp = samples[:num_possible]
    rest = samples[num_possible:]
    sp = [possible_sp.pop()]
    for count in xrange(k - 1):
        max_min_r = 0.
        for (pdx, [p, p_idx]) in enumerate(possible_sp):
            min_r = 1.e100
            for [spx, sp_idx] in sp:
                r = metric(p, spx)
                assert isinstance(r, float) 
                min_r = min(r, min_r)  # compute the minimal distance between the candidate split point p and all split points sp
            if min_r >= max_min_r: # check among candidate split points the one with the greatest minimal distance to the split points 
                max_min_r = min_r
                new_pdx = pdx
                new_sp = p
                new_sp_idx = p_idx
        del possible_sp[new_pdx]
        sp.append([new_sp, new_sp_idx])
    rest.extend(possible_sp)
    return [GNATNode(p, metric, k) for p in sp], rest


def build_gnat(samples, frac=1., metric=euclidean_metric, k=5): 

    # samples = samples used to build gnat
    # frac = fraction of the samples actually used
    # metric = metric used to find neighbors
    # k = number of direct subnodes in gnat (k=4, k=5 looks to be the more efficient value)

    samples_idxs = range(len(samples))
    shuffle(samples_idxs)
    samples_idxs = samples_idxs[:int(len(samples)*frac)]
    samples_with_idxs = []

    for sample_idx in samples_idxs: samples_with_idxs.append([samples[sample_idx], sample_idx])

    root_node = GNATNode(samples_with_idxs[0], metric, k)
    root_node.add_points(samples_with_idxs[1:])

    return root_node
