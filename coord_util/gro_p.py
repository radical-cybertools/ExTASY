"""Reader for gro format files."""

import itertools as it

import molecule

class GroError(Exception):
    pass


class GroColumnError(GroError):
    # Thrown when the problem may be the crd_column_length
    pass


crd_column_length=7

def read_next_gro_polymer(file, crd_column_length=7):
    try:
        name = file.next().strip()
        try:
            time = float(name.split('=')[1])
        except IndexError:
            time = None
    except StopIteration:
        return None

    try:
        num_atoms = int(file.next())
    except StopIteration:
        raise GroError("File ended unexpectedly when reading number of atoms.")
    last_rdx = -1
    last_resname = ""
    monomers = []
    atom_coords=[]
    atom_velocities=[]
    for count, line in it.izip(xrange(num_atoms), file):
        line = line.rstrip()
        try:
            rdx = int(line[:5])
        except ValueError:
            raise GroError("Malformed residue index in gromacs line '%s'" % line)

        resname = line[5:10]
        if rdx != last_rdx:
            if last_rdx != -1:
                monomer = molecule.Molecule(name=last_resname, atom_names=atom_names, coordinates=atom_coords, velocity=atom_velocities)
                monomers.append(monomer)
            atom_names=[]
            atom_coords=[]
            last_rdx = rdx
            last_resname = resname
        else:
            if resname != last_resname:
                raise GroError("Resname changed without residue index changing.")

        atom_names.append(line[10:15].strip())
        # I don't have a use for atom indices at a moment
        #atom_idx=int(line[15:20]) 
        pos = 20
        try:
            x=10. * float(line[pos:pos+crd_column_length]) # gro coordinates are in NM, multipy by 10. to convert to ANG
        except ValueError:
            raise GroColumnError("Malformed x coordinate, '%s', in gromacs line '%s'" % (line[pos:pos+crd_column_length], line))
        
        pos += crd_column_length
        try:
            y=10. * float(line[pos:pos+crd_column_length])
        except ValueError:
            raise GroColumnError("Malformed y coordinate, '%s', in gromacs line '%s'" % (line[pos:pos+crd_column_length], line))

        pos += crd_column_length
        try:
            z=10. * float(line[pos:pos+crd_column_length])
        except ValueError:
            raise GroError("Malformed z coordinate, '%s', in gromacs line '%s'" % (line[pos:pos_crd_column_length], line))
        atom_coords.append([x, y, z])

        line_len = len(line)
        if line_len > pos + crd_column_length:
            pos += crd_column_length
            try:
                vx=10. * float(line[pos:pos+crd_column_length])
            except ValueError:
                raise GroError("Malformed x velocity '%s', in gromacs line '%s'" % (line[pos:pos+crd_column_length], line))
            pos += crd_column_length
            try:
                vy=10. * float(line[pos:pos+crd_column_length])
            except ValueError:
                raise GroError("Malformed y velocity in gromacs line '%s'" % line)

            pos += crd_column_length
            try:
                vz=10. * float(line[pos:pos+crd_column_length])
            except ValueError:
                raise GroError("Malformed z velocity in gromacs line '%s'" % line)

            atom_velocities.append([vx, vy, vz])
        else:
            atom_velocities.append([0., 0., 0.])


    if count+1 != num_atoms:
        raise GroError("File ended unexpectedly while reading %dth atom in polymer." % (count+1))

        
                
    monomer = molecule.Molecule(name=last_resname, atom_names=atom_names, coordinates=atom_coords, velocity=atom_velocities)
    monomers.append(monomer)

    try:
        box_line = file.next()
    except StopIteration:
        raise GroError("File ended unexpectedly when reading box line.")
    box = molecule.Box(dimensions=[10. * float(x) for x in box_line.split()])

    polymer = molecule.Polymer(monomers=monomers, box=box, name=name)
    polymer.time = time
    return polymer

class Reader(object):
    
    def __init__(self, filename, crd_column_length=7, **kwargs):
        self.filename = filename
        file = self.file = open(filename)
        self.crd_column_length = crd_column_length

    def read(self):
        mol = read_next_gro_polymer(self.file, crd_column_length=self.crd_column_length)
        while mol:
            yield mol
            mol = read_next_gro_polymer(self.file, crd_column_length=self.crd_column_length)

    def close(self):
        self.file.close()
