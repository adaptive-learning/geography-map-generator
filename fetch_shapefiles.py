#!/usr/bin/python
import urllib
from zipfile import ZipFile


urls = [
    "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries_lakes.zip",
    "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_0_countries_lakes.zip",
    "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_populated_places.zip",
    "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_populated_places.zip",
    "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_populated_places.zip",
    "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_1_states_provinces_lakes.zip",
    "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/physical/ne_50m_land.zip",
    "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/physical/ne_10m_geography_regions_polys.zip",
    "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/physical/ne_50m_rivers_lake_centerlines.zip",
    "http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/physical/ne_50m_lakes.zip",
    "http://biogeo.ucdavis.edu/data/gadm2/shp/ITA_adm.zip",
    "http://biogeo.ucdavis.edu/data/gadm2/shp/ESP_adm.zip",
    "http://biogeo.ucdavis.edu/data/gadm2/shp/FRA_adm.zip",
]


def main():
    for url in urls:
        print url
        name, headers = urllib.urlretrieve(url)
        zp = ZipFile(name)
        zp.extractall("src/" + url[url.rfind('/'):-4])

if __name__ == '__main__':
    main()
