# CRISTIAN ECHEVERRÍA RABÍ

import openpyxl as ox
from munch import Munch

#---------------------------------------------------------------------------------------------------

class AttrDict(dict):
    __slots__ = ()
    #__getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

    def __getattr__(self, name):
        it = self[name]
        if type(it) is dict:
            return AttrDict(it)
        return it


#---------------------------------------------------------------------------------------------------

class Book(object):
    def __init__(self, filepath, read_only=True, data_only=True):
        self._wb = ox.load_workbook(filepath, read_only=read_only, data_only=data_only)
    
    def getData(self, shname, rows, cols, dict_class=AttrDict):
        sh = self._wb[shname]
        headers = [sh.cell(row=rows[0], column=x).value for x in range(*cols)]
        data = []
        for i in range(rows[0] + 1, rows[1]):
            row = [sh.cell(row=i, column=x).value for x in range(*cols)]
            data.append(dict_class(zip(headers, row)))
        return data
    
    def getRowIterator(self, sheet, rows=(1, None), cols=(1, None)):
        sh = self._wb[sheet]
        return sh.iter_rows(min_row=rows[0], max_row=rows[1], min_col=cols[0], max_col=cols[1])
    
    def getMuchData(self, sheet, rows=(1, None), cols=(1, None)):
        it = self.getRowIterator(sheet, rows, cols)
        headers = [c.value for c in next(it)]
        data = []
        for r in it:
            data.append(Munch(zip(headers, [c.value for c in r])))
        return data