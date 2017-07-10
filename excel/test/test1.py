# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ
# Fecha        : 24-09-2007 12:11:43   

from __future__ import with_statement
from cer.data import excel

#-----------------------------------------------------------------------------------------

filename = r"C:\Documents and Settings\cecheverria\Mis documentos\Demanda ATR-3 DDA Agosto 07.xls"

#-----------------------------------------------------------------------------------------

# Esta es la forma recomendada.
# El objeto excel.Application se crea implicitamente y se cierra en forma adecuada
# aún cuando falle la creación del Book.
# Si se requiere usar el objeto Application: Book y Sheet tienen referencias
"""
with excel.bookContext(filename, True) as bk:
    sh = bk.GetSheet(1)
    print sh.NRows, sh.NCols
    r = sh.GetRow(12)
    print r
"""


tpl = r"C:\Documents and Settings\cecheverria\Mis documentos\030_Devel\Tao\trunk\cerapp\macro\Transfe.xlt"

app = excel.Application()
#bk = app.Workbooks.Add(Template=tpl)
bk = app.addBook(Template=tpl)
sh = bk.getSheet("Hoja1")
print (sh.Name)
app.Visible = True
app.quit()

# Este código requiere que se llame explicitamente bk.Close y app.Quit
"""
app = excel.Application()

bk = app.GetBook(filename, True)
sh = bk.GetSheet(1)

print sh.NRows, sh.NCols

r = sh.GetRow(12)
print r

print bk.Close()
print app.Quit()
"""