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
CZECH_CITIES_FILE = "src/czech-republic-latest.shp/places.shp"
SLOVAK_CITIES_FILE = "src/slovakia-latest.shp/places.shp"
CZECH_MOUNTAINS = "my_src/CZE_mountains/CZE_mountains.shp"
CZECH_RIVERS_FILE = "my_src/CZE_rivers//CZE_rivers.shp"


def cities_size_filter(record):
    if record['ISO_A2'] == 'US':
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
        return BIG_CITIES_FILE

    def get_bg_src(self):
        if self.code in ["US", "CA", "CZ"]:
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


class CzechGenerator(CzSkGenerator):
    def get_cities_src(self):
        return CZECH_CITIES_FILE

    def get_config(self):
        config = super(CzSkGenerator, self).get_config()
        config["layers"][0]["filter"] = ["iso_a2", "is", "CZ"]
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
            "src": CZECH_RIVERS_FILE,
            "attributes": {
                "code": "name",
                "name": "name"
            },
        })
        return config

    def hacky_fixes(self, map_data):
        map_data = map_data.replace(
            "M398.077452,40.651030L",
            "M-5000.0,-5000.0L-5000.0,5000.0L5000.0,5000.0L5000.0,-5000.0L-5000.0,-5000.0Z " +
            "M398.077452,40.651030L")
        #map_data = map_data.replace(
        #    "M0.000000,0.000000L0.000000,567.267337" +
        #    "L1000.000000,567.267337L1000.000000,0.000000L0.000000,0.000000Z",
        #    "M-5000.0,-5000.0L-5000.0,5000.0L5000.0,5000.0L5000.0,-5000.0L-5000.0,-5000.0Z")
        # map_data = map_data.decode('cp1252').encode('utf')
        return map_data


class SlovakiaGenerator(CzSkGenerator):
    def get_cities_src(self):
        return SLOVAK_CITIES_FILE

    def get_config(self):
        config = super(CzSkGenerator, self).get_config()
        config["bounds"]["padding"] = 0.01
        return config

    def hacky_fixes(self, map_data):
        map_data = map_data.replace(
            "M0.000000,0.000000L0.000000,510.450681" +
            "L1000.000000,510.450681L1000.000000,0.000000L0.000000,0.000000Z",
            "M-5000.0,-5000.0L-5000.0,5000.0L5000.0,5000.0L5000.0,-5000.0L-5000.0,-5000.0Z")
        return map_data


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


class AustriaGenerator(StateGenerator):
    state_id = "bundesland"


class MexicoGenerator(StateGenerator):
    state_id = "state"

    def hacky_fixes(self, map_data):
        map_data = re.sub(r'cy="(\d*\.\d*)" data-code="',
                          'cy="\\1" data-code="city-', map_data)
        return map_data


class StatesGenerator(MapGenerator):
    default_codes = ["CZ", "SK", "DE", "AT", "CN", "IN", "US", "CA",
                     "AU", "GB", "ES", "IT", "FR", "MX"]
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
        "MX": MexicoGenerator,
    }

    def generate_one(self, state):
        gen = self.generators[state](state)
        gen.generate_map()
