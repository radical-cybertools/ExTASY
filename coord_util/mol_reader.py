import os

class MolReaderError(Exception):
    pass

class MolReaderArgumentError(MolReaderError):
    pass

class MDCrdFormat(object):

    def open(self, filename, kwargs):
        import mdcrd

        if 'num_atoms' not in kwargs or kwargs['num_atoms'] is None:
            raise MolReaderArgumentError("num_atoms are required to open mdcrd files for reading.")
        return mdcrd.MDCrdReader(filename, **kwargs)

# class PDBFormat(object):
#     num_atom_required=True

class GroFormat(object):

    def open(self, filename, kwargs):
        import gro
        # From my interactions with Cecilia, it seems there is no
        # standard crd_column_length.  Even in files output from a
        # single script, the length can change between runs.  So if no
        # crd_column_length was provided, try to guess between two I've seen.
        
        if 'crd_column_length' not in kwargs:
            for col_len in [7, 8]:
                reader = gro.Reader(filename, crd_column_length=col_len, **kwargs)
                try:
                    for x in reader.read():
                        break
                    break
                except gro.GroColumnError:
                    if col_len == 8:
                        raise

            return gro.Reader(filename, crd_column_length=col_len, **kwargs)
        else:
            return gro.Reader(filename, **kwargs)


class DBReader(object):
    
    def open(self, filename, kwargs):
        import trajectory_database as trajdb
        
        return trajdb.Reader(filename, **kwargs)


class XtcFormat(object):
    
    def open(self, filename, kwargs):
        import xtc
        
        return xtc.Reader(filename, **kwargs)


class TrrFormat(object):
    
    def open(self, filename, kwargs):
        import trr
        
        return trr.Reader(filename, **kwargs)


known_formats={'mdcrd':MDCrdFormat(),
               # 'PDB':PDBFormat(),
               'gro':GroFormat(),
               'db':DBReader(),
               'xtc':XtcFormat(),
               'trr':TrrFormat()}

format_aliases={'crd':'mdcrd'}

class MolReaderFormatError(MolReaderError):

    def __init__(self, format, known_formats):
        self.format = format
        self.known_formats = known_formats

    def __str__(self):
        global known_formats
        return 'Unknown molecule file format "%s"\n Available formats are %s.\n' % (self.format, self.known_formats.keys())

def open(filename, format=None, **kwargs):
    global known_formats, format_aliases
    if format is None:
        name, ext = os.path.splitext(filename)      #### for SUSY, filename is gamma_Centers.db =>  ext = .db
        format = ext.split('.')[-1] #### -1 is the last element of the list i.e. format = db

    format = format.lower()
    if format in format_aliases:
        format = format_aliases[format]

    if format not in known_formats:
        raise MolReaderFormatError(format, known_formats)

    return known_formats[format].open(filename, kwargs)    ### known_formats[format] = DBReader() est un objet dont la methode "open" renvoie un objet de type Reader
								### l'attribut "db" de cet objet est le resultat de "open_trajectory_database(filename, create=False)"

def parse_kwargs(kwarg_str):
    """Retrieve the kwarg dictionary from a user input string.

    The expected format is a single string, each argument separated by
    a comma, in the form varname:varvalue."""
    if not kwarg_str:
        return {}
    kwargs = {}
    for kwarg in kwarg_str.split(','):
        varname, varvalue_str = kwarg.split(':')
        varname = varname.strip()
        # Try to convert it to an int or float, otherwise default to string
        try:
            varvalue = int(varvalue_str)
        except ValueError:
            try:
                varvalue = float(varvalue_str)
            except ValueError:
                varvalue = varvalue_str

        kwargs[varname] = varvalue

    return kwargs
