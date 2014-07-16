import os
dir = os.path.dirname(os.path.realpath(__file__))
version = out=open ("%s/VERSION" % dir, 'r').read().strip()
