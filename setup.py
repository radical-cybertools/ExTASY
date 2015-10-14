#!/usr/bin/env python

"""Setup file for ExTASY
"""

__author__ = "Vivek"
__email__ = "vivek.balasubramanian@rutgers.edu"
__copyright__ = "Copyright 2014, The RADICAL Project at Rutgers"
__license__ = "MIT"


""" Setup script. Used by easy_install and pip. """

from setuptools import setup, find_packages, Command
import os

srcroot = os.path.dirname(os.path.realpath(__file__))


#-----------------------------------------------------------------------------
setup_args = {
    'name' : 'Extasy',
    'version' : open ('{0}/VERSION'.format(srcroot), 'r').readline().rstrip(),
    'description' :" A library to run Simulation-Analysis tasks using EnsembleMD",
    'author' : 'RADICAL Group at Rutgers University',
    'author_email' : 'vivek.balasubramanian@rutgers.edu',
    'maintainer' : "Vivek Balasubramanian",
    'maintainer_email' : 'vivek.balasubramanian@rutgers.edu',
    'url' : 'https://github.com/radical-cybertools',
    #'download_url' : 'https://github.com/vivek-bala/ensembleapi/tarball/0.1',
    'license' : 'MIT',
    'keywords' : "molecular dynamics workflow",
    'classifiers' : [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Environment :: Console',
        #'License :: OSI Approved :: MIT',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Topic :: System :: Distributed Computing',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix'
    ],

  

    'package_data' : {'': ['*.sh', 'VERSION', 'VERSION.git']},
    'install_requires' : ['radical.utils'],
  
    'zip_safe' : False,
}

#-----------------------------------------------------------------------------

setup (**setup_args)
