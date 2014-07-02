"""Reader for gro format files."""

import os
import molecule
from xdrfile import XTC

class XtcError(Exception):
    pass


def read_next_xtc_frame(frame, natoms):
    name = str(frame.time)
    time = frame.time
    num_atoms = natoms
    box = molecule.Box(dimensions=frame.box*10.0)
    monomers = []
    atom_names=[]
    atom_coords=[]
    atom_velocities=[]
    for count, x in enumerate(frame.x):
        atom_names.append(count)
        x0, x1, x2 = float(10.*x[0]), float(10.*x[1]), float(10.*x[2])
        atom_coords.append([x0, x1, x2])

    mol = molecule.Molecule(name, atom_names, atom_coords, box)
    mol.time = time

    return mol

class Reader(object):
    
    def __init__(self, filename, **kwargs):
        self.filename = filename
        file = self.file = XTC.XTCReader(filename)
        natoms = self.natoms = file.numatoms

    def read(self):
        for frame in self.file:
            mol = read_next_xtc_frame(frame, self.natoms)
            yield mol

#    def close(self):
#        self.file.close()
