# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------

__all__ = ["Coder"]

#-----------------------------------------------------------------------------------------

class Coder(object):
    
    __slots__ = ("cls", "name")
    
    def __init__(self, cls, name):
        self.cls = cls
        self.name = name
    
    def getarg(self, obj):
        return []
    
    def getkwa(self, obj):
        return {}    
    
    def encode(self, obj):
        arg = self.getarg(obj)
        kwa = self.getkwa(obj)
        return {"__class__": self.name, "__arg__": arg, "__kwa__": kwa}
    
    def decode(self, obj):
        arg = obj["__arg__"]
        kwa = obj["__kwa__"]
        return self.cls(*arg, **kwa)