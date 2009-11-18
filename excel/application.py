# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ
#
# Los atributos en excel son con Mayúsculas.
# Los proxys usan atributos en minúsculas para diferenciarlos de los objetos originales
# 

from __future__ import with_statement
from contextlib import contextmanager

import os, datetime
import win32com.client.dynamic
import pythoncom
import decimal

pythoncom.__future_currency__ = True

#-----------------------------------------------------------------------------------------

__all__ = ['app_context', 'book_context', 'Application', 'Book', 'Sheet',
           'APP_QUITOK', 'APP_QUITFAIL_WASOPEN', 'APP_QUITFAIL_HASWBKS',
           'BOOK_CLOSEOK', 'BOOK_CLOSEFAIL_WASOPEN',
           'APP_WINDOWSTATE_MIN', 'APP_WINDOWSTATE_MAX', 'APP_WINDOWSTATE_NOR'] 

#-----------------------------------------------------------------------------------------

@contextmanager
def app_context():
    """Permite usar Application con with statement"""
    app = Application()
    try:
        yield app
    finally:
        app.quit()


@contextmanager
def book_context(filename, readOnly=True):
    """Permite usar Book con with statement"""
    app = Application()
    try:
        book = app.getBook(filename, readOnly)
        try:
            yield book
        finally:
            book.close()
    finally:
        app.quit()

#-----------------------------------------------------------------------------------------

APP_QUITOK = 0
APP_QUITFAIL_WASOPEN = 1
APP_QUITFAIL_HASWBKS = 2

APP_WINDOWSTATE_MIN = -4140 # Minimize
APP_WINDOWSTATE_MAX = -4137 # Maximize
APP_WINDOWSTATE_NOR = -4143 # Normal


class Application(object):
    """Proxy class para Excel Application"""
    
    __slots__ = ('_obj', '_was_visible')

    def __init__(self):
        self._obj = win32com.client.dynamic.Dispatch("Excel.Application")
        self._was_visible = self.Visible
    
    def quit(self):
        """Finaliza Excel Application en forma segura"""
        if self._was_visible:
            # Can't quit: Excel was opened at start
            flag = False, APP_QUITFAIL_WASOPEN
        elif self.Workbooks.Count > 0:
            # Can't quit: There are Workbooks opened
            flag =  False, APP_QUITFAIL_HASWBKS
        else:
            # Excel Quit
            self._obj.Quit()
            flag = True, APP_QUITOK 
        self._obj = None # del self.__app
        return flag
    
    def getBook(self, filename, readOnly=True):
        """Retorna objeto Book"""
        filename = os.path.abspath(filename)
        bname = os.path.basename(filename)
        if bname in [x.Name for x in self.Workbooks]:
            wb = self.Workbooks(bname)
            was_closed = False
        else:
            wb = self.Workbooks.Open(filename, ReadOnly=readOnly)
            was_closed = True
        return Book(wb, was_closed)
    
    def addBook(self, *args, **kwa):
        wb = self._obj.Workbooks.Add(*args, **kwa)
        return Book(wb, False)
        
    def __getattr__(self, name):
        return getattr(self._obj, name)
    
    def __setattr__(self, name, value):
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        else:
            self._obj.__setattr__(name, value)


#-----------------------------------------------------------------------------------------

BOOK_CLOSEOK = 0
BOOK_CLOSEFAIL_WASOPEN = 1

class Book(object):
    """Proxy class para Excel Workbook"""
    
    __slots__ = ('_obj', '_was_closed')
    
    def __init__(self, wb, wasClosed):
        self._obj = wb
        self._was_closed = wasClosed
        #self.Application.WindowState = -4140 # Minimize
        self.Application.Visible = True

    def close(self, saveChanges=False):
        """Cierra Excel Workbook en forma segura"""
        if self._was_closed:
            # Book Close
            self._obj.Close(SaveChanges=saveChanges)
            flag = True, BOOK_CLOSEOK
        else:
            # Can't close: Book was opened at start
            flag = False, BOOK_CLOSEFAIL_WASOPEN
        self._obj = None # del self.__wb
        return flag
        
    def getSheet(self, idx):
        """Retorna objeto Sheet"""
        # idx: Puede ser un índice comenzando en 1 o el nombre de una hoja
        return Sheet(self.Worksheets(idx))
    
    def __getattr__(self, name):
        return getattr(self._obj, name)

    def __setattr__(self, name, value):
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        else:
            self._obj.__setattr__(name, value)

#-----------------------------------------------------------------------------------------

class Sheet(object):
    """Proxy class para Excel Worksheet"""
    
    __slots__ = ('_obj',)

    def __init__(self, ws):
        self._obj = ws

    def getNCols(self):
        return len(self.UsedRange.Columns)
    ncols = property(getNCols)
    
    def getNRows(self):
        return len(self.UsedRange.Rows)
    nrows = property(getNRows)

    def getRow(self, rn):
        row = [self.Cells(rn,i+1).Value for i in range(self.ncols)]
        return row
    
    def __getattr__(self, name):
        return getattr(self._obj,name)

    def __setattr__(self, name, value):
        if name in self.__slots__:
            object.__setattr__(self, name, value)
        else:
            self._ws.__setattr__(name, value)