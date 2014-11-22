__author__ = 'vivek'

import os
import sys

if __name__ == '__main__':
    num_CUs = sys.argv[1]
    md_output_file = sys.argv[2]
    path = sys.argv[3]

    with open(md_output_file, 'w') as output_grofile:
        for i in range(0,num_CUs):
            with open('out%s.gro' % i, 'r') as output_file:
                for line in output_file:
                    print >> output_grofile, line.replace("\n", "")
            os.remove('out%s.gro'%i)