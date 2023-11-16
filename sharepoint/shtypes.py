# CRISTIAN ECHEVERRÍA RABÍ

import json

__all__ = ["DataBase", "List", "Field", "Number", "Text", "Date", "Bool", "FIX_TITLE"]

#-----------------------------------------------------------------------------------------

FIX_TITLE = {
    "__metadata": { "type": "SP.FieldText" },
    "Required": False,
    "MaxLength": 1
}


#-----------------------------------------------------------------------------------------

class DataBase:
    def __init__(self, lists=[]):
        self.lists = lists
    
    def get(self):
        return [x.get() for x in self.lists]
    
    def json(self):
        return json.dumps(self.get())


#-----------------------------------------------------------------------------------------

class List:
    def __init__(self, name, fields=[], contentTypes=False):
        self.name = name
        self.fields = fields
        self.contentTypes = contentTypes
        self.type = "SP.List"
        self.template = 100
    
    def get_create(self):
        return {
            "__metadata": { "type": self.type },
            "Title": self.name,
            "AllowContentTypes": self.contentTypes,
            "BaseTemplate": self.template
        }
    
    def get_create_fields(self):
        return [x.get_create() for x in self.fields]
    
    def get_create_indexes(self):
        s = []
        for i in self.fields:
            if i.index: s.append( i.get_index(self.name) )
        return s
    
    def get(self):
        return {
            "List": self.name,
            "Create": self.get_create(),
            "Fix": FIX_TITLE,
            "CreteFields": self.get_create_fields(),
            "CreteIndexes": self.get_create_indexes()
        }
    
    def json(self):
        return json.dumps(self.get())


#-----------------------------------------------------------------------------------------

class Field:
    def __init__(self, name, required=False, unique=False, index=False, default=None, description=""):
        self.name = name
        self.required = required
        self.unique = unique
        self.index = False if unique else index         # unique field ya están indexados
        self.default = default
        self.description = description
        self.type = "SP.Field"
        self.typeKind = 0
    
    def get_create(self):
        r = {
            "__metadata": { "type": self.type, "addToDefaultView": True },
            "FieldTypeKind": self.typeKind,
            "Title": self.name,
            "Description": self.description
        }
        if self.required: r["Required"] = self.required
        if self.unique: r["EnforceUniqueValues"] = self.unique
        if self.default is not None: r["DefaultValue"] = self.default
        return r
    
    def get_index(self, list):
        return {
            "__metadata": { "type": "SP.Index" },
            "Name": f"{list}{self.name}Index",
            "IndexedField": f"{self.name}",
            "IndexType": 0      # 1 implica único
        }


#-----------------------------------------------------------------------------------------

class Number(Field):
    def __init__(self, name, required=False, unique=False, index=False, decimals=None, default=None, description=""):
        super().__init__(name, required, unique, index, default, description)
        self.decimals = decimals
        self.type = "SP.FieldNumber"
        self.typeKind = 1
    
    def get_create(self):
        r = super().get_create()
        if self.decimals is not None: r["DecimalPlaces"] = self.decimals
        return r


class Text(Field):
    def __init__(self, name, required=False, unique=False, index=False, maxLength=255, default=None, description=""):
        super().__init__(name, required, unique, index, default, description)
        self.maxLength = maxLength
        self.type = "SP.FieldText"
        self.typeKind = 2
    
    def get_create(self):
        r = super().get_create()
        r["MaxLength"] = self.maxLength
        return r


class Date(Field):
    def __init__(self, name, required=False, unique=False, index=False, dateOnly=False, default=None, description=""):
        super().__init__(name, required, unique, index, default, description)
        self.dateOnly = dateOnly
        self.type = "SP.FieldDateTime"
        self.typeKind = 4
    
    def get_create(self):
        r = super().get_create()
        r["DateTimeFormat"] = "DateOnly" if self.dateOnly else "DateTime"
        return r


class Bool(Field):
    def __init__(self, name, required=False, unique=False, index=False, decimals=None, default=False, description=""):
        super().__init__(name, required, unique, index, default, description)
        self.typeKind = 8