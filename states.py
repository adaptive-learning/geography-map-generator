# -*- coding: utf-8 -*-
from generator import MapGenerator, SingleMapGenerator, dashrepl
import re

PROVINCES_BIG_FILE = "src/ne_10m_admin_1_states_provinces_lakes/ne_10m_admin_1_states_provinces_lakes.shp"
ITALY_FILE = "src/ITA_adm/ITA_adm1.shp"
SPAIN_FILE = "src/ESP_adm/ESP_adm1.shp"
FRANCE_FILE = "src/FRA_adm/FRA_adm1.shp"
COAST_FILE = "src/ne_50m_land/ne_50m_land.shp"
COUNTRIES_MEDIUM_FILE = "src/ne_50m_admin_0_countries_lakes/ne_50m_admin_0_countries_lakes.shp"
BIG_CITIES_FILE = "src/ne_10m_populated_places/ne_10m_populated_places.shp"
PHYSICAL_FILE = "src/ne_10m_geography_regions_polys/ne_10m_geography_regions_polys.shp"
RIVERS_MEDIUM_FILE = "src/ne_50m_rivers_lake_centerlines/ne_50m_rivers_lake_centerlines.shp"
LAKES_MEDIUM_FILE = "src/ne_50m_lakes/ne_50m_lakes.shp"
CZECH_MOUNTAINS = "my_src/CZE_mountains/CZE_mountains.shp"
RIVER_FILES = {
    "CZ": "my_src/reky_cr/reky_cr.shp",
    "SK": "my_src/reky_sr/reky_sr.shp",
    "AT": "my_src/shp_riversAU/reky.shp",
}
STATE_BORDERS = {
    "CZ": "my_src/hranice_cr/hranice_cr.shp",
    "SK": "my_src/reky_sr/hranice_slovensko.shp",
    "AT": "my_src/border_AU/AUT_adm0.shp",
    "FI": "my_src/fin-border/fin_border.shp",
    "NO": "my_src/nor-border/nor_border.shp",
    "SE": "my_src/swe-border/swe_border.shp",
}
CITY_FILES = {
    'CZ': "src/czech-republic-latest.shp/places.shp",
    'SK': "src/slovakia-latest.shp/places.shp",
    "FI": "my_src/fin-city/fin_city.shp",
    "NO": "my_src/nor-city/nor_city.shp",
    "SE": "my_src/swe-city/swe_city.shp",
}


def cities_size_filter(record):
    if record['ISO_A2'] in ['US', 'BR']:
        min_pop = 10 ** 6
    elif record['ISO_A2'] in ['AT', 'CZ']:
        min_pop = 10 ** 4
    elif record['ISO_A2'] in ['FR', 'ES', 'IT']:
        min_pop = 1.5 * 10 ** 5
    else:
        min_pop = 3 * 10 ** 5
    return record['POP_MAX'] > min_pop


def cz_cities_size_filter(record):
    return record['population'] > 10 ** 4


class StateGenerator(SingleMapGenerator):
    state_id = "state"
    state_src = PROVINCES_BIG_FILE

    def __init__(self, code):
        self.code = code
        self.config = self.get_config()
        self.map_name = self.get_map_name()

    def get_name(self):
        if self.code in ["CZ", "US", "CN", "CA"]:
            return "iso_3166_2"
        elif self.code in ["DE", "AT", "AU", "IN", "SK"]:
            return "code_hasc"
        elif self.code in ["IT", "FR"]:
            return "NAME_1"
        elif self.code in ["ES"]:
            return "HASC_1"
        else:
            return "name"

    def get_realname(self):
        return "name"

    def get_cities_src(self):
        if self.code in CITY_FILES:
            return CITY_FILES[self.code]
        return BIG_CITIES_FILE

    def get_bg_src(self):
        if self.code in ["US", "CA", "CZ", "SK", "AT"]:
            return COUNTRIES_MEDIUM_FILE
        else:
            return COAST_FILE

    def get_filter(self):
        if self.code in ["IN", "CN", "US", "CA", "AU"]:
            return {
                "and": [
                    {"iso_a2": self.code},
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
            return {"iso_a2": self.code}

    def get_cities_attributes(self):
        return {
            "code": "NAMEASCII",
            "name": "NAME",
            "state-code": "ISO_A2",
            "population": "POP_MAX"
        }

    def get_cities_filter(self):
        filter = {"and": [
            {"ISO_A2": self.code},
            cities_size_filter
        ]}
        if self.code == "US":
            filter['and'].append(["NAME", "not in", ["St. Paul", "Vancouver"]])
        elif self.code == "CA":
            filter['and'].append(["NAME", "not in", ["Hamilton", "Kitchener", "Oshawa"]])
        elif self.code == "AT":
            filter['and'].append(["NAME", "not in", ["Passau"]])
        return filter

    def get_config(self):
        config = {
            "layers": [{
                "id": "bg",
                "src": self.get_bg_src(),
                "simplify": 5,
            }, {
                "id": self.state_id,
                "src": self.state_src,
                "attributes": {
                    "code": self.get_name(),
                    "name": self.get_realname(),
                },
                "filter": self.get_filter(),
            }],
            "bounds": {
                "mode": "polygons",
                "data": {
                    "layer": self.state_id,
                },
            }
        }

        if self.code in ["US", "CN", "DE", "AU", "IT", "ES", "FR", "CA"]:
            config["layers"][1]["simplify"] = 1
        if self.code in ["CZ", "AT", "SK"]:
            config["proj"] = {
                "id": "laea",
                "lon0": "auto",
                "lat0": "auto"
            }
        if self.code in ["US", "CA"]:
            config["layers"][0]["simplify"] = 2
            config["proj"] = {
                "id": "lonlat",
                "lon0": "auto",
                "lat0": 40
            }

        if self.code not in ["CN", "IN"]:
            config["layers"].append({
                "id": "city",
                "src": self.get_cities_src(),
                "attributes": self.get_cities_attributes(),
                "filter": self.get_cities_filter()
            })
        return config


class EsItFrGenerator(StateGenerator):
    def get_realname(self):
        return "NAME_1"

    def get_filter(self):
        return ["HASC_1", "not in", ["ES.CN", "ES.CE"]]


class SpainGenerator(EsItFrGenerator):
    state_id = "autonomous_comunity"
    state_src = SPAIN_FILE


class ItalyGenerator(EsItFrGenerator):
    state_id = "region_it"
    state_src = ITALY_FILE

    def get_config(self):
        config = super(ItalyGenerator, self).get_config()
        config["layers"].pop(0)
        return config

    def hacky_fixes(self, map_data):
        CODES = {
            u'Abruzzo': u'IT-65',
            u'Apulia': u'IT-75',
            u'Basilicata': u'IT-77',
            u'Calabria': u'IT-78',
            u'Campania': u'IT-72',
            u'Emilia-Romagna': u'IT-45',
            u'Friuli-Venezia_Giulia': u'IT-36',
            u'Lazio': u'IT-62',
            u'Liguria': u'IT-42',
            u'Lombardia': u'IT-25',
            u'Marche': u'IT-57',
            u'Molise': u'IT-67',
            u'Piemonte': u'IT-21',
            u'Sardegna': u'IT-88',
            u'Sicily': u'IT-82',
            u'Toscana': u'IT-52',
            u'Trentino-Alto_Adige': u'IT-32',
            u'Umbria': u'IT-55',
            u'Valle_d\'Aosta': u'IT-23',
            u'Veneto': u'IT-34',
        }
        pattern = re.compile('-code="(' + '|'.join(CODES.keys()) + ')"')
        map_data = pattern.sub(lambda x: u'-code="' + CODES[x.group(1)] + u'"', map_data)
        return map_data


class FranceGenerator(EsItFrGenerator):
    state_id = "region"
    state_src = FRANCE_FILE

    def hacky_fixes(self, map_data):
        CODES = {
            u'Alsace': u'FR-A',
            u'Aquitaine': u'FR-B',
            u'Auvergne': u'FR-C',
            u'Basse-Normandie': u'FR-P',
            u'Bourgogne': u'FR-D',
            u'Bretagne': u'FR-E',
            u'Centre': u'FR-F',
            u'Champagne-Ardenne': u'FR-G',
            u'Corse': u'FR-H',
            u'Franche-Comte': u'FR-I',
            u'Haute-Normandie': u'FR-Q',
            u'Ile-de-France': u'FR-J',
            u'Languedoc-Roussillon': u'FR-K',
            u'Limousin': u'FR-L',
            u'Lorraine': u'FR-M',
            u'Midi-Pyrenees': u'FR-N',
            u'Nord-Pas-de-Calais': u'FR-O',
            u'Pays_de_la_Loire': u'FR-R',
            u'Picardie': u'FR-S',
            u'Poitou-Charentes': u'FR-T',
            u'Provence-Alpes-Cote-d\'Azur': u'FR-U',
            u'Rhone-Alpes': u'FR-V',
        }
        pattern = re.compile(u'-code="(' + u'|'.join(CODES.keys()) + u')"')
        map_data = map_data.decode("utf-8")
        map_data = pattern.sub(lambda x: u'-code="' + CODES[x.group(1)] + u'"', map_data)
        map_data = re.sub(r'"[A-Z]{2}\-[A-Z]"', dashrepl, map_data)
        map_data = map_data.encode("utf-8")
        return map_data


class ChinaGenerator(StateGenerator):
    state_id = "province"

    def hacky_fixes(self, map_data):
        map_data = map_data.replace('"CN-"', '"CN-35"')
        return map_data


class CanadaGenerator(StateGenerator):
    state_id = "province"

    def hacky_fixes(self, map_data):
        map_data = map_data.replace('-code="London"', '-code="London_Ca"')
        return map_data


class UsaGenerator(StateGenerator):
    def hacky_fixes(self, map_data):
        map_data = map_data.replace(',559', ',564')
        map_data = map_data.replace('r="2"', 'r="8"')
        return map_data


class IndiaGenerator(StateGenerator):
    def hacky_fixes(self, map_data):
        map_data = map_data.replace('data-code="IN." data-name="Gujarat"',
                                    'data-code="IN.GJ" data-name="Gujarat"')
        map_data = map_data.replace('data-code="IN." data-name="Tamil Nadu"',
                                    'data-code="IN.TN" data-name="Tamil Nadu"')
        return map_data


class CzSkGenerator(StateGenerator):
    state_id = "region_cz"

    def get_cities_attributes(self):
        return {
            "code": "name",
            "name": "name",
            "population": "population"
        }

    def get_cities_filter(self):
        filter = {"and": [
            ["type", "in", ["city", "town"]],
            ["name", "not in", ["Kudowa-Zdrój", "Klingenthal", "Hejnice", "Rejdice",
                                "Nyergesújfalu", "Lábatlan", "Petržalka", "Nové Mesto",
                                "Ružinov"]],
            cz_cities_size_filter
        ]}
        return filter

    def hacky_fixes(self, map_data):
        map_data = map_data.replace(
            '<g class="" id="bg">',
            '<g class="" id="bg">' +
            '<path d="M-10000.0,-10000.0L-10000.0,10000.0L10000.0,10000.0L10000.0,-10000.0Z "/>')
        return map_data


class CzechGenerator(CzSkGenerator):

    def get_config(self):
        config = super(CzSkGenerator, self).get_config()
        config["layers"][0] = {
            "id": "bg",
            "src": STATE_BORDERS[self.code],
        }
        config["layers"].append({
            "id": "mountains",
            "src": CZECH_MOUNTAINS,
            "attributes": {
                "code": "name",
                "name": "name"
            },
        })
        config["layers"].append({
            "id": "river",
            "src": RIVER_FILES["CZ"],
            "attributes": {
                "code": "NAZ_TOK",
                "name": "NAZ_TOK"
            },
        })
        return config


class SlovakiaGenerator(CzSkGenerator):

    def get_config(self):
        config = super(CzSkGenerator, self).get_config()
        config["layers"][0] = {
            "id": "bg",
            "src": STATE_BORDERS[self.code],
        }
        config["bounds"]["padding"] = 0.01
        config["layers"].append({
            "id": "river",
            "src": RIVER_FILES[self.code],
            "attributes": {
                "code": "name",
                "name": "name"
            },
        })
        return config


class GermanyGenerator(StateGenerator):
    state_id = "bundesland"

    def hacky_fixes(self, map_data):
        map_data = map_data.replace('"DE."', '"DE.BB"')
        map_data = map_data.replace('r="2"', 'r="16"')
        return map_data


class GBGenerator(StateGenerator):
    def get_config(self):
        config = StateGenerator.get_config(self)
        config["layers"].pop(1)
        config["bounds"] = {
            "mode": "bbox",
            "data": [-10, 50, 2, 59]
        }
        return config


class ScandinaviaGenerator(StateGenerator):

    def get_cities_filter(self):
        return {}

    def get_config(self):
        config = StateGenerator.get_config(self)
        config["layers"][1] = {
            "id": "border",
            "src": COUNTRIES_MEDIUM_FILE,
            "filter": {
                "iso_a2": self.code,
            },
            "simplify": 5,
        }
        config["layers"][2]['attributes'] = {
            "code": "name",
            "name": "name",
            "population": "population",
        }
        config["bounds"] = {
            "mode": "polygons",
            "data": {
                "layer": "border",
            },
        }
        return config


class NorwayGenerator(ScandinaviaGenerator):
    def get_config(self):
        config = ScandinaviaGenerator.get_config(self)
        config["bounds"] = {
            "mode": "bbox",
            "data": [3, 58, 25, 71]
        }
        return config


class AustriaGenerator(StateGenerator):
    state_id = "bundesland"

    def get_config(self):
        config = StateGenerator.get_config(self)
        config["layers"][0] = {
            "id": "bg",
            "src": STATE_BORDERS[self.code],
        }
        config["bounds"]["padding"] = 0.01
        config["layers"].append({
            "id": "river",
            "src": RIVER_FILES[self.code],
            "simplify": 1,
            "charset": "cp1250",
            "attributes": {
                "code": "name",
                "name": "name"
            },
        })
        return config

    def hacky_fixes(self, map_data):
        map_data = map_data.replace(
            '<g class="" id="bg">',
            '<g class="" id="bg">' +
            '<path d="M-10000.0,-10000.0L-10000.0,10000.0L10000.0,10000.0L10000.0,-10000.0Z "/>')
        return map_data


class MexicoArgentinaGenerator(StateGenerator):
    def hacky_fixes(self, map_data):
        map_data = re.sub(r'cy="(\d*\.\d*)" data-code="',
                          'cy="\\1" data-code="city-', map_data)
        map_data = map_data.replace('Z " data-code="Tierra_del_Fuego"',
                                    'Z " data-code="Tierra_del_Fuego-state"')
        map_data = map_data.replace('data-name="Cdrdoba"',
                                    'data-name="Cordoba"')
        return map_data


class BrazilGenerator(StateGenerator):

    def hacky_fixes(self, map_data):
        map_data = map_data.replace('data-name="Vitiria"',
                                    'data-name="Vitoria"')
        map_data = map_data.replace('data-code="Vitoria"',
                                    'data-code="Vitoria-Brazil"')
        map_data = map_data.replace('data-code="Parana"',
                                    'data-code="Parana-state"')
        map_data = map_data.replace('Z " data-code="Rio_de_Janeiro"',
                                    'Z " data-code="Rio_de_Janeiro-state"')
        return map_data


class StatesGenerator(MapGenerator):
    default_codes = ["CZ", "SK", "DE", "AT", "CN", "IN", "US", "CA",
                     "AU", "GB", "ES", "IT", "FR", "MX", "AR", "BR"]
    generators = {
        "CZ": CzechGenerator,
        "DE": GermanyGenerator,
        "AT": AustriaGenerator,
        "CN": ChinaGenerator,
        "IN": IndiaGenerator,
        "US": UsaGenerator,
        "ES": SpainGenerator,
        "IT": ItalyGenerator,
        "FR": FranceGenerator,
        "CA": CanadaGenerator,
        "AU": StateGenerator,
        "SK": SlovakiaGenerator,
        "GB": GBGenerator,
        "FI": ScandinaviaGenerator,
        "NO": NorwayGenerator,
        "SE": ScandinaviaGenerator,
        "MX": MexicoArgentinaGenerator,
        "AR": MexicoArgentinaGenerator,
        "BR": BrazilGenerator,
    }

    def generate_one(self, state):
        gen = self.generators[state](state)
        gen.generate_map()
