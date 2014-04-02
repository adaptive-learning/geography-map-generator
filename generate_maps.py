#!/usr/bin/python

import optparse
from continents import ContinentsGenerator
from states import StatesGenerator
from generator import MapGenerator

COUNTRIES_MEDIUM_FILE = "src/ne_50m_admin_0_countries_lakes/ne_50m_admin_0_countries_lakes.shp"
COUNTRIES_FILE = "src/ne_110m_admin_0_countries_lakes/ne_110m_admin_0_countries_lakes.shp"
CITIES_BIG_FILE = "src/ne_10m_populated_places/ne_10m_populated_places.shp"
COAST_FILE = "src/ne_50m_land/ne_50m_land.shp"
PHYSICAL_FILE = "src/ne_10m_geography_regions_polys/ne_10m_geography_regions_polys.shp"


def main():
    p = optparse.OptionParser()
    options, arguments = p.parse_args()
    if len(arguments) < 1:
        StatesGenerator().generate([])
        WorldGenerator().generate([])
        ContinentsGenerator().generate([])
    else:
        maps = arguments.pop(0)
        codes = arguments
        generator = None
        if maps == 'states':
            codes = [c.upper() for c in codes]
            generator = StatesGenerator()
        elif maps == 'continents':
            generator = ContinentsGenerator()
        elif maps == 'world':
            generator = WorldGenerator()
        if generator is not None:
            generator.generate(codes)


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
                "filter": ["iso_a2", "is not", "AQ"]
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
            }]
        }
        self.generate_map(config, "world")


if __name__ == '__main__':
    main()
