# -*- coding: utf-8 -*-

import sqlite3
import datetime # requerido por sqlite3

#-----------------------------------------------------------------------------------------

__all__ = ['connect']

#-----------------------------------------------------------------------------------------
# Record factory for sqlite3

class _Record(dict):
    def __init__(self, names, values):
        dict.__init__(self, zip(names, values))
    def __getattr__(self, name):
        return self[name]

def _get_records(cursor, maxsplit=None):
    # maxsplit: permite eliminar partes del inicio de los nombres
    names = [x[0] for x in cursor.description]
    if maxsplit:
        names = [x.split("_", maxsplit)[-1] for x in names]
    data = cursor.fetchall()
    return [_Record(names, row) for row in data]

#-----------------------------------------------------------------------------------------

class Table(object):
    
    def __init__(self, db, viewName):
        self.db = db
        self.viewName = viewName
        self.tableName = viewName.split("_")[-1] # necesario para eliminar el v_ en views
    
    def fetch(self, where="", params=[], orderby=""):
        whe = ("where %s" % where) if (where != "") else ""
        oby = ("order by %s" % orderby) if (orderby != "") else ""
        query = "select * from %s %s %s" % (self.viewName, whe, oby)
        return self.db.fetch(query, params, maxsplit=1)
    
    def get(self, idx):
        data = self.fetch("%s_idx=?" % self.tableName, [idx])
        val = data[0] if data else None
        return val
    
    def update(self, idx, **kwa):
        items = kwa.items()
        ftxt = ",".join(["%s_%s=?" % (self.tableName, x[0]) for x in items])
        values = [x[1] for x in items]
        values.append(idx)
        query = "update %s set %s where %s_idx=?" % (self.tableName, ftxt, self.tableName)
        self.db.alter(query, values)
    
    def insert(self, **kwa):
        items = kwa.items()
        ftxt = ",".join(["%s_%s" % (self.tableName, x[0]) for x in items])
        values = [x[1] for x in items]
        vtxt = ",".join(["?"]*len(values))
        query = "insert into %s (%s) values (%s)" % (self.tableName, ftxt, vtxt)
        return self.db.alter(query, values)
    
    def delete(self, idx):
        query = "delete from %s where %s_idx=?" % (self.tableName, self.tableName)
        self.db.alter(query, [idx])

#-----------------------------------------------------------------------------------------

class Connection(sqlite3.Connection):
    
    def registerTables(self, *data):
        for viewName in data:
            t = Table(self, viewName)
            setattr(self, t.tableName, t)
    
    def alter(self, query, params=[]):
        cur = self.cursor()
        cur.execute(query, params)
        idx = cur.lastrowid
        cur.close()
        return idx
    
    def compact(self):
        self.alter("VACUUM")
    
    def fetch(self, query, params=[], maxsplit=None):
        # maxsplit: permite eliminar partes del inicio de los nombres
        # en los registros de salida
        cur = self.cursor()
        cur.execute(query, params)
        Q = _get_records(cur, maxsplit)
        cur.close()
        return Q

#-----------------------------------------------------------------------------------------

def connect(filename):
    db = sqlite3.connect(filename, 
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
        factory=Connection
    )
    return db