import os
import sqlite3
import contextlib as cl
import itertools as it
import time

import numpy as np

import molecule

class TrajectoryDatabaseError(sqlite3.DatabaseError):
    pass

class NotATable(TrajectoryDatabaseError):
    pass

class TrajectoryKeyTableError(TrajectoryDatabaseError):
    pass

class TrajectoryKeyTable(object):

    table_name='TrajectoryKeys'

    _trajectorykey_column='TrajectoryKey'

    @property
    def trajectorykey_column(self):
        return '%s.%s' % (self.table_name, self._trajectorykey_column)

    def count(self, c):
        table_name = self.table_name
        c.execute("SELECT COUNT(*) FROM %(table_name)s" % locals())
        try:
            the_count = c.fetchone()[0]
        except Exception:
            the_count = 0
        return the_count

    def create_sql_table(self, c):
        table_name = self.table_name
        trajectorykey_column = self._trajectorykey_column
        c.executescript("""CREATE TABLE IF NOT EXISTS %(table_name)s (
%(trajectorykey_column)s INTEGER PRIMARY KEY
);""" % locals())


    def max_trajectorykey(self, c):
        table_name = self.table_name
        trajectorykey_column = self._trajectorykey_column
        c.execute("""SELECT MAX(%(trajectorykey_column)s) FROM %(table_name)s""" % locals())
        max_key = c.fetchone()[0]
        if max_key is None:
            max_key = 0
        return max_key

    def insert_new_trajectory_cursor(self, c, trajectorykey=None, **kwargs):
        table_name = self.table_name

        if trajectorykey is None:
            c.execute("""INSERT OR REPLACE INTO %(table_name)s VALUES (NULL)""" % locals(), ())
        else:
            try:
                c.execute("""INSERT OR FAIL INTO %(table_name)s VALUES (?)""" % locals(), (trajectorykey,))
            except sqlite3.IntegrityError:
                raise TrajectoryKeyTableError("Trajectorykey '%s 'is invalid or already exists in database." % trajectorykey)


        if trajectorykey is not None:
            return trajectorykey
        else:
            return c.lastrowid


    def insert_new_trajectories_cursor(self, c, trajectorykeys):
        table_name = self.table_name

        try:
            c.executemany("""INSERT OR FAIL INTO %(table_name)s (TrajectoryKey) VALUES (?)""" % locals(), trajectorykeys)
        except sqlite3.IntegrityError:
            raise TrajectoryKeyTableError("Trajectorykey '%s 'is invalid or already exists in database." % trajectorykeys)


    def num_trajectories(self, c):
        table_name = self.table_name
        trajectorykey_column = self._trajectorykey_column
        c.execute("""SELECT COUNT(%(trajectorykey_column)s) FROM %(table_name)s""" % locals())
        num = c.fetchone()[0]
        if num is None:
            num = 0
        return num

    def trajectorykeys(self, c):
        table_name = self.table_name
        trajectorykey_column = self._trajectorykey_column
        c.execute("""SELECT %(trajectorykey_column)s FROM %(table_name)s""" % locals())
        for row in c:
            yield row[0]

    def trajectorykey_in_table(self, c, trajectorykey):
        table_name = self.table_name
        trajectorykey_column = self._trajectorykey_column
        c.execute("""SELECT %(trajectorykey_column)s FROM %(table_name)s WHERE %(trajectorykey_column)s=?""" % locals(), (trajectorykey,))
        return c.fetchone() is not None
            

class TimeKeyTableError(TrajectoryDatabaseError):
    pass

class SampleKeyTableError(TrajectoryDatabaseError):
    pass

class SampleKeyTable(object):
    
    table_name='SampleKeys'
    _samplekey_column='SampleKey'


    @property
    def samplekey_column(self):
        return '%s.%s' % (self.table_name, self._samplekey_column)

    def create_sql_table(self, c):
        table_name = self.table_name

        samplekey_column = self._samplekey_column
        
        sql = """CREATE TABLE IF NOT EXISTS %(table_name)s (
%(samplekey_column)s INTEGER,
PRIMARY KEY (%(samplekey_column)s));""" % locals()

        if os.getenv('DEBUGSQL'):
            print sql

        c.executescript(sql)

    def new_sample_key(self, c, key=None):
        samplekeys = self.table_name

        if key is None:
            sql = """INSERT OR REPLACE INTO %(samplekeys)s VALUES (NULL)""" % locals()
            args = tuple()
            c.execute(sql,args)
            if os.getenv('DEBUGSQL'):
                print sql, args

            return c.lastrowid
        else:
            sql = """INSERT OR REPLACE INTO %(samplekeys)s (SampleKey) VALUES (?)""" % locals()
            args = (key,)
            c.execute(sql, args)
            if os.getenv('DEBUGSQL'):
                print sql, args

            return key

    def new_sample_keys(self, c, keys):
        samplekeys = self.table_name
        sql = """INSERT OR REPLACE INTO %(samplekeys)s (SampleKey) VALUES (?)""" % locals()
        if os.getenv('DEBUGSQL'):
            print sql
            
        c.executemany(sql, keys)



    def sample_key(self, c, trajectorykey, timekey):
        samplekeys = self.table_name
        trajectorykey_column = self._trajectorykey_column
        timekey_column = self._timekey_column
        c.execute("""SELECT SampleKey FROM %(samplekeys)s WHERE %(trajectorykey_column)s=? AND %(timekey_column)s=?""" % locals(), trajectorykey, timekey)
        samplekey = c.fetchone()[0]
        if samplekey is None:
            raise SampleKeyTableError("No samplekey for (%(trajectorykey_column)s, %(timekey_column)s)==(%s, %s)" % (trajectorykey, timekey))
        return samplekey


    def max_samplekey(self, c):
        samplekeys = self.table_name
        samplekey_column = self._samplekey_column
        c.execute("""SELECT max(%(samplekey_column)s) FROM %(samplekeys)s""" % locals())
        samplekey = c.fetchone()[0]
        if samplekey is None:
            return 0
        return samplekey

class SamplePropertyTable(object):
    """Base class for tables holding properties tied to a SampleKey."""

    def __init__(self, traj_db, samplekey_table):
        self.traj_db = traj_db
        self.samplekey_table = samplekey_table
        self._samplekey_column = samplekey_table._samplekey_column

    def create_sql_table(self, c):
        raise Exception("create_sql_table has not been implemented.")

    def insert(self, c, **kwargs):
        return

    @property
    def samplekeys_table_name(self):
        return self.samplekey_table.table_name

    @property
    def samplekey_column(self):
        return '%s.%s' % (self.table_name, self._samplekey_column)

    @property
    def samplekey_inner_join_stmt(self):
        table_name = self.table_name
        samplekeys_table_name = self.samplekeys_table_name
        samplekey_column = self.samplekey_column
        samplekeys_samplekey_column = self.samplekey_table.samplekey_column
        return '\nINNER JOIN %(table_name)s ON %(samplekey_column)s=%(samplekeys_samplekey_column)s\n' % locals()

    @property
    def property_columns(self):
        raise TrajectoryDatabaseError("property_columns not implemented.")

    def add_tables_lookup(self, tables):
        tables[self.table_name] = self
        return tables


class TrajectoryPropertyTable(SamplePropertyTable):
    """Base class for tables holding properties tied to a TrajectoryKey."""

    def __init__(self, traj_db, samplekey_table, trajectorykey_table):
        SamplePropertyTable.__init__(self, traj_db, samplekey_table)

        self.trajectorykey_table = trajectorykey_table
        self._trajectorykey_column = trajectorykey_table._trajectorykey_column

    @property
    def trajectorykeys_table_name(self):
        return self.trajectorykey_table.table_name

    @property
    def trajectorykey_column(self):
        return '%s.%s' % (self.table_name, self._trajectorykey_column)

    @property
    def trajectorykey_inner_join_stmt(self):
        table_name = self.table_name
        trajectorykeys_table_name = self.trajectorykeys_table_name
        trajectorykey_column = self.trajectorykey_column
        trajectorykeys_trajectorykey_column = self.trajectorykey_table.trajectorykey_column
        return '\nINNER JOIN %(table_name)s ON %(trajectorykey_column)s=%(trajectorykeys_trajectorykey_column)s\n' % locals()


class CoordinateTableError(TrajectoryDatabaseError):
    pass


max_sql_variables=500

class CoordinateTable(SamplePropertyTable):

    table_name = 'Coordinates'

    columns_per_table=max_sql_variables

    @property
    def num_sql_tables(self):
        columns_per_table = self.columns_per_table
        return 1+(self.ndof-1)/columns_per_table

    def num_columns_in_table(self, table_num):
        columns_per_table = self.columns_per_table
        if columns_per_table * (table_num+1) > self.ndof:
            return self.ndof - columns_per_table * table_num
        else:
            return columns_per_table

    def _crd_columns_of_table(self, table_num):
        columns_per_table = self.columns_per_table
        offset = columns_per_table * table_num
        for crdidx in xrange(offset + 1, offset + 1 + self.num_columns_in_table(table_num)):
            yield 'Coord%d' % crdidx

    def table_name_of_table(self, table_num):
        if table_num == 0:
            return self.table_name
        else:
            return self.table_name + str(table_num+1)

    @property
    def table_names(self):
        for table_num in xrange(self.num_sql_tables):
            yield self.table_name_of_table(table_num)

    def add_tables_lookup(self, tables):
        for table_name in self.table_names:
            tables[table_name] = self
        return tables

    @property
    def _crd_columns(self):
        crd_columns = []
        for crdidx in xrange(1, self.ndof+1):
            crd_columns.append('Coord%d' % crdidx)
        return crd_columns



    def crd_columns_of_table(self, table_num):
        crd_columns = []

        table_name = self.table_name_of_table(table_num)

        for crd_column in self._crd_columns_of_table(table_num):
            crd_columns.append('%s.%s' % (table_name, crd_column))

        return crd_columns

    @property
    def crd_columns(self):

        crd_columns = []

        for table_num in xrange(self.num_sql_tables):
            for crd_column in self.crd_columns_of_table(table_num):
                crd_columns.append(crd_column)

        return crd_columns


    @property
    def crd_names(self):
        return ', '.join(self.crd_columns)

    @property
    def _crd_names(self):
        return ', '.join(self._crd_columns)

    def crd_names_of_table(self, table_num):
        return ', '.join(self.crd_columns_of_table(table_num))


    def _crd_names_of_table(self, table_num):
        return ', '.join(self._crd_columns_of_table(table_num))


    # @property
    # def table_crd_names(self):
    #     table_name = self.table_name
    #     return ','.join(['%s.%s' % (table_name, crd_name) for crd_name in self.crd_column_names])

    @property
    def crd_qs(self):
        return ','.join(('?' for name in xrange(self.ndof)))

    def crd_qs_of_table(self, table_num):
        return ','.join(('?' for name in xrange(self.num_columns_in_table(table_num))))


    def crd_schema_lines(self):
        for crd_column_name in self._crd_columns:
            yield crd_column_name + ' INTEGER'

    @property
    def crd_schema(self):
        return ',\n'.join(list(self.crd_schema_lines()))

    @property
    def ndof(self):
        return self.traj_db.ndof

    def num_samples(self, c):
        coordinates = self.table_name
        samplekey_column = self.samplekey_column
        c.execute("""SELECT COUNT(%(samplekey_column)s) FROM %(coordinates)s""" %  locals())
        count = c.fetchone()[0]
        return count

    def create_sql_table(self, c):
        table_name = self.table_name
        column_per_table = self.columns_per_table
        samplekeys_table_name = self.samplekeys_table_name
        samplekeys_samplekey = self.samplekey_table._samplekey_column
        samplekey = self._samplekey_column

        table_creation_sql= """CREATE TABLE IF NOT EXISTS %%s (
%(samplekey)s INTEGER,
%%s,
PRIMARY KEY (%(samplekey)s),
FOREIGN KEY (%(samplekey)s) REFERENCES %(samplekeys_table_name)s (%(samplekey)s)
);""" % locals()


        columns_per_table = self.columns_per_table
        ndof = self.ndof

        current_schema_lines = []
        current_table_name = table_name
        num_tables = 1
        
        for count, single_schema_line in enumerate(self.crd_schema_lines()):
            current_schema_lines.append(single_schema_line)

            if count % columns_per_table == columns_per_table - 1:
                sql = table_creation_sql % (current_table_name, ',\n'.join(current_schema_lines))
                if os.getenv('DEBUGSQL'):
                    print sql
                c.executescript(sql)
                current_schema_lines = []
                num_tables += 1
                current_table_name = table_name + str(num_tables)
            
        if current_schema_lines != []:
            sql = table_creation_sql % (current_table_name, ',\n'.join(current_schema_lines))
            c.executescript(sql)

    @property
    def samplekey_inner_join_stmt(self):
        samplekeys_table_name = self.samplekeys_table_name
        samplekey_column = self.samplekey_column
        samplekeys_samplekey_column = self.samplekey_table.samplekey_column

        lines = []
        for table_num in xrange(self.num_sql_tables):
            table_name = self.table_name_of_table(table_num)
            samplekey_column = table_name + '.' + self._samplekey_column
            lines.append('INNER JOIN %(table_name)s ON %(samplekey_column)s=%(samplekeys_samplekey_column)s' % locals())

        return '\n' + '\n'.join(lines) + '\n'



    def insert_many(self, c, iterator):
        columns_per_table = self.columns_per_table
        ndof = self.ndof
        
        sqls = []
        for table_num in xrange(self.num_sql_tables):
            table_name = self.table_name_of_table(table_num)
            
            crd_names = self._crd_names_of_table(table_num)

            offset = columns_per_table * table_num

            samplekey_column = self._samplekey_column

            crd_qs = self.crd_qs_of_table(table_num)

            sql = """INSERT OR REPLACE INTO %(table_name)s (%(samplekey_column)s, %(crd_names)s) Values (?,%(crd_qs)s)""" % locals()
            if os.getenv('DEBUGSQL'):
                print sql
            sqls.append(sql)



        for row in iterator:
            samplekey = row[0]

            for table_num, sql in enumerate(sqls):
                offset = columns_per_table * table_num
                args = (samplekey,) + tuple(row[1+offset:1+min(offset+columns_per_table, ndof)])

                try:
                    c.execute(sql, args)            
                except:
                    if os.getenv('DEBUGSQL'):
                        print 'Failed: %s, %s' % (sql, args)
                    raise


    def insert(self, c, samplekey, coords=None, **kwargs):
        self.insert_many(c, [(samplekey,) + tuple(coords)])

class MomentumTableError(CoordinateTableError):
    pass

class MomentumTable(CoordinateTable):
    table_name='Momenta'

    def insert(self, c, samplekey, p=None, **kwargs):
        if p is None:
            raise MomentumTableError("Momentum argument (p) not provided for insert.")
        CoordinateTable.insert(self, c, samplekey, coords=p)



class EnergyTableError(TrajectoryDatabaseError):
    pass

class EnergyTable(SamplePropertyTable):
    
    table_name='Energies'

    _energy_column='Energy'

    @property
    def property_columns(self):
        return [self._energy_column]


    @property
    def energy_column(self):
        return '%s.%s' % (self.table_name, self._energy_column)

    def create_sql_table(self, c):
        energies = self.table_name
        samplekeys_table_name = self.samplekeys_table_name
        samplekey_column = self.samplekey_column
        samplekeys_samplekey_column=self.samplekey_table._samplekey_column
        energy_column = self._energy_column
        c.executescript("""CREATE TABLE IF NOT EXISTS %(energies)s (
%(samplekey_column)s INTEGER,p
%(energy_column)s REAL,
PRIMARY KEY (%(samplekey_column)s),
FOREIGN KEY (%(samplekey_column)s) REFERENCES %(samplekeys_table_name)s (%(samplekeys_samplekey_column)s)
);""" % locals())

    def insert(self, c, samplekey, energy=None, **kwargs):
        if energy is None:
            raise EnergyTableError("energy argument (energy) not provided for insert.")
        energies = self.table_name
        samplekey_column = self._samplekey_column
        energy_column = self.energy_column
        c.execute("""INSERT OR REPLACE INTO %(energies)s (%(samplekey_column)s, %(energy_column)s) VALUES (?,?)""" % locals(), (samplekey, energy))


class VarsTableError(TrajectoryDatabaseError):
    pass

class VarsTable(object):
    """A table to arbitrary variables for a databse."""
    
    table_name='Vars'

    def create_sql_table(self, c):
        table_name = self.table_name

        c.executescript("""CREATE TABLE IF NOT EXISTS %(table_name)s (
Name TEXT,
Value
);""" % locals())

    def get_var(self, c, name):
        table_name = self.table_name
        c.execute("""SELECT Value FROM %(table_name)s WHERE Name=?""" % locals(), (name,))
        
        r = c.fetchone()
        if r is None:
            raise VarsTableError("""No such var in Vars table: '%s'""" % name)
        
        return r[0]

    def set_var(self, c, name, value, replace=True):
        table_name = self.table_name
        
        if replace:
            replace = "OR REPLACE"
        else:
            replace = ""
            
        c.execute("""INSERT %(replace)s INTO %(table_name)s (Name, Value) VALUES (?, ?)""" % locals(), (name, value))

def split_column(column_name):
    parts = column_name.split('.')
    n = len(parts)
    if n == 1:
        return '', parts[0]
    elif n == 2:
        return parts[0], parts[1]
    else:
        raise Exception('Unable to split column name: "%s"' % column_name)


class ClassTableError(TrajectoryDatabaseError):
    pass

class ClassTable(SamplePropertyTable):

    table_name='Classes'
    _class_column='Class'

    def __init__(self, traj_db, samplekey_table, table_name=None, class_column=None):
        SamplePropertyTable.__init__(self, traj_db, samplekey_table)

	if table_name is not None:
	    self.table_name = table_name
	if class_column is not None:
	    self._class_column = class_column
    
    @property
    def property_columns(self):
        return [self._class_column]


    @property
    def class_column(self):
        return '%s.%s' % (self.table_name, self._class_column)

    class_type='REAL'

    def create_sql_table(self, c):
        table_name = self.table_name

        samplekeys_table_name = self.samplekeys_table_name
        samplekeys_samplekey = self.samplekey_table._samplekey_column
        samplekey = self._samplekey_column

        class_column = self._class_column

        class_type = self.class_type

        # c.executescript("""DROP TABLE IF EXISTS %(table_name)s;""" % locals())
        sql = """CREATE TABLE IF NOT EXISTS %(table_name)s (
%(samplekey)s INTEGER PRIMARY KEY,
%(class_column)s %(class_type)s,
FOREIGN KEY (%(samplekey)s) REFERENCES %(samplekeys_table_name)s (%(samplekeys_samplekey)s)
);""" % locals()

        if os.getenv('DEBUGSQL'):
            print 'create_sql_table ', sql


        try:
            c.executescript(sql)
        except:
            if os.getenv('DEBUGSQL'):
                print 'exception whie executing SQL statement:'
                print 'exception sql = ', sql
            raise


    def insert_many(self, c, iterator):
        table_name = self.table_name

        samplekey = self._samplekey_column

        class_column = self._class_column

        sql = "INSERT OR REPLACE INTO %(table_name)s (%(samplekey)s, %(class_column)s) VALUES (?,?)" % locals()
        if os.getenv('DEBUGSQL'):
            print 'insert_many ', sql

        c.executemany(sql, iterator)

    insert_classes_many=insert_many


class TimesTable(ClassTable):
    
    table_name='Times'
    _class_column='Time'

    time_column=ClassTable.class_column

class TrajectoriesTable(ClassTable):
    
    table_name='Trajectories'
    _class_column='TrajectoryKey'
    class_type='INTEGER'

    trajectory_column=ClassTable.class_column

    # TODO: override __init__ to require trajectorykey table

    def create_sql_table(self, c):
        table_name = self.table_name

        trajectorykeys_table_name = 'TrajectoryKeys' # TODO: this should on __init__ 
        trajectorykey_column = 'TrajectoryKey'

        samplekeys_table_name = self.samplekeys_table_name
        samplekeys_samplekey = self.samplekey_table._samplekey_column
        samplekey = self._samplekey_column

        class_column = self._class_column

        class_type = self.class_type

        # c.executescript("""DROP TABLE IF EXISTS %(table_name)s;""" % locals())
        sql = """CREATE TABLE IF NOT EXISTS %(table_name)s (
%(samplekey)s INTEGER,
%(class_column)s %(class_type)s,
PRIMARY KEY (%(samplekey)s, %(class_column)s)
FOREIGN KEY (%(samplekey)s) REFERENCES %(samplekeys_table_name)s (%(samplekeys_samplekey)s)
FOREIGN KEY (%(class_column)s) REFERENCES %(trajectorykeys_table_name)s (%(trajectorykey_column)s)
);""" % locals()

        if os.getenv('DEBUGSQL'):
            print 'create_sql_table ', sql


        c.executescript(sql)
    

class DatabaseMixin(object):
    
    def __init__(self, dbname, *args, **kwargs):

        if 'create' in kwargs:
            create = kwargs['create']
        else:
            create = None

        self.dbname = dbname

        if create is not None:
            
            exists = os.path.exists(dbname)
            
            if create:
                if exists:
                    os.remove(dbname)
            else:
                
                if not exists:
                    raise TrajectoryDatabaseError("Database does not exist: %s" % dbname)
        create = not os.path.exists(dbname) # if the file dbname exists : create = False 

        kwargs['create'] = create # Transmit the create status to subclasses

        sqlite3.register_adapter(np.float32, float)
        sqlite3.register_adapter(np.float64, float)
        self.sql_db = sqlite3.connect(dbname)
        
        self.vars = VarsTable()
        with self.cursor() as c:
            try:
                self.vars.create_sql_table(c)
            except sqlite3.OperationalError:
                pass

        self.init_tables(*args, **kwargs)
        
        if create:
            with self.session():
                self.create_sql_tables(*args, **kwargs)


    def init_tables(self, *args, **kwargs):
        self.tables = {}


    def create_sql_tables(self, *args, **kwargs):
        pass

        
class TrajectoryDatabase(DatabaseMixin):
    """MD coordinate trajectory database.    """

    def __init__(self, *args, **kwargs):
        self.__timekey_cache = None
        self.__last_checkpoint = time.time()
        super(TrajectoryDatabase, self).__init__(*args, **kwargs)
        

    def init_tables(self, *args, **kwargs):
        super(TrajectoryDatabase, self).init_tables(*args, **kwargs)

        if 'ndof' in kwargs:
            ndof = kwargs['ndof']
        else:
            ndof = None

        try:
            # self.ndof is a property that looks in the VarsTable
            previous_ndof = self.ndof
        except VarsTableError:
            if ndof is None:
                raise TrajectoryDatabaseError("ndof is not present in Vars table or __init__ kwargs.")
            with self.session():
                previous_ndof = self.ndof = ndof

        if ndof is not None:
            if previous_ndof != ndof:
                raise TrajectoryDatabaseError("__init__ kwargs ndof not equal to ndof in Vars table.")

        self.trajectorykeys = TrajectoryKeyTable()
        self.samplekeys = SampleKeyTable()

         # Implicitly add a default table class for all the sample
         # property tables already in the database.  More specific
         # classes (such as CoordinateTable) will replace these
         # default tables when provided.
        list(self.sample_property_tables)
        # for table in self.sample_property_tables:
        # print 'TABLE: %30s  CLASS_COLUM %60s' % (table.table_name, table.class_column)


        self.momenta = self._add_sample_table(MomentumTable(self, self.samplekeys))
        self.coordinates = self._add_sample_table(CoordinateTable(self, self.samplekeys))
        self.times = self._add_sample_table(TimesTable(self, self.samplekeys))
        self.trajectories = self._add_sample_table(TrajectoriesTable(self, self.samplekeys))


    def create_sql_tables(self, *args, **kwargs):
        super(TrajectoryDatabase, self).create_sql_tables(*args, **kwargs)
        with self.cursor() as c:
            self.trajectorykeys.create_sql_table(c)
            self.samplekeys.create_sql_table(c)
            self.coordinates.create_sql_table(c)
            self.momenta.create_sql_table(c)
            self.times.create_sql_table(c)
            self.trajectories.create_sql_table(c)
            

    def _add_sample_table(self, table, create=False):

        self.tables = table.add_tables_lookup(self.tables)

        if create:
            with self.cursor() as c:
                table.create_sql_table(c)

        return table

    def _add_trajectory_table(self, table):
        # TODO: let trajectory property tables add themselves
        self.tables[table.table_name] = table
        return table

    def add_class_table(self, table_name, class_column=None, create=False):
        table = self._add_sample_table(ClassTable(self, self.samplekeys, table_name=table_name, class_column=class_column),
                                       create=create)
        
        return table

    def insert_classes_many(self, table, iterator):

        if not isinstance(table, SamplePropertyTable):
            class_table = self.find_table(table)
        else:
            class_table = table
	with self.cursor() as c:
	    class_table.insert_classes_many(c, iterator)


    # def insert_many(self, table, iterator):
    #     with self.cursor() as c:
    #         table.insert_many(c, iterator)
        

    #### General database tools
    def close(self):
        self.sql_db.close()

    @cl.contextmanager
    def session(self):
        try:
            yield
            self.sql_db.commit()
        except:
            self.sql_db.rollback()
            raise

    @cl.contextmanager
    def cursor(self):
        c = self.sql_db.cursor()
        try:
            yield c
        finally:
            c.close()

    @property
    def table_names(self):
        with self.cursor() as c:
            for row in c.execute("""SELECT name FROM sqlite_master"""):
                yield row[0]


    def table_columns(self, table_name):
        old_factory = self.sql_db.row_factory
        try:
            self.sql_db.row_factory = sqlite3.Row
            with self.cursor() as c:
                try:
                    c.execute("""SELECT * FROM %s""" % table_name)
                except sqlite3.OperationalError:
                    return []
                r = c.fetchone()
                # if r is None, then I won't get anything to procure the column names from..
                try:
                    return [column.upper() for column in r.keys()]
                except AttributeError:
                    # print 'WARNING: %s is empty' % table_name
                    return []
        finally:
            self.sql_db.row_factory = old_factory

    @property
    def sample_property_tables(self):
        for table_name in self.table_names:
            table_columns = self.table_columns(table_name)
            if len(table_columns) != 2:
                continue
            if self.samplekeys._samplekey_column.upper() not in table_columns:
                continue

            # If we already have a class for the table return that,
            # otherwise make a new one and return that
            try:
                yield self.find_table(table_name)
            except NotATable:
                class_columns = [column for column in table_columns if column != self.samplekeys._samplekey_column.upper()]
                yield self._add_sample_table(ClassTable(self, self.samplekeys, table_name=table_name, class_column=class_columns[0]))
            

    def checkpoint(self, check_time=5*60.):
        current_checkpoint = time.time()
        delta = current_checkpoint - self.__last_checkpoint
        if delta > check_time:
            self.sql_db.commit()
            self.__last_checkpoint = current_checkpoint
        


    def execute_sql(self, sql, args=tuple()):
        with self.cursor() as c:
            if os.getenv('DEBUGSQL'):
                print sql, args
            for x in c.execute(sql, args):
                yield x

    @property
    def ndof(self):
        try:
            return self.__ndof
        except AttributeError:
            with self.cursor() as c:
                self.__ndof = self.vars.get_var(c, 'ndof')
            return self.__ndof

    @ndof.setter
    def ndof(self, new_ndof):
        with self.cursor() as c:
            self.vars.set_var(c, 'ndof', new_ndof)
        self.__ndof = new_ndof


    def find_table(self, table_name):
        if table_name == self.samplekeys.table_name:
            return self.samplekeys
        try:
            return self.tables[table_name]
        except KeyError:
            raise NotATable("No such table '%s'.  Available tables are %s" % (table_name, self.tables.values()))


    def select_trajectories(self, column_names):
        table_names = set([])
        for column in column_names:
            table_name, column_name = split_column(column)
            table_names.add(table_name)

        trajectorykeys = self.trajectorykeys.table_name
        tables = [self.find_table(table_name) for table_name in table_names if table_name != trajectorykeys]

        inner_join = ''
        for table in tables:
            inner_join += table.trajectorykey_inner_join_stmt

        columns = ', '.join(column_names)

        args = tuple()

        with self.cursor() as c:
            sql = "SELECT %(columns)s FROM %(trajectorykeys)s %(inner_join)s" % locals()
	    try:
                if os.getenv('DEBUGSQL'):
                    print 'select_trajectories ', sql, args
		c.execute(sql, args)
		for row in c:
		    yield row
	    except:
                if os.getenv('DEBUGSQL'):
                    print 'exception whie executing SQL statement:'
                    print 'exception sql = ', sql, args
		raise



        
    
    def select_samples(self, column_names, orderby=None, offset=None, limit=None, samplekey=None, trajectorykey=None,
                       min_samplekey=None, max_samplekey=None, samplekey_in=None):
        table_names = set([])
        for column in column_names:
            table_name, column_name = split_column(column)
            table_names.add(table_name)

        if orderby is None:
            orderby = ''
        else:
            table_name, column_name = split_column(orderby)
            table_names.add(table_name)
            orderby = 'ORDER BY %s' % orderby

        samplekeys = self.samplekeys.table_name
        tables = set([self.find_table(table_name) for table_name in table_names if table_name != samplekeys])

        # TODO: add a general constraint class
        if trajectorykey is not None:
            if self.trajectories not in tables:
                tables.add(self.trajectories)

        inner_join = ''
        for table in tables:
            inner_join += table.samplekey_inner_join_stmt



        args=()
        
        where_conditions = []
        if samplekey is not None:
            where_conditions.append(self.samplekeys.samplekey_column + '=? ')
            args = args + (samplekey,)

        if trajectorykey is not None:
            where_conditions.append(self.trajectories.trajectory_column + '=? ')
            args = args + (trajectorykey, )

        if min_samplekey is not None:
            where_conditions.append(self.samplekeys.samplekey_column + '>=? ')
            args = args + (min_samplekey,)
        if max_samplekey is not None:
            where_conditions.append(self.samplekeys.samplekey_column + '<=? ')
            args = args + (max_samplekey,)

        if samplekey_in is not None:
            where_conditions.append(self.samplekeys.samplekey_column + ' IN (%s)' % samplekey_in)

        if where_conditions != []:
            where = 'WHERE ' + ' AND '.join(where_conditions)
        else:
            where = ''

        if offset is not None:
            offset = ' OFFSET %d ' % offset
        else:
            offset = ''

        if limit is not None:
            limit = ' LIMIT %d ' % limit
        else:
            limit = ''





        def selector(column_names):
            samplekeys; inner_join; where; orderby; limit; offset

            columns = ', '.join(column_names)
        
            with self.cursor() as c:
                sql = "SELECT %(columns)s FROM %(samplekeys)s %(inner_join)s %(where)s %(orderby)s %(limit)s %(offset)s" % locals()
                try:
                    if os.getenv('DEBUGSQL'):
                        print 'select_samples ', sql, args
                    c.execute(sql, args)
                    for row in c:
                        yield row
                except:
                    if os.getenv('DEBUGSQL'):
                        print 'select samples exception sql = ', sql, args
                    raise

        if len(column_names) < max_sql_variables:
            for row in selector(column_names):
                yield row
        else:
            column_selectors = []

            num_variables = len(column_names)

            for column_cut in xrange(0,num_variables, max_sql_variables):

                cut_column_names = column_names[column_cut:min(num_variables, column_cut+max_sql_variables)]

                column_selectors.append(selector(cut_column_names))

            def flatten(r):
                if len(r) > 1:
                    return r[0] + flatten(r[1:])
                else:
                    return r[0]

            for rows in it.izip(*column_selectors):
                row = flatten(rows)
                yield row


    def num_coordinate_samples(self):
        with self.cursor() as c:
            return self.coordinates.num_samples(c)

    # def create_energy_table(self):
    #     with self.cursor() as c:
    #         self.tables['Energies'].create_sql_table(c)

    def insert_new_trajectory_cursor(self, c, **kwargs):
        return self.trajectorykeys.insert_new_trajectory_cursor(c, **kwargs)

    @property
    def num_trajectories(self):
        with self.cursor() as c:
            return self.trajectorykeys.num_trajectories(c)

    @property
    def max_trajectorykey(self):
        with self.cursor() as c:
            return self.trajectorykeys.max_trajectorykey(c)

    @property
    def last_samplekey(self):
        with self.cursor() as c:
            return self.samplekeys.max_samplekey(c)


    def get_trajectorykeys(self):
        with self.cursor() as c:
            return self.trajectorykeys.trajectorykeys(c)

    def trajectorykey_in_database(self, trajectorykey):
        with self.cursor() as c:
            return self.trajectorykeys.trajectorykey_in_table(c, trajectorykey)
        

    # @property
    # def time_keys(self):
    #     with self.cursor() as c:
            

    @property
    def last_trajectorykey(self):
        with self.cursor() as c:
            return self.trajectorykeys.max_trajectorykey(c)

    # def insert_trajectory_step_cursor(self, c, trajectorykey, timekey, **kwargs):
    #     samplekey = self.samplekeys.new_sample_key(c, trajectorykey, timekey)
    #     # TODO: insert into sample property tables
    #     for table in self.tables.values():
    #         table.insert(c, samplekey, **kwargs)
    #     return samplekey

    # def insert_trajectory_step(self, trajectorykey, timekey, coords=None, **kwargs):
    #     if coords is None:
    #         raise TrajectoryDatabaseError("coords kwarg not provided.")
    #     with self.cursor() as c:
    #         samplekey = self.insert_trajectory_step_cursor(c, trajectorykey, timekey, coords=coords, **kwargs)
    #     return samplekey


    # def insert_trajectory_step_many(self, iterator):
    #     with self.cursor() as c:
    #         for step in iterator:
    #             trajectorykey, timekey, kwargs = step
    #             self.insert_trajectory_step_cursor(c, trajectorykey, timekey, **kwargs)


    def new_sample_keys(self, iterator):
        with self.cursor() as c:
            self.samplekeys.new_sample_keys(c, iterator)

    # def _samplekey_constraints(self, timekey=None, trajectorykey=None):
    #     where_expr=''
    #     cursor_args=()

    #     timekey_column = self.samplekeys.qualified_timekey_column
    #     trajectorykey_column = self.samplekeys.qualified_trajectorykey_column
    #     samplekeys = self.samplekeys.table_name

    #     if timekey is not None:
    #         where_expr += ' %(timekey_column)s=? ' % locals()
    #         cursor_args+=(timekey,)

    #     if trajectorykey is not None:
    #         if where_expr:
    #             where_expr += ' AND '
    #         where_expr += ' %(trajectorykey_column)s=? ' % locals()
    #         cursor_args+=(trajectorykey,)

    #     if where_expr:
    #         where_expr += ' ORDER BY %(timekey_column)s ' % locals()

    #     return where_expr, cursor_args
            
    def add_new_trajectory(self, **kwargs):
        with self.cursor() as c:
            trajkey = self.insert_new_trajectory_cursor(c, **kwargs)
        return trajkey

    def new_trajectory(self, coord_iterator, time_step, initial_time=0.):
        trajectorykey = self.add_new_trajectory()
        self.insert_trajectory(trajectorykey, coord_iterator, 
                               time_step, initial_time)
        return trajectorykey

    def last_trajectory_time(self, trajectorykey):
        row = (None,)
        for row in self.select_samples([self.times.time_column], trajectorykey=trajectorykey):
            pass
        last_time = row[0]
        return last_time

    def extend_trajectory(self, trajectorykey, coord_iterator, time_step, initial_time=None):

        last_time = self.last_trajectory_time(trajectorykey)

        if initial_time is None:
            if last_time is None:
                initial_time = 0.
            else:
                initial_time = time_step + last_time
        else:
            last_time = self.last_trajectory_time(trajectorykey)
            if last_time is not None:
                if initial_time <= last_time:
                    raise TrajectoryDatabaseError("Tried to extend trajectory from a time earlier than the last time: %s <= %s" % (initial_time, last_time))

        self.insert_trajectory(trajectorykey, coord_iterator, time_step, initial_time)

    def new_samplekeys_iterator(self, trajectorykey, times=None):

        if times is not None:
            timekey_iterator = self.timekey_iterator(times)
        else:
            timekey_iterator = self.timekeys_iterator()

        for samplekey in self.new_sample_keys(it.izip(it.repeat(trajectorykey), timekey_iterator)):
            yield samplekey


            
    def new_samplekeys_iterator(self):
        with self.cursor() as c:
            while True:
                yield self.samplekeys.new_sample_key(c)



    def timed_samplekeys(self, trajectorykey, time_step, initial_time):
        time = initial_time
        with self.cursor() as time_c:
            with self.cursor() as trajectory_c:
                for samplekey, in it.izip(self.new_samplekeys_iterator()):
                    self.times.insert_many(time_c, [(samplekey, time)])
                    self.trajectories.insert_many(trajectory_c, [(samplekey, trajectorykey)])
                    time += time_step
                    yield samplekey
            

        

    def insert_trajectory(self, trajectorykey, coord_iterator, time_step, initial_time):
        
        def insert_iterator():
            time = initial_time
            for coords, samplekey in it.izip(coord_iterator, self.timed_samplekeys(trajectorykey, time_step, initial_time)):
                yield (samplekey,) + tuple(coords)
        with self.cursor() as c:
            self.coordinates.insert_many(c, insert_iterator())
        return trajectorykey


    def insert_susy_coordinate(self, trajectorykey, coord,  time_step, initial_time):

        with self.cursor() as c:

            samplekey = self.timed_samplekeys(trajectorykey, time_step, initial_time).next()

            q = coord

            self.coordinates.insert_many(c, [(samplekey,) + tuple(q)])

        return trajectorykey


    def insert_coordinate_and_momentum(self, trajectorykey, coord, time_step, initial_time):

        with self.cursor() as c:

            samplekey = self.timed_samplekeys(trajectorykey, time_step, initial_time).next()

            (q, p) = coord

            self.coordinates.insert_many(c, [(samplekey,) + tuple(q)])
            self.momenta.insert_many(c, [(samplekey,) + tuple(p)])

        return trajectorykey


    def new_coordinate(self, coord, time_step, initial_time = 0.):

        trajectorykey = self.add_new_trajectory()
        self.insert_coordinate(trajectorykey, coord, time_step, initial_time)

        return trajectorykey


    def new_coordinate_and_momentum(self, coord, time_step, initial_time = 0.):

        trajectorykey = self.add_new_trajectory()
        self.insert_coordinate_and_momentum(trajectorykey, coord, time_step, initial_time)

        return trajectorykey



    def add_sample_property_from_geometry(self, table_name, property_func, column_name=None):
        table = self.add_class_table(table_name, class_column=column_name, create=True)
        
        def property_iterator():
            for row in self.select_samples([self.samplekeys.samplekey_column] + self.coordinates.crd_columns):
                yield row[0], property_func(row[1:])

        self.insert_classes_many(table, property_iterator())


    def merge(self, merge_db):
        # Merge the samplekeys
        samplekey_offset = self.last_samplekey

        def samplekeys():
            for row in merge_db.select_samples([merge_db.samplekeys.samplekey_column]):
                yield (row[0] + samplekey_offset, )

        with self.cursor() as c:
            self.samplekeys.new_sample_keys(c, samplekeys())


        # Merge the trajectory keys
        trajectorykey_offset = self.last_trajectorykey
        

        def trajectorykeys():
            for row in merge_db.select_trajectories([merge_db.trajectorykeys.trajectorykey_column]):
                yield (row[0] + trajectorykey_offset, )

        def trajectories():
            for row in merge_db.select_samples([merge_db.samplekeys.samplekey_column,
                                                     merge_db.trajectories.trajectory_column]):
                yield (row[0] + samplekey_offset, row[1] + trajectorykey_offset, )

        with self.cursor() as c:
            self.trajectorykeys.insert_new_trajectories_cursor(c, trajectorykeys())
            self.trajectories.insert_many(c, trajectories())

        
        # Merge the coordinates

        def coordinates():
            for row in merge_db.select_samples([merge_db.samplekeys.samplekey_column] + merge_db.coordinates.crd_columns):
                yield (row[0] + samplekey_offset,) + row[1:]

        with self.cursor() as c:
            self.coordinates.insert_many(c, coordinates())


        # Merge the class tables

        for table in merge_db.sample_property_tables:
            if table.table_name == merge_db.trajectories.table_name:
                continue
            print 'Merging ', table.table_name
            class_table = self.add_class_table(table.table_name, class_column=table._class_column, create=True)
            
            def classes():
                for row in merge_db.select_samples([merge_db.samplekeys.samplekey_column,
                                                         table.class_column]):
                    yield (row[0] + samplekey_offset, row[1])

            self.insert_classes_many(class_table, classes())


            

open_trajectory_database=TrajectoryDatabase

class Reader(object):
    
    def __init__(self, filename, samplekey=None, trajectorykey=None, samplekey_in=None):
        self.samplekey=samplekey
        self.trajectorykey=trajectorykey
        self.samplekey_in=samplekey_in
        self.db = open_trajectory_database(filename, create=False)

    def read(self):
        num_atoms = self.db.ndof/3
        for row in self.db.select_samples(self.db.coordinates.crd_columns, # self.db.coordinates.crd_columns est une liste rapportant la position de chaque coordonnee dans la
								           # database. Chaque element de la liste est une string du type 'Coordinatesx.Coordy' 
									   # ou x est le numero de la table dans laquelle figure la coordonnee (500 coord par table) et
								           # y le numero de la coordonnee
                                          samplekey=self.samplekey, 
                                          trajectorykey=self.trajectorykey,
                                          samplekey_in=self.samplekey_in):
            q = np.array(row)
            yield molecule.Molecule('', ['?'] * num_atoms, q)



