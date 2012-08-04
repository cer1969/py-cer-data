# -*- coding: utf-8 -*-

from time import clock
from datetime import datetime, date, time
from cer.data import jsonu

#-----------------------------------------------------------------------------------------

def getItem(i):
    return jsonu.AttrDict({
        "user": {
            "name": u"Juán Araya",
            "birdth": date(1969, 12, 28),
        },
        "idx"    : i,
        "values" : [("ID", "VALUE"), (100, 1), (200, 2), (300, 3), (400, time(8,30))],
        "malo"   : (False, None),
        "msg"    : u"Niño malo canta una canción\nMuy bonita.",
        "stamp"  : datetime.now(),
    })

#s = jsonu.dumps(getItem(1))
#obj = jsonu.loads(s)
#print s
#print obj.values

t1 = clock()
mydata = [getItem(i) for i in range(10)]

t2 = clock()
jsonu.save("test.json", mydata, compresslevel=0)

t3 = clock()
jsonu.save("test.json.gz", mydata, compresslevel=9)

t4 = clock()

print "Tiempo creando= %f" % (t2-t1)
print "Tiempo json= %f" % (t3-t2)
print "Tiempo json.gz= %f" % (t4-t3)
print "Tiempo total= %f" % (t4-t1)