from generator import MapGenerator

PROVINCES_BIG_FILE = "src/ne_10m_admin_1_states_provinces_lakes/ne_10m_admin_1_states_provinces_lakes.shp"
ITALY_FILE = "src/ITA_adm/ITA_adm1.shp"
SPAIN_FILE = "src/ESP_adm/ESP_adm1.shp"
FRANCE_FILE = "src/FRA_adm/FRA_adm1.shp"
COAST_FILE = "src/ne_50m_land/ne_50m_land.shp"
COUNTRIES_MEDIUM_FILE = "src/ne_50m_admin_0_countries_lakes/ne_50m_admin_0_countries_lakes.shp"
MEDIUM_CITIES_FILE = "src/ne_50m_populated_places/ne_50m_populated_places.shp"
PHYSICAL_FILE = "src/ne_10m_geography_regions_polys/ne_10m_geography_regions_polys.shp"
RIVERS_MEDIUM_FILE = "src/ne_50m_rivers_lake_centerlines/ne_50m_rivers_lake_centerlines.shp"
LAKES_MEDIUM_FILE = "src/ne_50m_lakes/ne_50m_lakes.shp"


def cities_size_filter(record):
    return record['POP_MAX'] > 5 * 10 ** 5


class StatesGenerator(MapGenerator):
    default_codes = ["CZ", "DE", "AT", "CN", "IN", "US", "ES", "IT", "FR", "CA", "AU"]

    def get_name(self, state):
        if state in ["CZ", "US", "CN", "CA"]:
            return "iso_3166_2"
        elif state in ["DE", "AT", "AU", "IN"]:
            return "code_hasc"
        elif state in ["IT", "FR"]:
            return "NAME_1"
        elif state in ["ES"]:
            return "HASC_1"
        else:
            return "name"

    def get_realname(self, state):
        if state in ["IT", "ES", "FR"]:
            return "NAME_1"
        else:
            return "name"

    def get_bg_src(self, state):
        if state in ["US", "CA"]:
            return COUNTRIES_MEDIUM_FILE
        else:
            return COAST_FILE

    def get_src(self, state):
        if state == "IT":
            return ITALY_FILE
        elif state == "ES":
            return SPAIN_FILE
        elif state == "FR":
            return FRANCE_FILE
        else:
            return PROVINCES_BIG_FILE

    def get_filter(self, state):
        if state in ["IT", "ES", "FR"]:
            return ["HASC_1", "not in", ["ES.CN", "ES.CE"]]
        elif state in ["IN", "CN", "US", "CA", "AU"]:
            return {
                "and": [
                    {"iso_a2": state},
                    ["iso_3166_2", "not in", ["US-HI", "US-AK", "US-DC", "CA-"]],
                    ["code_hasc", "not in", ["AU", "AU.JB"]],
                    ["name", "not in", [
                        "Andaman and Nicobar",
                        "Chandigarh",
                        "Dadra and Nagar Haveli",
                        "Daman and Diu",
                        "Lakshadweep",
                        "Puducherry",
                    ]]
                ]
            }
        else:
            return {"iso_a2": state}

    def generate_one(self, state):
        config = {
            "layers": [{
                "id": "bg",
                "src": self.get_bg_src(state),
                "simplify": 5,
            }, {
                "id": "states",
                "src": self.get_src(state),
                "attributes": {
                    "name": self.get_name(state),
                    "realname": self.get_realname(state),
                },
                "filter": self.get_filter(state),
            }],
            "bounds": {
                "mode": "polygons",
                "data": {
                    "layer": "states",
                },
            }
        }

        if state in ["US", "CN", "DE", "AU", "IT", "ES", "FR", "CA"]:
            config["layers"][1]["simplify"] = 1
        if state in ["CZ", "AT"]:
            config["proj"] = {
                "id": "laea",
                "lon0": "auto",
                "lat0": "auto"
            }
        if state in ["US", "CA"]:
            config["layers"][0]["simplify"] = 2
            config["proj"] = {
                "id": "lonlat",
                "lon0": "auto",
                "lat0": 40
            }
        if state in ["IT", "CA"]:
            config["layers"].pop(0)

        if state == "US":
            '''
            config["layers"].append({
                "id": "mountains",
                "src": PHYSICAL_FILE,
                "attributes": {
                    "name": "name",
                    "realname": "name"
                },
                "filter": {"and": [
                    {"region": "North America"},
                    {"featurecla": "Range/mtn"},
                    ["name", "not in", [
                        "SIERRA MADRE OCCIDENTAL",
                        "SIERRA MADRE ORIENTAL",
                        "COAST MOUNTAINS"
                    ]],
                ]}
            })
            config["layers"].append({
                "id": "rivers",
                "src": RIVERS_MEDIUM_FILE,
                "attributes": {
                    "name": "name",
                    "realname": "name"
                },
                "filter": {"and": [
                    ["name", "not in", []],
                    ["scalerank", "not in", [4, 5, 6]],
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
                "src": MEDIUM_CITIES_FILE,
                "attributes": {
                    "name": "NAMEASCII",
                    "realname": "NAME",
                    "state-code": "ISO_A2",
                    "population": "POP_MAX"
                },
                "filter": {"and": [
                    ["ISO_A2", "in",
                        ["US"]
                     ],
                    ["NAME", "not in", ["St. Paul", "Vancouver"]],
                    cities_size_filter
                ]}
            })
        filename = state.lower()
        self.generate_map(config, filename)
