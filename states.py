from generator import MapGenerator

PROVINCES_BIG_FILE = "src/ne_10m_admin_1_states_provinces_lakes/ne_10m_admin_1_states_provinces_lakes.shp"
PROVINCES_MEDIUM_FILE = "src/ne_50m_admin_1_states_provinces_lakes/ne_50m_admin_1_states_provinces_lakes.shp"
ITALY_FILE = "src/ITA_adm/ITA_adm1.shp"
SPAIN_FILE = "src/ESP_adm/ESP_adm1.shp"
FRANCE_FILE = "src/FRA_adm/FRA_adm1.shp"


class StatesGenerator(MapGenerator):
    default_codes = ["CZ", "DE", "AT", "CN", "IN", "US"]

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
                    ["iso_3166_2", "not in", ["US-HI", "US-AK", "CN-", "CA-"]],
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
                "id": "states",
                "src": self.get_src(state),
                "attributes": {
                    "name": self.get_name(state),
                    "realname": self.get_realname(state),
                },
                "filter": self.get_filter(state)
            }]
        }

        if state in ["CZ", "US", "CN", "DE", "AU", "CA", "IT", "ES", "FR"]:
            config["layers"][0]["simplify"] = 1
        if state in ["CZ", "AT"]:
            config["proj"] = {
                "id": "laea",
                "lon0": 15,
                "lat0": 48
            }
        if state in ["US", "CA"]:
            config["proj"] = {
                "id": "lonlat",
                "lon0": -101,
                "lat0": 40
            }
        filename = state.lower()
        self.generate_map(config, filename)
