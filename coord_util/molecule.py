"""Class representing molecule geometries."""

import sys
import os.path
import re
import traceback

# I really want resist requiring numpy, since it isn't always available.

def build_coordinates(coords):
    """build the coordinate data structure."""
    final_coords = []
    if len(coords) == 0:
        return final_coords
    # The coords may be a list of tuples, or flat coordinates
    if isinstance(coords[0], tuple) or isinstance(coords[0], list):
        for coord in coords:
            if not isinstance(coord, tuple) and not isinstance(coord, list):
                raise MoleculeError("Not all coordinates are tuples or lists: %s" % coord )
            for x in coord:
                if not isinstance(x, float):
                    raise MoleculeError("Invalid coordinate type: %s" % type(x))
            final_coords.extend(coord)
    elif isinstance(coords[0], float):
        for coord in coords:
            if not isinstance(coord, float) and not isinstance(coord, int):
                raise MoleculeError("Invalid coordinate: %s" % coord)
            final_coords.append(coord)
    else:
        raise MoleculeError("Unknown coordinate type: %s" % type(coords[0]))
    return final_coords
    

def parse_atom_coords(coordinates, ndof=3):
    num_atoms = len(coordinates)/ndof
    return [coordinates[ndof*offset:ndof*offset+ndof] for offset in xrange(num_atoms)]

class Box:
    def __init__(self, dimensions, angles=[]):
        if len(dimensions) != 3:
            raise MoleculeError("Wrong number of dimensions: %s" % len(dimensions))
#        if not all(dim >= 0.0 for dim in dimensions):
        for dim in dimensions:
            try:
                for d in dim:
                    if d < 0.0:
                        raise MoleculeError("Box dimensisons are not all positive %s " % dimensions)
            except:
                if dim < 0.0:
                    raise MoleculeError("Box dimensisons are not all positive %s " % dimensions)

        self.dimensions = dimensions

        if len(angles) not in [0,3]:
            raise MoleculeError("Wrong number of angles: %s" % len(angles))
        self.angles = angles

class MoleculeError(RuntimeError): pass

class Molecule(object):
    """Abstract interace to the molecule type."""

    default_ndof=3

    def __init__(self, name, atom_names, coordinates, box=None, ndof=None, velocity=None):
        self.coordinates = build_coordinates(coordinates)
        if velocity is not None:
            self.velocity = build_coordinates(velocity)
        else:
            self.velocity = None
        self.atom_names = atom_names
        if ndof:
            self.ndof = ndof
        else: 
            self.ndof = self.default_ndof

        if self.ndof *len(self.atom_names) != len(self.coordinates):
            raise MoleculeError("atom_names and coordinates dimensions do not match: %s != %s" % (self.ndof *len(self.atom_names), len(self.coordinates)))
        self.name = name
        if box and not isinstance(box, Box):
            raise MoleculeError("Non-box type provided as box: %s" % box)
        self.box = box


    @property
    def num_atoms(self):
        return len(self.atom_names)

    @property
    def atom_coords(self):
        return parse_atom_coords(self.coordinates, ndof=self.ndof)

    @property
    def atom_velocities(self):
        return parse_atom_coords(self.velocity, ndof=self.ndof)

    def get_atom_names(self):
        return self.atom_names

    def set_coords(self, coords):
        self.coordintes = coords

    def get_num_atoms(self):
        return self.num_atoms
           
    def get_atom_idx(self, atom_identifier):
        """Return the index of the atom with the given name."""
        if type(atom_identifier) == type(1):
            if atom_identifier < self.get_num_atoms():
                return atom_identifier
            raise MoleculeError("Atom index out of range: %d" % atom_identifier)
        if type(atom_identifier) == type(''):
            try:
                idx = self.atom_names.index(atom_identifier)
            except Exception:
                raise MoleculeError("%s does not name an atom in this molecule" % atom_identifier)
            dup = True
            try:
                self.atom_names[idx+1:].index(atom_name)
            except Exception:
                dup = False
                if dup:
                    raise MoleculeError("Ambiguous atom name: %s" % atom_name)
            return idx
        raise MoleculeError("Unknown atom identifier type: %s" % type(atom_identifier))

    def get_submolecule(self, atom_indices, name=None, atom_names=None):
        """Return a molecule consisting of only the atoms denoted by the indices."""
        indices = [self.get_atom_idx(idx) for idx in atom_indices]
        if atom_names is None:
            sub_names = [self.atom_names[idx] for idx in indices]
        else:
            sub_names = atom_names
            if len(atom_names) != len(atom_indices):
                raise MoleculeError("Number of atom names does not match number of indices.")
        sub_coords = []
        for idx in indices:
            sub_coords.extend(self.coordinates[self.ndof * idx:self.ndof * (idx + 1)])

        if not name is None:
            sub_name = name
        else:
            sub_name = 'sub ' + self.name

        return Molecule(sub_name, sub_names, sub_coords, box=self.box)

    def __str__(self):
        """Give a string representation of the molecule in a gaussian-like format."""
        # The fact that it's gaussian-like is important as gaussian_template module uses this function
        coord_lines = []
        for atm_idx in range(len(self.atom_names)):
            coord_lines.append("%8s%12.6f%12.6f%12.6f" % (self.atom_names[atm_idx], self.coordinates[self.ndof * atm_idx], self.coordinates[self.ndof * atm_idx + 1], self.coordinates[self.ndof * atm_idx + 2]))

        return '\n'.join(coord_lines)

class Polymer(object):
    """A molecule consisting of sub molecules. """

    def __init__(self, monomers, box=None, name=None):
        self.name = name
        self.monomers = monomers
        self.box = box

    def get_atom_names(self):
        atom_names = []
        for monomer in self.monomers:
            atom_names.extend(monomer.get_atom_names())
        return atom_names

    def monomer_names(self):
        names = []
        for monomer in self.monomers:
            names.append(monomer.name)
        return names

    def __str__(self):
        return '\n'.join((str(x) for x in self.monomers))

    def __getattr__(self, name):
        if name == "num_atoms":
            return sum((mol.num_atoms) for mol in self.monomers)
        elif name == "num_monomers":
            return len(self.monomers)
        elif name == "atom_names":
            all_names = []
            for mol in self.monomers:
                all_names += mol.atom_names
            return all_names
        elif name == "atom_coords":
            all_coords = []
            for mol in self.monomers:
                all_coords += mol.atom_coords
            return all_coords
        elif name == "coordinates":
            coordinates = []
            for monomer in self.monomers:
                coordinates.extend(list(monomer.coordinates))
            return build_coordinates(coordinates)
        elif name == "atom_velocities":
            all_velocities = []
            for mol in self.monomers:
                all_velocities += mol.atom_velocities
            return all_velocities
        elif name == "velocity":
            velocity = []
            for monomer in self.monomers:
                velocity.extend(list(monomer.velocity))
            return build_coordinates(velocity)

        return Polymer.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name == "coordinates":
            coord_idx = 0
            for monomer in self.monomers:
                monomer.coordinates = value[coord_idx:coord_idx + monomer.ndof * monomer.num_atoms]
                coord_idx += monomer.ndof * monomer.num_atoms
        else:
            self.__dict__[name] = value
        


    
def get_polymer_backbone(polymer):
    backbone_monomers = []
    for monomer in polymer.monomers:
        backbone_monomers.append(monomer.get_submolecule(['N', 'CA', 'C']))
    return Polymer('backbone of ' + polymer.name, backbone_monomers)
        
    
