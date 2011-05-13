# -*- coding: utf-8 -*-

import os, sqlite3, datetime # requerido por sqlite3

#-----------------------------------------------------------------------------------------

__all__ = ['connect', 'copyDataBase', 'compactFile']

#-----------------------------------------------------------------------------------------
# Record factory for sqlite3

class _Record(dict):
    def __init__(self, names, values):
        dict.__init__(self, zip(names, values))
    def __getattr__(self, name):
        return self[name]

def _getRecords(cursor, maxsplit=None):
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
    
    def fetch(self, where="", params=None, orderby=""):
        whe = ("where %s" % where) if (where != "") else ""
        oby = ("order by %s" % orderby) if (orderby != "") else ""
        query = "select * from %s %s %s" % (self.viewName, whe, oby)
        prms = [] if params is None else params
        return self.db.fetch(query, prms, maxsplit=1)
    
    def get(self, _idx):
        data = self.fetch("%s_idx=?" % self.tableName, [_idx])
        val = data[0] if data else None
        return val
    
    def update(self, _idx, **kwa):
        items = kwa.items()
        ftxt = ",".join(["%s_%s=?" % (self.tableName, x[0]) for x in items])
        values = [x[1] for x in items]
        values.append(_idx)
        query = "update %s set %s where %s_idx=?" % (self.tableName, ftxt, self.tableName)
        self.db.alter(query, values)
    
    def insert(self, **kwa):
        items = kwa.items()
        ftxt = ",".join(["%s_%s" % (self.tableName, x[0]) for x in items])
        values = [x[1] for x in items]
        vtxt = ",".join(["?"]*len(values))
        query = "insert into %s (%s) values (%s)" % (self.tableName, ftxt, vtxt)
        return self.db.alter(query, values)
    
    def delete(self, _idx):
        query = "delete from %s where %s_idx=?" % (self.tableName, self.tableName)
        self.db.alter(query, [_idx])

#-----------------------------------------------------------------------------------------

class Connection(sqlite3.Connection):
    # TODO: Incorporar métodos para verificar que es una data nueva, verificar tablas y crear nuevas
    
    def getViewsInfo(self):
        return self.fetch("select * from sqlite_master where type=?", ["view"])
    
    def getTablesInfo(self):
        tq = self.fetch("select * from sqlite_master where type=?", ["table"])
        return [x for x in tq if not(x.name.startswith("sqlite_"))]
    
    def loadTables(self):
        # Identifica tablas y vistas en la base de datos y llama a registerTables
        views = [x.name for x in self.getViewsInfo()]
        tables = [x.name for x in self.getTablesInfo()]
        
        tables_with_views = [x.split("_")[-1] for x in views]
        for i in tables:
            if not (i in tables_with_views):
                views.append(i)
        
        self.registerTables(*views)
    
    def registerTables(self, *data):
        for viewName in data:
            t = Table(self, viewName)
            setattr(self, t.tableName, t)
    
    def alter(self, query, params=None):
        cur = self.cursor()
        prms = [] if params is None else params
        cur.execute(query, prms)
        idx = cur.lastrowid
        cur.close()
        return idx
    
    #def compact(self):
    #    self.alter("VACUUM")
    
    def fetch(self, query, params=None, maxsplit=None):
        # maxsplit: permite eliminar partes del inicio de los nombres
        # en los registros de salida
        cur = self.cursor()
        prms = [] if params is None else params
        cur.execute(query, prms)
        Q = _getRecords(cur, maxsplit)
        cur.close()
        return Q

#-----------------------------------------------------------------------------------------

def connect(filename):
    db = sqlite3.connect(filename, 
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, 
        factory=Connection
    )
    return db


def copyDataBase(db1, db2):
    """ Copia contenidos de db1 a db2
    """
    cur1 = db1.cursor()
    cur2 = db2.cursor()
    
    # Crea tablas de db1 en db2
    for t in db1.getTablesInfo():
        cur2.execute(t.sql)
        
        cur1.execute("select * from %s" % t.name)
        data = cur1.fetchall()
        
        query = "insert into %s values (%s)" % (t.name, ",".join(["?"]*len(data[0])))
        cur2.executemany(query, data)
    
    for v in db1.getViewsInfo():
        db2.execute(v.sql)
    
    db2.commit()


def compactFile(filename):
    """ Compacta filename copiando su contenido a memoria y restituyendolo
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
    copyDataBase(dbm, db)
    db.close()