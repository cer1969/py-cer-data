# CRISTIAN ECHEVERRÍA RABÍ

import model

#-----------------------------------------------------------------------------------------

data = model.Area.json()

f = open("sh_area_list.json", "w")
f.write( data )
f.close()

print( data )