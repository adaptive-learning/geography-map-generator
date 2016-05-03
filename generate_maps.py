#!/usr/bin/python
# -*- coding: utf-8 -*-

import optparse
from continents import ContinentsGenerator
from states import StatesGenerator
from generator import MapGenerator

COUNTRIES_MEDIUM_FILE = "src/ne_50m_admin_0_countries_lakes/ne_50m_admin_0_countries_lakes.shp"
COUNTRIES_FILE = "src/ne_110m_admin_0_countries_lakes/ne_110m_admin_0_countries_lakes.shp"
CITIES_FILE = "src/ne_110m_populated_places/ne_110m_populated_places.shp"
COAST_FILE = "src/ne_50m_land/ne_50m_land.shp"
PHYSICAL_FILE = "src/ne_10m_geography_regions_polys/ne_10m_geography_regions_polys.shp"
RIVERS_FILE = "my_src/ne_110m_rivers_lake_centerlines/ne_110m_rivers_lake_centerlines.shp"
LAKES_FILE = "src/ne_110m_lakes/ne_110m_lakes.shp"


def main():
    p = optparse.OptionParser()
    options, arguments = p.parse_args()
    if len(arguments) < 1:
        print_usage()
    else:
        maps = arguments.pop(0)
        codes = arguments
        generator = None
        if maps == 'all':
            StatesGenerator().generate([])
            WorldGenerator().generate([])
            ContinentsGenerator().generate([])
        elif maps == 'states':
            codes = [c.upper() for c in codes]
            generator = StatesGenerator()
        elif maps == 'continents':
            generator = ContinentsGenerator()
        elif maps == 'world':
            generator = WorldGenerator()
        else:
            print_usage()
        if generator is not None:
            generator.generate(codes)


def print_usage():
    print "USAGE: \n./generate_maps.py [all|states|continents|world] [<map_codes> ...]"


def cities_size_filter(record):
    return record['POP_MAX'] > 10 ** 5


class WorldGenerator(MapGenerator):
    default_codes = ["world"]

    def generate_one(self, code):
        config = {
            "layers": [{
                "id": "bg",
                "src": COUNTRIES_FILE,
                "join": {'export-ids': False},
                "filter": ["iso_a2", "is not", "AQ"]
            }, {
                "id": "state",
                "src": COUNTRIES_FILE,
                "attributes": {
                    "code": "iso_a2",
                    "name": "name",
                    "population": "pop_est",
                },
                "filter": {"and": [
                    ["iso_a2", "is not", "AQ", "GF"],
                    ["name", "is not", "N. Cyprus"]
                ]}
            }, {
                "id": "island",
                "src": PHYSICAL_FILE,
                "simplify": 1,
                "attributes": {
                    "code": "name",
                    "name": "name"
                },
                "filter": {"and": [
                    {"featurecla": "Island"},
                    lambda r: r["scalerank"] < 4,
                    ["name", "not in", ["Great Nicobar", "N. Andaman", "Middle Andaman", "S. Andaman"]],
                    lambda r: r["name"].decode('cp1252').encode('utf') != "Bol’shoy Begichev I.",
                ]}
            }, {
                "id": "mountains",
                "src": PHYSICAL_FILE,
                "attributes": {
                    "code": "name",
                    "name": "name"
                },
                "filter": {"and": [
                    {"featurecla": "Range/mtn"},
                    lambda r: r["scalerank"] < 3,
                ]}
            }, {
                "id": "river",
                "src": RIVERS_FILE,
                "attributes": {
                    "code": "name",
                    "name": "name"
                },
                "filter": {"and": [
                    ["name", "not in", ["Peace", "Yangtze"]],
                ]}
            }, {
                "id": "lake",
                "src": LAKES_FILE,
                "attributes": {
                    "code": "name",
                    "name": "name"
                },
                "filter": {"and": [
                    ["name", "not in", [
                        "Lake Athabasca",
                        "Great Salt Lake",
                        "Lake Tana",
                        "Lake Okeechobee",
                    ]],
                ]}
            }, {
                "id": "city",
                "src": CITIES_FILE,
                "attributes": {
                    "code": "NAMEASCII",
                    "name": "NAME",
                    "state-code": "ISO_A2",
                    "population": "POP_MAX"
                },
                "filter": {"and": [
                    lambda r: r["POP_MAX"] > 2 * 10 ** 6,
                ]}
            }]
        }
        self.generate_map(config, "world")


if __name__ == '__main__':
    main()
