from generator import MapGenerator

COUNTRIES_FILE = "src/ne_110m_admin_0_countries_lakes/ne_110m_admin_0_countries_lakes.shp"
CITIES_FILE = "src/ne_110m_populated_places/ne_110m_populated_places.shp"


class ContinentsGenerator(MapGenerator):
    default_codes = ["Africa", "Europe", "Asia", "North America", "South America",
                     "Oceania"]

    def generate_one(self, continent):
        config = {
            "layers": [{
                "id": "states",
                "src": COUNTRIES_FILE,
                "attributes": {
                    "name": "iso_a2",
                    "realname": "name"
                },
                "filter": {"continent": continent}
            }]
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
            config["layers"].append({
                "id": "cities",
                "src": CITIES_FILE,
                "attributes": {
                    "name": "NAME",
                    "realname": "NAME",
                    "state-code": "ISO_A2"
                },
                "filter": {"and": [
                    ["ISO_A2", "not in",
                        ["IQ", "CY", "TR", "AM", "GE", "AZ", "TN", "DZ", "MA"]
                     ],
                    ["NAME", "not in", ["The Hague", "Vatican City"]]
                ]}
            })
        if continent == "Oceania":
            config["bounds"] = {
                "mode": "bbox",
                # [minLon, minLat, maxLon, maxLat].
                "data": [110, -45, 180, 0]
            }
        if continent == "North America":
            filename = "namerica"
        if continent == "South America":
            filename = "samerica"
        self.generate_map(config, filename)