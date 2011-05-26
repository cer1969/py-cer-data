# -*- coding: utf-8 -*-

#-----------------------------------------------------------------------------------------

__all__ = ["Translator", "AttrDict"]

#-----------------------------------------------------------------------------------------

class AttrDict(dict):
    __slots__ = ()
    def __getattr__(self, idx):
        return self[idx]
    def __setattr__(self, idx, value):
        self[idx] = value

#-----------------------------------------------------------------------------------------

class Translator(object):
    
    __slots__ = ("coders")
    
    def __init__(self, coders):
        self.coders = coders
    
    def toJson(self, obj):
        for t in self.coders:
            if isinstance(obj, t.cls):
                return t.encode(obj)
        raise TypeError(repr(obj) + ' is not JSON serializable')
    
    def fromJson(self, obj):
        if '__class__' in obj:
            for t in self.coders:
                if obj['__class__'] == t.name:
                    return t.decode(obj)
        return AttrDict(obj)