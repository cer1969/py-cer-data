# -*- coding: utf-8 -*-

import os, weakref, sqlite3

#-----------------------------------------------------------------------------------------

__all__ = ['connect', 'copyDataBase', 'compactFile']

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

class View(object):
    
    def __init__(self, dbref, name):
        self._db = dbref
        self.name = name
        self.colnames = self._get_colnames()
        self.key = "idx"
        self.orderby = ""
    
    def _get_colnames(self):
        # La llamada a PRAGMA provoca commit
        Q = self._db.fetch("PRAGMA table_info(%s)" % self.name)
        return [x.name for x in Q]
    
    def fetch(self, where="", params=None, cols="*", orderby=None):
        orderby = self.orderby if orderby is None else orderby
        
        whe = ("where %s" % where) if (where != "") else ""
        oby = ("order by %s" % orderby) if (orderby != "") else ""
        query = "select %s from %s %s %s" % (cols, self.name, whe, oby)
        prms = [] if params is None else params
        
        return self._db.fetch(query, prms)
    
    def __getitem__(self, idx):
        data = self.fetch("%s=?" % self.key, [idx])
        val = data[0] if data else None
        return val


#-----------------------------------------------------------------------------------------

class Table(View):
    
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
        idx = r[self.key]
        del r[self.key]
        ftxt = ",".join(["%s=?" % x for x in r.keys()])
        query = "update %s set %s where %s=?" % (self.name, ftxt, self.key)
        vals = r.values() + [idx]
        self._db.alter(query, vals)
    
    def delete(self, rec):
        self.deleteById(rec[self.key])
    
    def deleteById(self, idx):
        query = "delete from %s where %s=?" % (self.name, self.key)
        self._db.alter(query, [idx])


#-----------------------------------------------------------------------------------------

class QueryDict(dict):
    """ Los nombres de tablas/vistas __*__ no están permitidos:
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
        master = self.fetch("select * from sqlite_master")
        
        self.tablesinfo = [t for t in master if (t.type=="table" and not t.name.startswith("sqlite_"))]
        self.tables = QueryDict()
        for t in self.tablesinfo:
            self.tables[t.name] = Table(weakref.proxy(self), t.name)
        
        self.indexesinfo = [t for t in master if (t.type=="index" and not t.name.startswith("sqlite_"))]
        
        self.viewsinfo = [t for t in master if t.type=="view"]
        self.views = QueryDict()
        for t in self.viewsinfo:
            self.views[t.name] = View(weakref.proxy(self), t.name)
    
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
        try:
            return self.tables[name]
        except KeyError:
            try:
                return self.views[name]
            except KeyError:
                raise Exception("No table/view with name '%s'" % name)


#-----------------------------------------------------------------------------------------

def connect(filename):
    return sqlite3.connect(filename,
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, 
        factory=Connection
    )


def copyDataBase(db1, db2):
    row_factory = db1.row_factory
    db1.row_factory = None
    
    cur1 = db1.cursor()
    cur2 = db2.cursor()
    
    # Copia tablas
    for t in db1.tablesinfo:
        cur2.execute(t.sql)
        
        cur1.execute("select * from %s" % t.name)
        data = cur1.fetchall()
        
        query = "insert into %s values (%s)" % (t.name, ",".join(["?"]*len(data[0])))
        cur2.executemany(query, data)
    
    # Copia indices
    for i in db1.indexesinfo:
        cur2.execute(i.sql)
    
    # Copia vistas
    views = db1.viewsinfo[:]
    while len(views)>0:
        v = views.pop(0)
        try:
            cur2.execute(v.sql)
        except sqlite3.OperationalError:
            views.append(v)
    
    db1.row_factory = row_factory
    db2.commit()


def compactFile(filename):
    """ Compacta filename copiando sus datos a memoria y restituyendolo
        en el mismo archivo. Requiere que filename no este abierto.
    """
    db = connect(filename)
    dbm = connect(":memory:")
    
    # Copiamos de db filename a memoria
    copyDataBase(db, dbm)
    
    # Borra db filename
    db.close()
    os.remove(filename)
    
    # Restaura datos de dbm a db filename
    db = connect(filename)
    dbm.refresh()
    copyDataBase(dbm, db)
    db.close()
    dbm.close()