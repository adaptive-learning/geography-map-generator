from generator import MapGenerator

COUNTRIES_FILE = "src/ne_110m_admin_0_countries_lakes/ne_110m_admin_0_countries_lakes.shp"
CITIES_FILE = "src/ne_110m_populated_places/ne_110m_populated_places.shp"
MEDIUM_CITIES_FILE = "src/ne_50m_populated_places/ne_50m_populated_places.shp"
PHYSICAL_FILE = "src/ne_10m_geography_regions_polys/ne_10m_geography_regions_polys.shp"
RIVERS_MEDIUM_FILE = "src/ne_50m_rivers_lake_centerlines/ne_50m_rivers_lake_centerlines.shp"
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

    def generate_one(self, continent):
        config = {
            "layers": [{
                "id": "states",
                "src": COUNTRIES_FILE,
                "attributes": {
                    "name": "iso_a2",
                    "realname": "name"
                },
                "filter": self.get_filter(continent)
            }]
        }
        if continent == "Asia":
            config["bounds"] = {
                "mode": "bbox",
                "data": [40, -10, 145, 55]
            }
        elif continent == "Europe":
            config["bounds"] = {
                "mode": "bbox",
                "data": [-15, 36, 50, 70]
            }
            config["layers"].insert(0, {
                "id": "bg",
                "src": COUNTRIES_FILE,
                "join": {'export-ids': False},
                "filter": self.get_filter(continent)
            })
            config["layers"].append({
                "id": "mountains",
                "src": PHYSICAL_FILE,
                "attributes": {
                    "name": "name",
                    "realname": "name"
                },
                "filter": {"and": [
                    {"region": "Europe"},
                    {"featurecla": "Range/mtn"}
                ]}
            })
            '''
            config["layers"].append({
                "id": "rivers",
                "src": RIVERS_MEDIUM_FILE,
                "attributes": {
                    "name": "name",
                    "realname": "name"
                },
                "filter": {"and": [
                    ["name", "not in", ["Dicle", "Al Furat", "Firat", "Tigris"]],
                    {"featurecla": "River"}
                ]}
            })
            config["layers"].append({
                "id": "lakes",
                "src": LAKES_MEDIUM_FILE,
                "attributes": {
                    "name": "name",
                    "realname": "name"
                },
                "filter": {"and": [
                    ["scalerank", "not in", [4, 5, 6]],
                    ["name", "not in", ["Lake Sevana"]],
                    ["featurecla", "in", ["Lake", "Reservoir"]]
                ]}
            })
            '''
            config["layers"].append({
                "id": "cities",
                "src": CITIES_FILE,
                "attributes": {
                    "name": "NAMEASCII",
                    "realname": "NAME",
                    "state-code": "ISO_A2",
                    "population": "POP_MAX"
                },
                "filter": {"and": [
                    ["ISO_A2", "not in",
                        ["IQ", "CY", "TR", "AM", "GE", "AZ", "TN", "DZ", "MA"]
                     ],
                    ["NAME", "not in", ["The Hague", "Vatican City", "Geneva"]]
                ]}
            })
        elif continent == "North America":
            config["layers"].append({
                "id": "cities",
                "src": MEDIUM_CITIES_FILE,
                "attributes": {
                    "name": "NAMEASCII",
                    "realname": "NAME",
                    "state-code": "ISO_A2",
                    "population": "POP_MAX"
                },
                "filter": {"and": [
                    ["ISO_A2", "not in",
                        ["ML", "SM", "PT", "GN", "VE", "CO"]
                     ],
                    ["NAME", "not in", ["The Hague", "Vatican City", "Geneva"]],
                    cities_size_filter
                ]}
            })
        elif continent == "Oceania":
            config["bounds"] = {
                "mode": "bbox",
                # [minLon, minLat, maxLon, maxLat].
                "data": [110, -45, 180, 0]
            }
        filename = continent.lower()
        if continent == "North America":
            filename = "namerica"
        if continent == "South America":
            filename = "samerica"
        self.generate_map(config, filename)
