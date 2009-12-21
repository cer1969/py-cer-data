# -*- coding: utf-8 -*-
# CRISTIAN ECHEVERRÍA RABÍ
# Archivo      : doc/excel/Functions
# Fecha        : 27-09-2007 15:15:00  
# Descripción  : Convierte datos entre Excel a python

import pywintypes
import datetime

#-----------------------------------------------------------------------------------------

__all__ = ['getExcelTime', 'getDate', 'getDateTime', 'getInt', 'getFloat', 'getText'] 

#-----------------------------------------------------------------------------------------
# Python a Excel

def getExcelTime(t):
    """Retorna Excel Time
    t: time tuple
    """
    mk = t.timetuple()
    return pywintypes.Time(mk)

#-----------------------------------------------------------------------------------------
# Excel a python

def getDate(t):
    """Retorna python datetime.date
    t: Excel Time"""
    try:
        nt = datetime.date(t.year,t.month,t.day)
    except AttributeError:
        nt = ""
    return nt

def getDateTime(t):
    """Retorna python datetime.datetime
    t: Excel Time"""
    try:
        nt = datetime.datetime(t.year,t.month,t.day,t.hour,t.minute)
    except AttributeError:
        nt = ""
    return nt

def getInt(txt):
    """Retorna python int
    txt: string o objeto compatible con int
    """
    try:
        value = int(txt)
    except (TypeError,ValueError):
        value = 0
    return value

def getFloat(txt):
    """Retorna python float
    txt: string o objeto compatible con float
    """
    try:
        value = float(txt)
    except (TypeError,ValueError):
        value = 0.0
    return value

def getText(txt):
    """Retorna python string o unicode
    txt: string o objeto compatible con string
    """
    if txt is None:
        return ""
    #if type(txt) in (int,float):
    #    if txt == 0:
    #        return ""
    #    else:
    #        return unicode(int(txt))
    return unicode(txt).strip()