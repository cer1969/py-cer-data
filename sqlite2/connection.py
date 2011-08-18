# -*- coding: utf-8 -*-

import os, weakref, sqlite3

#-----------------------------------------------------------------------------------------

__all__ = ['connect', 'copyTables', 'compactFile']

#-----------------------------------------------------------------------------------------

class _Record(dict):
    """ Los nombres de columnas __*__ no están permitidos:
    """
    __slots__ = ()
    
    def __getattr__(self, name):
        return self[name]
    
    def __setattr__(self, name, value):
        self[name] = value


def _get_clean_dict(rec):
    d = {}
    for (key,value) in rec.items():
        if not(value is None) and not isinstance(value, _Record):
            d[key] = value
    return d
    

def _record_factory(cursor, row):
    names = [x[0] for x in cursor.description]
    return _Record(zip(names, row))

#-----------------------------------------------------------------------------------------

class Table(object):
    # TODO: Analizar conveniencia de incorporar insertMany
    
    def __init__(self, dbref, name):
        self._db = dbref
        self.name = name
        self.colnames = self._get_colnames()
        self.linknames = [x.split("_")[0] for x in self.colnames if ("_idx" in x)]
        self.orderby = ""
    
    def _get_colnames(self):
        # La llamada a PRAGMA provoca commit
        Q = self._db.fetch("PRAGMA table_info(%s)" % self.name)
        return [x.name for x in Q]
    
    def getNew(self, **kwa):
        return _Record(kwa)
    
    def insert(self, rec):
        r = _get_clean_dict(rec)
        return self.insertNew(**r)
    
    def insertNew(self, **kwa):
        ctxt = ",".join(kwa.keys())
        vals = kwa.values()
        vtxt = ",".join(["?"]*len(vals))
        query = "insert into %s (%s) values (%s)" % (self.name, ctxt, vtxt)
        return self._db.alter(query, vals)
       
    def update(self, rec):
        r = _get_clean_dict(rec)
        idx = r["idx"]
        del r["idx"]
        ftxt = ",".join(["%s=?" % x for x in r.keys()])
        query = "update %s set %s where idx=?" % (self.name, ftxt)
        vals = r.values() + [idx]
        self._db.alter(query, vals)
    
    def delete(self, rec):
        self.deleteById(rec.idx)
    
    def deleteById(self, idx):
        query = "delete from %s where idx=?" % self.name
        self._db.alter(query, [idx])
    
    def fetch(self, where="", params=None, orderby=None):
        orderby = self.orderby if orderby is None else orderby
        tn = self.name
        
        whe = ("where %s" % where) if (where != "") else ""
        oby = ("order by %s" % orderby) if (orderby != "") else ""
        query = "select * from %s %s %s" % (tn, whe, oby)
        prms = [] if params is None else params
        
        Q = self._db.fetch(query, prms)
        
        for tn2 in self.linknames:
            fn = "%s_idx" % tn2
            
            # Se recuperan idx de la tabla linkeada en la tabla principal
            query = "select distinct %s from %s" % (fn, tn)
            idxs = self._db.fetch(query)
            
            # Se recuperan registros de la tabla linkeada
            where = "idx in (%s)" % ",".join(["'%s'" % x[fn] for x in idxs])
            lrecs = self._db.tables[tn2].fetch(where)   # Esto es recursivo
            odict = dict([(r.idx, r) for r in lrecs])   # El dict facilita la asignación
            
            # Se incorpora a registros de la tabla principal
            for r in Q:
                r[tn2] = None if r[fn] is None else odict[r[fn]]
        
        #print "Fetching %s (%d registros)" % (tn, len(Q))
        return Q
    
    def __getitem__(self, idx):
        data = self.fetch("idx=?", [idx])
        val = data[0] if data else None
        return val

#-----------------------------------------------------------------------------------------

class TablesDict(dict):
    """ Los nombres de tablas __*__ no están permitidos:
    """
    __slots__ = ()
    
    def __getattr__(self, name):
        return self[name]


#-----------------------------------------------------------------------------------------

class Connection(sqlite3.Connection):
    
    def __init__(self, *args, **kwa):
        sqlite3.Connection.__init__(self, *args, **kwa)
        self.row_factory = _record_factory
        self.refresh()
    
    def refresh(self):
        self.sqlitemaster = self._get_sqlite_master()
        self.tablenames = [t.name for t in self.sqlitemaster if t.type=="table"]
        
        self.tables = TablesDict()
        for name in self.tablenames:
            self.tables[name] = Table(weakref.proxy(self), name)
    
    def _get_sqlite_master(self):
        return self.fetch("select * from sqlite_master")
    
    def fetch(self, query, params=None):
        cur = self.cursor()
        prms = [] if params is None else params        
        cur.execute(query, prms)
        Q = cur.fetchall()
        cur.close()
        return Q
    
    def alter(self, query, params=None, many=False):
        cur = self.cursor()
        prms = [] if params is None else params
        if many:
            cur.executemany(query, prms)
        else:
            cur.execute(query, prms)
        idx = cur.lastrowid
        cur.close()
        return idx
    
    def __getitem__(self, name):
        return self.tables[name]


#-----------------------------------------------------------------------------------------

def connect(filename):
    return sqlite3.connect(filename,
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, 
        factory=Connection
    )


def copyTables(db1, db2):
    """ Copia tablas de db1 a db2
        No copia vistas
    """
    row_factory = db1.row_factory
    db1.row_factory = None
    
    cur1 = db1.cursor()
    cur2 = db2.cursor()
    
    # Crea tablas de db1 en db2
    cur1.execute("select name,sql from sqlite_master where type='table'")
    
    tables = [x for x in cur1.fetchall() if not(x[0].startswith("sqlite_"))]
    
    for (name,sql) in tables:
        cur2.execute(sql)
        
        cur1.execute("select * from %s" % name)
        data = cur1.fetchall()
        
        query = "insert into %s values (%s)" % (name, ",".join(["?"]*len(data[0])))
        cur2.executemany(query, data)
    
    db1.row_factory = row_factory
    db2.commit()


def compactFile(filename):
    """ Compacta filename copiando sus tablas a memoria y restituyendolo
        en el mismo archivo. Requiere que filename no este abierto.
    """
    db = connect(filename)
    dbm = connect(":memory:")
    
    # Copiamos de db filename a memoria
    copyTables(db, dbm)
    
    # Borra db filename
    db.close()
    os.remove(filename)
    
    # Restaura datos de dbm a db filename
    db = connect(filename)
    copyTables(dbm, db)
    db.close()