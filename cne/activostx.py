# © Cristian Echeverría Rabí

import requests

#---------------------------------------------------------------------------------------------------
# https://activos-tx-prod.appspot.com/api/v1/
# https://api-infotecnica.coordinador.cl/v1/
BASE_URL = "https://activos-tx-prod.appspot.com/api/v1/"

#---------------------------------------------------------------------------------------------------

class Table:
    
    def __init__(self, name):
        self.name = name
        self.url = f"{BASE_URL}{name}/"
    
    def get(self, **kw):
        r = requests.get(self.url, params=kw)
        data = r.json()
        return data
    
    def get_by_id(self, id):
        point = f"{self.url}{id}/"
        r = requests.get(point)
        data = r.json()
        return data

    def count(self, **kw):
        # Con page_size 1 debería devolver count más rápido
        data = self.get(page_size=1, **kw)
        return data["count"]

    def get_data_page(self, **kw):
        data = self.get(**kw)
        return data["results"]
    
    def get_data_all(self, page_size=100, pmin=1, pmax=None, **kw):
        page = pmin
        data = []
        while True:
            d = self.get(page=page, page_size=page_size, **kw)
            data.extend(d["results"])

            print(f"page: {page} - {len(d['results'])} - {len(data)}")

            if pmax is not None and page >= pmax:
                break
            if d["next"] is None:
                break

            page = page + 1
        return data


#---------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    t = Table("oocc")
    print(t.count(decreto_id=1057))
    # parece que le max de page_size es 1000
    # data = t.get_data_all(decreto_id=1057, page_size=100)
    # print(len(data))
    # item = t.get_by_id(8)
    # print(item)

# import pandas as pd

# people = [
#     {'name': 'Alice', 'age': 25, 'city': 'New York'},
#     {'name': 'Bob', 'age': 30, 'city': 'Chicago'},
#     {'name': 'Charlie', 'age': 35, 'city': 'Los Angeles'}
# ]

# # Crear el DataFrame y establecer 'name' como índice
# df = pd.DataFrame(people).set_index('name')

# print(df)

# En la distribución normal (campana de Gauss), los porcentajes de datos que se cubren con desviaciones estándar son los siguientes:

# 1. Una desviación estándar (±1σ): Aproximadamente el 68.27% de los datos
# 2. Dos desviaciones estándar (±2σ): Aproximadamente el 95.45% de los datos
# 3. Tres desviaciones estándar (±3σ): Aproximadamente el 99.73% de los datos

# Estos porcentajes se conocen como la "regla empirica" o "regla 68-95-99.7" en estadística. Esto significa que:
# - Cerca del 68% de los datos están dentro de una desviación estándar de la media
# - Cerca del 95% de los datos están dentro de dos desviaciones estándar de la media
# - Casi el 99.7% de los datos están dentro de tres desviaciones estándar de la media

# Es importante recordar que estos porcentajes son precisos solo para distribuciones que siguen una distribución normal (campana de Gauss).