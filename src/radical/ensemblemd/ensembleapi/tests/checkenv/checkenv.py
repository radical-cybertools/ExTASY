__author__ = 'vivek'

import radical.ensemblemd.ensembleapi.bin.mdAPI as ensembleapi
import os
import unittest
import sys

DBURL = os.getenv('ENSEMBLE_DBURL')
if DBURL is None:
    print "ERROR: ENSEMBLE_DBURL (MongoDB server URL) is not defined."
    sys.exit(1)


RCONF = os.getenv('ENSEMBLE_RCONF',["file://localhost/home/vivek/MDEnsemble/config/my-futuregrid.json",
          "file://localhost/home/vivek/MDEnsemble/config/my-xsede.json"])

class Remote_Checkenv(unittest.TestCase):

    def setUp(self):

        self.resource_name = os.getenv('ENSEMBLE_RNAME','localhost')
        self.uname = os.getenv('ENSEMBLE_UNAME')
        self.workdir = os.getenv('ENSEMBLE_WORKDIR','/tmp/ensembleapi.sandbox')
        self.pilotsize = os.getenv('ENSEMBLE_NUM_OF_CORES')
        self.numofcus = os.getenv('ENSEMBLE_NUM_OF_TASKS')

    def tearDown(self):
        print 'Checkenv test successful'

    def failUnless(self, expr):
        return self.assertTrue(expr)

    def failIf(self, expr):
        return self.assertFalse(expr)

    def EnvCheck(self):
        obj = ensembleapi.simple(DBURL=DBURL)
        RESOURCE= {
                    #Resource related inputs	--MANDATORY
                    'remote_host' : self.resource_name,
                    'remote_directory' : self.workdir,
                    'username' : self.uname,
                    'number_of_cores' : self.pilotsize,
                    'walltime' : 5
                }
        obj.startResource(resource_info=RESOURCE,RCONF=RCONF)
        result = obj.checkEnv()
        sys.exit(result)
