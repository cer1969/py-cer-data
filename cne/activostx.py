# © Cristian Echeverría Rabí

import requests

#---------------------------------------------------------------------------------------------------
# https://activos-tx-prod.appspot.com/api/v1/
# https://api-infotecnica.coordinador.cl/v1/
BASE_URL = "https://activos-tx-prod.appspot.com/api/v1/"

#---------------------------------------------------------------------------------------------------

class Table:
    
    def __init__(self, name, **filters):
        self.name = name
        self.filters = filters
        self.url = f"{BASE_URL}{name}/"
    
    @property
    def config(self):
        return f"Tabla '{self.name}' - Filtros: {self.filters}"

    def get(self, **kw):
        params = {}
        params.update(**self.filters, **kw)
        r = requests.get(self.url, params=params)
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
