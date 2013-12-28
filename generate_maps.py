#!/usr/bin/python

from kartograph import Kartograph
import re
import optparse

PROVINCES_BIG_FILE = "src/ne_10m_admin_1_states_provinces_lakes/ne_10m_admin_1_states_provinces_lakes.shp"
PROVINCES_MEDIUM_FILE = "src/ne_50m_admin_1_states_provinces_lakes/ne_50m_admin_1_states_provinces_lakes.shp"
COUNTRIES_MEDIUM_FILE = "src/ne_50m_admin_0_countries_lakes/ne_50m_admin_0_countries_lakes.shp"
COUNTRIES_FILE = "src/ne_110m_admin_0_countries_lakes/ne_110m_admin_0_countries_lakes.shp"
CITIES_BIG_FILE = "src/ne_10m_populated_places/ne_10m_populated_places.shp"
CITIES_MEDIUM_FILE = "src/ne_50m_populated_places/ne_50m_populated_places.shp"
CITIES_FILE = "src/ne_110m_populated_places/ne_110m_populated_places.shp"
RIVERS_FILE = "src/ne_110m_rivers_lake_centerlines/ne_110m_rivers_lake_centerlines.shp"
LAKES_FILE = "src/ne_110m_lakes/ne_110m_lakes.shp"


def main():
    p = optparse.OptionParser()
    options, arguments = p.parse_args()
    if len(arguments) < 1:
        generate_continents([])
        generate_world()
        generate_states([])
        generate_regions([])
    else:
        maps = arguments.pop(0)
        codes = arguments
        if maps == 'states':
            generate_states(codes)
        elif maps == 'continents':
            generate_continents(codes)
        elif maps == 'world':
            generate_world()
        elif maps == 'regions':
            generate_regions(codes)


def cities_size_filter(record):
    return record['POP_MIN'] > 10 ** 6


def generate_world():
    config = {
       "layers": [{
           "id": "states",
           "src": COUNTRIES_FILE,
            "attributes": {
              "name": "iso_a2",
              "realname": "name",
            },
            "filter": ["iso_a2", "is not", "AQ"]
         }
       ]
    }
    generate(config, "world")


def generate_regions(codes):
    regions = ["Latin America & Caribbean"] if len(codes) == 0 else codes
    for region in regions:
        config = {
           "layers": [{
               "id": "states",
               "src": COUNTRIES_FILE,
                "attributes": {
                  "name": "iso_a2"
                },
                "filter": {"region_wb": region}
             }
           ]
        }
        filename = region.lower().replace(" ", "")
        if region == "Latin America & Caribbean":
            config["layers"][0]["filter"] = {
                "and": [
                    ["region_wb", "is", region],
                    ["continent", "is not", "South America"]
                ]
            }
            filename = "camerica"
        generate(config, filename)


def generate_continents(codes):
    continents = ["Africa", "Europe", "Asia", "North America", "South America",
                   "Oceania"] if len(codes) == 0 else codes
    for continent in continents:
        config = {
           "layers": [{
               "id": "states",
               "src": COUNTRIES_FILE,
                "attributes": {
                  "name": "iso_a2"
                },
                "filter": {"continent": continent}
             }, {
           "id": "cities",
           "src": CITIES_FILE,
            "attributes": {
              "name": "NAME",
              "state-code": "ISO_A2"
            }
         }
           ]
        }
        filename = continent.lower()
        if continent == "Asia":
            config["layers"][0]["filter"] = {"or": [
                ["iso_a2", "is", "RU"],
                {"continent": "Asia"},
            ]}
            config["bounds"] = {
                "mode": "bbox",
                "data": [40, -10, 145, 55]
            }
        if continent == "Europe":
            config["bounds"] = {
                "mode": "bbox",
                "data": [-15, 36, 50, 70]
            }
            config["layers"][1]["filter"] = ["ISO_A2", "not in",
                  ["IQ", "CY", "TR", "AM", "GE", "AZ", "TN", "DZ", "MA"]
            ]
        if continent == "Oceania":
            config["bounds"] = {
            "mode": "bbox",
#            [minLon, minLat, maxLon, maxLat].
            "data": [110, -45, 180, 0]
            }
        if continent == "North America":
            filename = "namerica"
        if continent == "South America":
            filename = "samerica"
        generate(config, filename)


def generate_states(codes):
    if len(codes) == 0:
        states = ["CZ", "DE", "AT", "CN", "IN", "US"]
    else:
        states = [c.upper() for c in codes]
    for state in states:
        config = {
           "layers": [{
               "id": "states",
               "src": PROVINCES_BIG_FILE,
               "attributes": {
                  "name": "iso_3166_2",
                  "realname": "name",
               },
                "filter": {"iso_a2": state}
             }, {
               "id": "cities",
               "src": CITIES_BIG_FILE,
               "attributes": {
                  "name": "NAME",
                  "state-code": "ISO_A2"
               },
                "filter": {"ISO_A2": state}
             }
           ]
        }
        if state in ["IN", "CN", "US"]:
            config["layers"][0]["filter"] = {
                "and": [
                    config["layers"][0]["filter"],
                    ["iso_3166_2", "not in", ["US-HI", "US-AK"]]
                ]
            }
            config["layers"][1]["filter"] = {
                "and": [
                    cities_size_filter,
                    config["layers"][1]["filter"]
                ]
            }
            config["layers"][0]["simplify"] = 1
        filename = state.lower()
        generate(config, filename)


def generate(config, name):
    K = Kartograph()
    file_name = 'map/' + name + '.svg'
    K.generate(config, outfile=file_name)
    codes_hacks(file_name)
    print "generated map:", file_name


def codes_hacks(file_name):
    mapFile = open(file_name)
    map_data = mapFile.read()
    mapFile.close()

    mapFile = open(file_name, 'w')

    def dashrepl(matchobj):
        return matchobj.group(0).lower()
    map_data = re.sub(r'"[A-Z]{2}"', dashrepl, map_data)
    if "europe" in file_name:
        # set missing iso codes of Kosovo xk
        map_data = re.sub(r'"-99"', '"xk"', map_data)
    if "world" in file_name:
        map_data = re.sub(r'r="2"', 'r="4"', map_data)
        # set missing iso codes of Kosovo and Somaliland to xk and xs
        map_data = map_data.replace('data-name="-99" data-realname="Kosovo"',
                                     'data-name="xk" data-realname="Kosovo"')
        map_data = map_data.replace('data-name="-99" data-realname="Somaliland"',
                                     'data-name="xs" data-realname="Somaliland"')
        # TODO: set missing iso code of Northern Cyprus. But what code?
    else:
        map_data = re.sub(r'r="2"', 'r="8"', map_data)
    mapFile.write(map_data)
    mapFile.close()


if __name__ == '__main__':
    main()
