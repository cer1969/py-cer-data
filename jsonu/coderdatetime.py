# -*- coding: utf-8 -*-

from coder import Coder
from datetime import datetime, date, time

#-----------------------------------------------------------------------------------------

__all__ = ['DateTimeCoder', 'DateCoder', 'TimeCoder', 'datetime_coders']

#-----------------------------------------------------------------------------------------

class DateTimeCoder(Coder):
    
    __slots__ = ()
    
    def __init__(self):
        Coder.__init__(self, datetime, "datetime")
    
    def getarg(self, obj):
        return [obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second, obj.microsecond]

#-----------------------------------------------------------------------------------------

class DateCoder(Coder):
    
    __slots__ = ()
    
    def __init__(self):
        Coder.__init__(self, date, "date")
    
    def getarg(self, obj):
        return [obj.year, obj.month, obj.day]

#-----------------------------------------------------------------------------------------

class TimeCoder(Coder):
    
    __slots__ = ()
    
    def __init__(self):
        Coder.__init__(self, time, "time")
    
    def getarg(self, obj):
        return [obj.hour, obj.minute, obj.second, obj.microsecond]

#-----------------------------------------------------------------------------------------

datetime_coders = [DateTimeCoder(), DateCoder(), TimeCoder()]