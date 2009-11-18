# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ
# Archivo      : setup
# Fecha        : 15-09-2006 11:43:58 

import glob, sys, os
from distutils.core import setup
import py2exe

#-----------------------------------------------------------------------------------------

# Cuando se corre sin argumentos, incorporamos los que faltan
if len(sys.argv) == 1:
    sys.argv.append("py2exe")
    sys.argv.append("-b 2")

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # Valores predeterminados para la información de versión del ejecutable
        self.company_name = u"Cristian Echeverría Rabí"
        self.copyright = u"(R)Cristian Echeverría Rabí"

#-----------------------------------------------------------------------------------------
# Definición del ejecutable

app = Target(
    # used for the versioninfo resource
    version = "0.0.1.0",
    description = "WebCompras",
    name = "WebCompras",
    # what to build
    script = "test1.py",
    #icon_resources = [(1, "./globe.ico")],
    # nombre del ejecutable
    dest_base = "WebCompras"
)

#-----------------------------------------------------------------------------------------

options = dict (
    py2exe = dict (
        compressed = 1,
        optimize = 2,
        #packages = ["email","HTMLParser"],
        #packages = ["email"],
        #excludes = ["Tkconstants","Tkinter","tcl"],
    )
)

# Archivos adicionales
"""
sal = [("data" ,     glob.glob("./data/*.*")),
       ("." ,        ['WebCompras.conf','startPage.html'])
]

for r,d,f in os.walk("./public"):
    flist = []
    for i in f:
        fn = os.path.join(r,i)
        flist.append(fn)
    sal.append((r,flist))
"""

#-----------------------------------------------------------------------------------------

setup(
    console = [app],
    #data_files = sal,
    options = options,
    zipfile = "data.zip"
)
