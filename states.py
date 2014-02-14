from generator import MapGenerator

PROVINCES_BIG_FILE = "src/ne_10m_admin_1_states_provinces_lakes/ne_10m_admin_1_states_provinces_lakes.shp"
PROVINCES_MEDIUM_FILE = "src/ne_50m_admin_1_states_provinces_lakes/ne_50m_admin_1_states_provinces_lakes.shp"


class StatesGenerator(MapGenerator):
    default_codes = ["CZ", "DE", "AT", "CN", "IN", "US"]

    def generate_one(self, state):
        config = {
            "layers": [{
                "id": "states",
                "src": PROVINCES_BIG_FILE,
                "attributes": {
                    "name": "name",
                    "realname": "name",
                },
                "filter": {"iso_a2": state}
            }]
        }
        if state in ["CZ", "US", "CN", "CA"]:
            config["layers"][0]["attributes"]["name"] = "iso_3166_2"
        if state in ["DE", "AT"]:
            config["layers"][0]["attributes"]["name"] = "code_hasc"
        if state in ["IN", "CN", "US"]:
            config["layers"][0]["filter"] = {
                "and": [
                    config["layers"][0]["filter"],
                    ["iso_3166_2", "not in", ["US-HI", "US-AK", "CN-"]],
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
        if state in ["CZ", "US", "CN", "DE", "AU", "CA"]:
            config["layers"][0]["simplify"] = 1
        if state in ["CZ", "AT"]:
            config["proj"] = {
                "id": "laea",
                "lon0": 15,
                "lat0": 48
            }
        if state == "US":
            config["proj"] = {
                "id": "lonlat",
                "lon0": -101,
                "lat0": 40
            }
        filename = state.lower()
        self.generate_map(config, filename)
