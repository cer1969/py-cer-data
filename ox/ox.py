# CRISTIAN ECHEVERRÍA RABÍ

import openpyxl as ox

#---------------------------------------------------------------------------------------------------

class AttrDict(dict):
    __slots__   = ()
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

    def get_sheet(self, name):
        return Sheet(self, name)


#---------------------------------------------------------------------------------------------------

class Sheet(object):

    def __init__(self, book, name):
        self._sh = book._wb[name]

    def iter_data(self, rows=(1, None), cols=(1, None)):
        return self._sh.iter_rows(min_row=rows[0], max_row=rows[1], min_col=cols[0], max_col=cols[1])

    def get_data(self, rows, cols, dict_class=dict):
        it = self.iter_data(rows, cols)
        headers = [c.value.lower() for c in next(it)]
        data = []
        for r in it:
            data.append(dict_class(zip(headers, [c.value for c in r])))
        return data