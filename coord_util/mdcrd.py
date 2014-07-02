"""Read and write AMBER mdcrd format."""

import sys
import os.path
import re
import traceback

import split_chunks
import molecule

crd_per_line=10
crd_fmt='%8.3f'
crd_len=8                       # Should be len(crd_fmt)

def use_x_format():
    global crd_per_line, crd_fmt, crd_len
    crd_per_line=6
    crd_fmt='%24.12f'
    crd_len=24

class MDCrdError(RuntimeError): pass

class MDCrdWriter:
    """An interface for writing molecule coordinates to file."""

    def __init__(self, filename, comment, box=False):
	if filename == '-':
	    self.file = sys.stdout
	else:
	    self.file = open(filename, 'w')
        self.file.write('%s\n' % comment)
        self._box=box

    def write(self, molecule):
        every10 = crd_per_line
        for coord in molecule.coordinates:
            self.file.write(crd_fmt % coord)
            every10 -= 1
            if every10 == 0:
                every10 = crd_per_line
                self.file.write('\n')
        if every10 != crd_per_line:
            self.file.write('\n')
        if self._box:
            for dim in molecule.box.dimensions:
                self.file.write(crd_fmt % dim)
            for angle in molecule.box.angles:
                self.file.write(crd_fmt % angle)
            self.file.write('\n')
        
    def close(self):
        self.file.close()


def write_mdcrd_coordinates(comment, filename, coords):
    writer = MDCrdWriter(filename, comment)
    for coord in coords:
        writer.write(molecule.Molecule(comment, ['?'] * (len(coord)/3), coord))
    
    

def write_mdcrds(filename, mols, comment=None, box=False):
    """Write the list of molecules to an mdcrd file."""
    if not comment:
        comment = "Created by molecule.py."
    writer = MDCrdWriter(filename, comment, box=box)
    for mol in mols:
        writer.write(mol)

def count_mdcrds(crd_filename, num_atoms, box=False):
    """Count the number of molecules in an mdcrd file."""
    reader = MDCrdReader(crd_filename, num_atoms=num_atoms, box=box)
    count = 0
    for mol in reader.read():
        count = count + 1
    return count

def mdcrds_in_file(crd_filename, num_atoms=None, atom_names=None, name='mdcrd mol', box=False):
    """Return the list of all molecules in an mdcrd file."""
    reader = MDCrdReader(crd_filename, num_atoms=num_atoms, atom_names=atom_names, name=name, box=box)
    for mol in reader.read():
        yield mol

def floatx(x):
    """Return a float or 9999.999 for ********"""
    try:
        return float(x)
    except ValueError:
        x = x.strip()
        if x == '********':
            print 'WARNING: treating ******** as 9999.999 in mdcrd file.'
            return 9999.999
        elif x[1:].find('-') > 0 or x[1:].find('+') > 0:
            mantissa_start = x[1:].find('-') + x[1:].find('+') + 2
            return float(x[:mantissa_start] + 'E' + x[mantissa_start:])
        else:
            raise

def read_mdcrd_chunks(file, name, atom_names, num_coords, box=False):
    """Yield coordinates from single chunk of an mdcrd file."""
    coords = []
    try:
        for (line_num, line) in enumerate(file):
            new_coords = map(floatx, split_chunks.split_chunks(line, crd_len)[:-1])
            if len(new_coords) == 0:
                # If we find no coords on some line, it must be the last line containing text.
                if len(line.split()) != 0:
                    raise MDCrdError("Encountered improperly formatted mdcrd line.")
                for following_line in file:
                    if len(following_line.split()) != 0:
                        raise MDCrdError("Line without coordinates in mdcrd file")
                break
            if len(new_coords) != min(crd_per_line, num_coords - len(coords)):
                raise MDCrdError("Encountered incorrectly formatted line while reading.  %d coordinates found on a line where I expected %d." % (len(new_coords), min(crd_per_line, num_coords - len(coords))))
            coords.extend(new_coords)
            if len(coords) == num_coords:
                if box:
                    for line in file:
                        line_parts = line.split()
                        if len(line_parts) not in [3,6]:
                            raise MDCrdError("Invalid line for box: %s" % line)
                        numbers = [float(x) for x in line_parts]
                        break
                    yield molecule.Molecule(name, atom_names, coords, box=molecule.Box(numbers[0:3], numbers[3:6]))
                else:
                    yield molecule.Molecule(name, atom_names, coords)
                coords = []
    except GeneratorExit:
        pass
    except Exception:
        raise MDCrdError("%s\nError while reading line #%d: '%s'" % (traceback.format_exc(), line_num + 1, line))


class MDCrdReader:
    """An interface for reading a list of molecules from mdcrd format."""

    def __init__(self, crd_filename, num_atoms=None, name='mdcrd mol', atom_names=None, box=False):
        assert atom_names != None or num_atoms != None, "either atom_names or num_atoms must be provided."
        assert atom_names == None or num_atoms == None or len(atom_names) == num_atoms, "the number of atom_names and num_atoms do not match."
            
        self.comment = "Nothing read."
        self.name = name
        if atom_names:
            self.atom_names = atom_names
        else:
            self.atom_names = ['??'] * num_atoms
        if not num_atoms:
            num_atoms = len(self.atom_names)
        self.num_coords = molecule.Molecule.default_ndof * len(self.atom_names)
        self.crd_filename = crd_filename
        self.__open()
        self._box=box

    def __open(self):
        if os.path.splitext(self.crd_filename)[1] == '.gz':
            import gzip
            self.file = gzip.open(self.crd_filename)
        else:
            self.file = open(self.crd_filename)
        
    def read(self):
        try:
            self.comment = self.file.readline()[:-1]
            for mol in read_mdcrd_chunks(self.file, self.name, self.atom_names, self.num_coords, box=self._box):
                yield mol
        except GeneratorExit:
            pass
        except Exception:
            raise MDCrdError('%s\n Failure while reading mdcrd file "%s"' % (traceback.format_exc(), self.crd_filename))
        finally:
            self.file.close()

        

class MultiMDCrdReader:
    """An interface for reading from a list of mdcrd files.
    
    mdcrd file names provided are popped from the end of the list."""

    def __init__(self, crd_filenames, num_atoms=None, name='mdcrd mol', atom_names=None, box=False):
        assert atom_names != None or num_atoms != None, "either atom_names or num_atoms must be provided."
        assert atom_names == None or num_atoms == None or len(atom_names) == num_atoms, "the number of atom_names and num_atoms do not match."
            
        self.comment = "Nothing read."
        self.name = name
        if atom_names:
            self.atom_names = atom_names
        else:
            self.atom_names = ['??'] * num_atoms
        self.num_coords = 3 * len(self.atom_names)
        self.crd_filenames = crd_filenames
        self._box=box
        self.open_next()

    def open_next(self):
        """Open the next mdcrd file in the list.  Return True if something was opened."""
        if self.crd_filenames == []:
            return False
        mdcrd_file_name = self.crd_filenames.pop()
        self.reader = MDCrdReader(mdcrd_file_name, atom_names=self.atom_names, name=self.name, box=self._box)
        return True
        
    def read(self):
        another_mol_to_read = True
        while another_mol_to_read:
            for mol in self.reader.read():
                yield mol
            another_mol_to_read = self.open_next()
                
            
                    
                

