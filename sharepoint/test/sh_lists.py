# CRISTIAN ECHEVERRÍA RABÍ

import model

#-----------------------------------------------------------------------------------------

data = model.db.json()

f = open("sh_list.json", "w")
f.write(data)
f.close()

print( data )