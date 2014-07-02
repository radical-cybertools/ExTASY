"""Reader for gro format files."""

import os
import xdrfile
import itertools as it
import molecule
from xdrfile import TRR
import numpy as np

class TrrError(Exception):
    pass


def read_next_trr_frame(frame, natoms):
    name = str(frame.time)
    time = frame.time
    num_atoms = natoms
    ndof = 3
    box = molecule.Box(dimensions=frame.box*10.0)
    monomers = []
    atom_names=[]
    atom_coords=[]
    for count, x in enumerate(frame.x):
        atom_names.append(count)
        x0, x1, x2 = float(10.*x[0]), float(10.*x[1]), float(10.*x[2])
        atom_coords.append([x0, x1, x2])

    atom_velocities = None
    if frame.v is not None:
        atom_velocities=[]
        for v in frame.v:
            v0, v1, v2 = float(10.*v[0]), float(10.*v[1]), float(10.*v[2])
            atom_velocities.append([v0, v1, v2])

    mol = molecule.Molecule(name, atom_names, atom_coords, box, ndof, atom_velocities)
    mol.time = time

    return mol

class Reader(object):
    
    def __init__(self, filename, **kwargs):
        self.filename = filename
        self._reader = TRR.TRRReader(filename)

    def read(self):
        for frame in self._reader:
            mol = read_next_trr_frame(frame, self._reader.numatoms)
            yield mol

    def close(self):
        self._reader.close_trajectory()


class Frame(object):

    def __init__(self, mol):

        self.mol = mol


    @property
    def x(self):
        x =  np.array(self.mol.atom_coords, dtype=np.float32)#.transpose()
        x /= 10.
        return x

    @property
    def v(self):
        if self.mol.velocity is not None:
            v =  np.array(self.mol.atom_velocities, dtype=np.float32)#.transpose()
            v /= 10.
        else:
            v = np.zeros((3,self.mol.num_atoms), dtype=np.float32)
        return v

    
    @property
    def time(self):
        return 0.

    @property
    def step(self):
        return 0

    @property 
    def numatoms(self):
        return self.mol.num_atoms 

    @property
    def box(self):
        try:
            b =  np.array(self.mol.box.dimensions, dtype=np.float32)
        except AttributeError:
            b = np.zeros((3,3), dtype=np.float32)
        b /= 10.
        return b


class Writer(object):

    def __init__(self, filename):
        self.filename = filename

        self._have_writer = False
        self._numatoms = None

    def _open_writer(self, numatoms):
        self.writer = TRR.TRRWriter(self.filename, numatoms)
        self._numatoms = numatoms

    def write(self, mol):
        if not self._have_writer:
            self._open_writer(mol.num_atoms)
            self._have_writer = True
            
        assert mol.num_atoms == self._numatoms

        writer = self.writer

        frame = Frame(mol)

        writer.write_next_timestep(frame)

        
    def close(self):
        if self._have_writer:
            self.writer.close_trajectory()


def write_to_trr(filename, xs, vs=None):
    writer = Writer(filename)

    if vs is None:
        vs = [None for x in xs]

    num_atoms = None
    for x, v in it.izip(xs, vs):
        if num_atoms is None:
            num_atoms = len(x)/3
        assert len(x)/3 == num_atoms
        mol = molecule.Molecule('trr mol', ['?'] * num_atoms, x, velocity=v)
        writer.write(mol)
    writer.close()
    
def read_from_trr(filename):

    reader = Reader(filename)

    for mol in reader.read():
        yield mol

    reader.close()
        

#    def close(self):
#        self.file.close()
