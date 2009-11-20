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

class Connection(sqlite3.Connection):
    
    def alter(self, query, params=[]):
        cur = self.cursor()
        cur.execute(query, params)
        idx = cur.lastrowid
        cur.close()
        return idx
    
    def fetch(self, query, params=[], maxsplit=None):
        # maxsplit: permite eliminar partes del inicio de los nombres
        # en los registros de salida
        cur = self.cursor()
        cur.execute(query, params)
        Q = _get_records(cur, maxsplit)
        cur.close()
        return Q
    
    def __getattr__(self, name):
        if self._reg_actions.has_key(name):
            return self._reg_actions[name]
        raise AttributeError("%s not implemented for %s" % (name, self.__class__))
    
    def regActions(self, *data):
        # Registra metodos para obtener datos de tablas
        # Este método debería ser llamado solo una vez
        self._reg_actions = {}
        
        for i in data:
            self._regTableActions(i)
    
    def _regTableActions(self, table):
        name = table.split("_")[-1] # necesario para eliminar el v_ en views
        capName = name.capitalize()
        
        # fetchTable
        def _fetchTable(where="", params=[], orderby=""):
            whe = ("where %s" % where) if (where != "") else ""
            oby = ("order by %s" % orderby) if (orderby != "") else ""
            query = "select * from %s %s %s" % (table, whe, oby)
            return self.fetch(query, params, maxsplit=1)
        self._reg_actions["fetch%s" % capName] = _fetchTable
        
        # fetchTableById
        def _fetchTableById(idx):
            data = _fetchTable("%s_idx=?" % name, [idx])
            val = data[0] if data else None
            return val
        self._reg_actions["fetch%sById" % capName] = _fetchTableById
        
        # updateTable
        def _updateTable(idx, **kwa):
            items = kwa.items()
            ftxt = ",".join(["%s_%s=?" % (name,x[0]) for x in items])
            values = [x[1] for x in items]
            values.append(idx)
            query = "update %s set %s where %s_idx=?" % (name, ftxt, name)
            self.alter(query, values)
        self._reg_actions["update%s" % capName] = _updateTable
        
        # insertTable
        def _insertTable(**kwa):
            items = kwa.items()
            ftxt = ",".join(["%s_%s" % (name,x[0]) for x in items])
            values = [x[1] for x in items]
            vtxt = ",".join(["?"]*len(values))
            query = "insert into %s (%s) values (%s)" % (name, ftxt, vtxt)
            return self.alter(query, values)
        self._reg_actions["insert%s" % capName] = _insertTable

#-----------------------------------------------------------------------------------------

def connect(filename):
    db = sqlite3.connect(filename, 
        detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES,
        factory=Connection
    )
    return db