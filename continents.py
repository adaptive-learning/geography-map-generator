# -*- coding: utf-8 -*-
from generator import MapGenerator

COUNTRIES_FILE = "src/ne_110m_admin_0_countries_lakes/ne_110m_admin_0_countries_lakes.shp"
CITIES_FILE = "src/ne_110m_populated_places/ne_110m_populated_places.shp"
MEDIUM_CITIES_FILE = "src/ne_50m_populated_places/ne_50m_populated_places.shp"
PHYSICAL_FILE = "src/ne_10m_geography_regions_polys/ne_10m_geography_regions_polys.shp"
RIVERS_MEDIUM_FILE = "my_src/ne_50m_rivers_lake_centerlines/ne_50m_rivers_lake_centerlines.shp"
LAKES_MEDIUM_FILE = "src/ne_50m_lakes/ne_50m_lakes.shp"
COAST_FILE = "src/ne_50m_land/ne_50m_land.shp"


def cities_size_filter(record):
    return record['POP_MAX'] > 10 ** 6


class ContinentsGenerator(MapGenerator):
    default_codes = ["Africa", "Europe", "Asia", "North America", "South America",
                     "Oceania"]

    def get_filter(self, continent):
        if continent == "Asia":
            return {"or": [
                ["iso_a2", "is", "RU"],
                {"continent": "Asia"},
            ]}
            return ["HASC_1", "not in", ["ES.CN", "ES.CE"]]
        else:
            return {"continent": continent}

    def cities_filter(self, continent):
        filters = {
            'Asia': {"and": [
                ["ISO_A2", "not in",
                    ["MK", "XK", "HR", "AL", "BG", "BA", "SC", "MT", "HU",
                     "RO", "GR", "UA", "ET", "IT", "RU", "KE", "EG", "ME",
                     "KM", "SM", "TZ", "-99", "DJ", "MD", "SO", "ER", "RS",
                     "SD", "VA"]
                 ],
                ["NAME", "not in", ["Sri Jawewardenepura Kotte", "Kyoto"]]
            ]},
            'Europe': {"and": [
                ["ISO_A2", "not in",
                    ["IQ", "CY", "TR", "AM", "GE", "AZ", "TN", "DZ", "MA", "SY", "KW", "LB"]
                 ],
                ["NAME", "not in", ["The Hague", "Vatican City", "Geneva"]]
            ]},
            "Africa": {"and": [
                ["ISO_A2", "not in",
                    ["IQ", "CY", "TR", "AM", "GE", "SY", "KW", "LB", "MT",
                     "QA", "BH", "GW", "JO", "IL", "YE", "IR", "SA"]
                 ],
                ["NAME", "not in", ["Brazzaville", "Lobamba", "Cotonou"]]
            ]},
            "North America": {"and": [
                ["ISO_A2", "not in",
                    ["VE", "IS", "PT", "SM", "EH", "MA", "SL", "GM", "CV",
                     "GW", "MR", "ML", "GN"]
                 ],
                ["NAME", "not in", ["Sri Jawewardenepura Kotte", "Kyoto"]]
            ]},
            "South America": {"and": [
                ["ISO_A2", "not in", ["TT", "GD", "PA"]],
                ["NAME", "not in", ["Valparaiso"]],
            ]},
            "Oceania": ["ISO_A2", "not in", ["TL"]],
        }
        return filters.get(continent, {})

    def generate_one(self, continent):
        config = {
            "layers": [{
                "id": "bg",
                "src": COUNTRIES_FILE,
                "join": {'export-ids': False},
                "filter": self.get_filter(continent)
            }, {
                "id": "state",
                "src": COUNTRIES_FILE,
                "attributes": {
                    "code": "iso_a2",
                    "name": "name",
                    "population": "pop_est",
                },
                "filter": self.get_filter(continent)
            }]
        }
        if continent == "Asia":
            config["bounds"] = {
                "mode": "bbox",
                "data": [35, -10, 145, 55]
            }
            config["layers"].append({
                "id": "island",
                "src": PHYSICAL_FILE,
                "simplify": 1,
                "attributes": {
                    "code": "name",
                    "name": "name"
                },
                "charset": "cp1252",
                "filter": {"and": [
                    {"region": continent},
                    {"featurecla": "Island"},
                    lambda r: r["scalerank"] < 5,
                ]}
            })
            config["layers"].append({
                "id": "mountains",
                "src": PHYSICAL_FILE,
                "attributes": {
                    "code": "name",
                    "name": "name"
                },
                "filter": {"and": [
                    {"region": continent},
                    {"featurecla": "Range/mtn"},
                    lambda r: r["scalerank"] < 3,
                ]}
            })
        elif continent == "Europe":
            config["bounds"] = {
                "mode": "bbox",
                "data": [-15, 35, 50, 70]
            }
            config["layers"].append({
                "id": "island",
                "src": PHYSICAL_FILE,
                "simplify": 1,
                "attributes": {
                    "code": "name",
                    "name": "name"
                },
                "charset": "cp1252",
                "filter": {"and": [
                    {"region": continent},
                    {"featurecla": "Island"},
                    lambda r: r["name"].decode('cp1252').encode('utf') != "Pelopónnisos",
                ]}
            })
            config["layers"].append({
                "id": "mountains",
                "src": PHYSICAL_FILE,
                "attributes": {
                    "code": "name",
                    "name": "name"
                },
                "filter": {"and": [
                    {"region": "Europe"},
                    {"featurecla": "Range/mtn"}
                ]}
            })
            config["layers"].append({
                "id": "river",
                "src": RIVERS_MEDIUM_FILE,
                "attributes": {
                    "code": "name",
                    "name": "name"
                },
                "filter": {"and": [
                    ["name", "not in", ["Dicle", "Al Furat", "Firat", "Tigris"]],
                    ["name", "not in", [
                        "Borcea",
                        "Bratul Chillia",
                        "Bratul Sfintu Gheorghe",
                        "Bratul Sulina",
                        "Ferenc Csatorna",
                        "Göta älv",
                        "Kokemäenjoki",
                        "Soroksari Duna",
                        "Vuoksi",
                        "Svir’",
                        "Neva",
                        "Kem",
                    ]],
                    {"featurecla": "River"}
                ]}
            })
            '''
            config["layers"].append({
                "id": "lake",
                "src": LAKES_MEDIUM_FILE,
                "attributes": {
                    "code": "name",
                    "name": "name"
                },
                "filter": {"and": [
                    ["scalerank", "not in", [4, 5, 6]],
                    ["name", "not in", ["Lake Sevana"]],
                    ["featurecla", "in", ["Lake", "Reservoir"]]
                ]}
            })
            '''
        elif continent == "Oceania":
            config["bounds"] = {
                "mode": "bbox",
                # [minLon, minLat, maxLon, maxLat].
                "data": [110, -45, 180, 0]
            }

        config["layers"].append({
            "id": "city",
            "src": CITIES_FILE,
            "attributes": {
                "code": "NAMEASCII",
                "name": "NAME",
                "state-code": "ISO_A2",
                "population": "POP_MAX"
            },
            "filter": self.cities_filter(continent)
        })
        filename = continent.lower()
        if continent == "North America":
            filename = "namerica"
        if continent == "South America":
            filename = "samerica"
        self.generate_map(config, filename)
