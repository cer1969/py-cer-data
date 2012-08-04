# -*- coding: utf-8 -*-

import time
from cer.data import jsonu

#-----------------------------------------------------------------------------------------

t1 = time.clock()

x = jsonu.read("test.json.gz")

print x[0]
print x[0].msg
print x[0]["user"]["birdth"].strftime("%d-%m-%Y")
print x[0].user.birdth.strftime("%d-%m-%Y")
print x[0].stamp.strftime("%d-%m-%Y %H:%M:%S")

print time.clock() - t1