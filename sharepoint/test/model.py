# CRISTIAN ECHEVERRÍA RABÍ

import cer.data.sharepoint as sh

#-----------------------------------------------------------------------------------------

AREA_CODE = sh.TypeText(3)
ROLE_CODE = sh.TypeText(15)
TXT_050 = sh.TypeText(50)
TXT_100 = sh.TypeText(100)
ORDER = sh.TypeNumber(decimals=0, min=0)
# Standard Sharepoint
ID = sh.TypeNumber(decimals=0)

#-----------------------------------------------------------------------------------------
# DEVEL LISTS: Listas relacionadas con la implementación

Role = sh.List("Role",
    sh.Field("Code", ROLE_CODE, required=True, unique=True, description="Role Code"),
    sh.Field("Detail", TXT_100, description="Role description"),
    sh.Field("ForArea", sh.Bool, required=True, index=True, default="1", description="True: Area; false: General"),
    sh.Field("Active", sh.Bool, required=True, index=True, default="1", description="True: Active"),
)

#-----------------------------------------------------------------------------------------
# USER LISTS: Listas con datos de usuarios y modificadas por las aplicaciones

Area = sh.List("Area",
    sh.Field("Code", AREA_CODE, required=True, unique=True, description="Area Code"),
    sh.Field("Name", TXT_050, required=True, description="Area Name"),
    sh.Field("Order", ORDER, required=True, index=True, description="Items order (10, 20, ...)"),
    sh.Field("Active", sh.Bool, required=True, index=True, default="1", description="True: Active"),
)

UserRole = sh.List("UserRole",
    sh.Field("ID", ID, core=True),
    sh.Field("Email", TXT_050, required=True, index=True, description="User Email"),
    sh.Foreign("Role", Role, required=True, index=True, description="Role Code"),
    sh.Foreign("Area", Area, index=True, description="Area Code"),
    sh.Field("Active", sh.Bool, required=True, index=True, default="1", description="True: Active"),
)

#-----------------------------------------------------------------------------------------

db = sh.DataBase(Area, Role, UserRole)