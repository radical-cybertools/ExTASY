import os
import sys
import ConfigParser
import optparse

import math
import numpy as np

from random import random


def exponential(a, n=1):

    # p(x) = a*exp(-ax) if x>=0
    # p(x) = 0 if x<0

    sample = -math.log(random())/a
 
    return sample 


def uniform(xmin, xmax):

    return random()*(xmax-xmin)+xmin 


def truncated_exponential(a, xmin, xmax):

    if a==0.0: return uniform(xmin, xmax)

    # p(x) = a*exp(-a(xmax-x))/(1 - exp(-a*(xmax-xmin))) if xmin<=x=<xmax
    # p(x) = 0 if x>xmax or x<xmin

    # p(x) = p(xmax)/2 => x = xmax - ln(2)/a
    # p(xmin) = frac*p(xmax) => a = -ln(frac)/(xmax - xmin)

    # rejection sampling with m = 2*a*(xmax - xmin)/(1 - exp(-a*(xmax - xmin)))
    # and q(x) = U(xmin, xmax) = 1/(xmax - xmin), if x lies in [xmin, xmax]

    # note that p(x) =< m*q(x) as required

    m = 2*a*(xmax - xmin)/(1 - math.exp(-a*(xmax - xmin)))
    x = (xmax - xmin)*random() + xmin # generate a random number according to q(x)
    r = 0.5*math.exp(-a*(xmax - x)) # compute p(x)/(m*q(x)) 

    u = random()

    while u>r:

        x = (xmax - xmin)*random() + xmin # generate a random number according to q(x)
        r = 0.5 * math.exp(-a*(xmax - x)) # compute p(x)/(m*q(x))
        u = random()

    sample = x

    return sample


def get_sample(sampling, *args):

    known_samplings = {'exp': exponential, 'texp': truncated_exponential, 'flat': uniform, 'uniform': uniform}
    sample = known_samplings[sampling](*args)

    return sample

def test_sampling(nsamples):

    output_name = 'sampling.txt'

    xmax = 0.6
    xmin = 0.0
    frac = 1.0
    a = -math.log(frac)/(xmax-xmin)
    
    with open(output_name, 'w') as output:

        for i in range(nsamples):

            sample = truncated_exponential(a, xmin, xmax)
            print >> output, sample

