# CRISTIAN ECHEVERRÍA RABÍ

import json
#import weakref

#__all__ = ["DataBase", "List", "Field", "Number", "Text", "Date", "Bool", "FIX_TITLE"]

#-----------------------------------------------------------------------------------------

class Type:
    def __init__(self, type="SP.Field", typeKind=0, kwa={}) -> None:
        self.type = type
        self.typeKind = typeKind
        self.kwa = kwa

    def get(self):
        r = {
            "__metadata": { "type": self.type, "addToDefaultView": True },
            "FieldTypeKind": self.typeKind,
        }
        r.update(self.kwa)
        return r


class TypeNumber(Type):
    def __init__(self, decimalPlaces=0, min=None, max=None) -> None:
        super().__init__("SP.FieldNumber", 9, {"DecimalPlaces": decimalPlaces})
        if min is not None: self.kwa["Min"] = min
        if max is not None: self.kwa["Max"] = max


class TypeText(Type):
    def __init__(self, maxLength=255) -> None:
        super().__init__("SP.FieldText", 2, {"MaxLength": maxLength})


class TypeNote(Type):
    def __init__(self, numberOfLines=3, richText=False, appendOnly=False) -> None:
        super().__init__("SP.FieldMultiLineText", 3, {"NumberOfLines": numberOfLines})
        if richText: self.kwa["RichText"] = True
        if appendOnly: self.kwa["AppendOnly"] = True



Date = Type("SP.FieldDateTime", 4, {"DisplayFormat": "DateOnly"})
DateTime = Type("SP.FieldDateTime", 4, {"DisplayFormat": "DateTime"})
Bool = Type("SP.Field", 8)


#-----------------------------------------------------------------------------------------

class Field:
    def __init__(self, name, type, core=False, required=False, unique=False, index=False, default=None, description=""):
        #self.fk = False
        self.name = name
        self.type = type
        self.core = core                                # Sharepoint default field (ID, Created, CreatedBy, etc)
        self.required = required
        self.unique = unique
        self.index = False if unique else index         # unique field ya están indexados
        self.default = default
        self.description = description
    
    def get(self):
        r = self.type.get()
        r.update({
            "Title": self.name,
            "Description": self.description
        })
        if self.required: r["Required"] = self.required
        if self.unique: r["EnforceUniqueValues"] = self.unique
        if self.default is not None: r["DefaultValue"] = self.default
        return r
    
    def get_index(self, listName):
        return {
            "__metadata": { "type": "SP.Index" },
            "Name": f"{listName}{self.name}Index",
            "IndexedField": f"{self.name}",
            "IndexType": 0      # 1 implica único
        }


class Foreign(Field):
    def __init__(self, name, list, required=False, index=False, default=None, description=""):
        super().__init__(name, list.pk.type, False, required, False, index, default, description)
        #self.fk = True


#-----------------------------------------------------------------------------------------


FIX_TITLE = {
    "__metadata": { "type": "SP.FieldText" },
    "Required": False,
    "MaxLength": 1
}


#-----------------------------------------------------------------------------------------

class List:
    def __init__(self, name, pk, *fields, allowContentTypes=False):
        #self.pk = weakref.proxy(pk)
        self.pk = pk
        self.fields = [pk, *fields]

        self.name = name
        self.allowContentTypes = allowContentTypes
        self.type = "SP.List"
        self.template = 100
    
    def get_create(self):
        return {
            "__metadata": { "type": self.type },
            "Title": self.name,
            "AllowContentTypes": self.allowContentTypes,
            "BaseTemplate": self.template
        }
    
    def get_create_fields(self):
        return [x.get() for x in self.fields if not x.core]
    
    def get_create_indexes(self):
        s = []
        for i in self.fields:
            if i.index: s.append( i.get_index(self.name) )
        return s
    
    def get(self):
        return {
            "List": self.name,
            "Create": self.get_create(),
            #"Fix": FIX_TITLE,
            "CreteFields": self.get_create_fields(),
            "CreteIndexes": self.get_create_indexes()
        }
    
    def json(self):
        return json.dumps(self.get())


#-----------------------------------------------------------------------------------------

class DataBase:
    def __init__(self, *lists):
        self.lists = lists
    
    def get(self):
        return [x.get() for x in self.lists]
    
    def json(self):
        return json.dumps(self.get())
