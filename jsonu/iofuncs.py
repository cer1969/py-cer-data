# -*- coding: utf-8 -*-

import json, gzip
from coderdatetime import datetime_coders
from translator import Translator

#-----------------------------------------------------------------------------------------

__all__ = ['dumps', 'loads', 'save', 'read']

#-----------------------------------------------------------------------------------------

default_translator = Translator(datetime_coders)

#-----------------------------------------------------------------------------------------

def dumps(obj, indent=4, translator=default_translator):
    return json.dumps(obj, indent=indent, default=translator.toJson)

def loads(s, translator=default_translator):
    return json.loads(s, object_hook=translator.fromJson)

#-----------------------------------------------------------------------------------------

def save(filename, data, indent=4, compresslevel=9, translator=default_translator):
    if compresslevel == 0:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=indent, default=translator.toJson)
    else:
        with gzip.open(filename, 'w', compresslevel) as f:
            json.dump(data, f, indent=indent, default=translator.toJson)


def read(filename, translator=default_translator):
    try:
        with open(filename, 'r') as f:
            return json.load(f, object_hook=translator.fromJson)
    except ValueError:
        with gzip.open(filename, 'r') as f:
            return json.load(f, object_hook=translator.fromJson)