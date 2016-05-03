# -*- coding: utf-8 -*-
from generator import MapGenerator, SingleMapGenerator
import unicodedata

PROVINCES_BIG_FILE = "src/ne_10m_admin_1_states_provinces_lakes/ne_10m_admin_1_states_provinces_lakes.shp"
SOORP_FILE = "my_src/soorp_cr/soorp.shp"
SOOPU_FILE = "my_src/soorp_cr/sopou.shp"
MZCHU_FILE = "my_src/mzchu/mzchu_npp_npr_body3.shp"
RIVER_FILE = "my_src/reky_cr/reky_cr.shp"
CITY_FILE = "my_src/Obce_cz/Obce_body.shp"
CITY_FILE = "src/czech-republic-latest.shp/places.shp"


def slugrepl(text):
    repl = {
        'ý': 'y', 'ě': 'e', 'š': 's',
        'č': 'c', 'ř': 'r', 'ž': 'z',
        'á': 'a', 'í': 'i', 'é': 'e',
        'ů': 'u'
    }
    text = text.lower()
    for i in repl.keys():
        text = text.replace(i, repl[i])
    return text
    # return unicodedata.normalize('NFD', text).encode('ascii', 'ignore')


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii


def cz_cities_size_filter(record):
    return record['population'] > 5 * 10 ** 3


class RegionGenerator(SingleMapGenerator):
    state_id = "region"

    def __init__(self, code):
        self.code = code
        self.config = self.get_config()
        self.map_name = self.get_map_name()

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

    def get_config(self):
        config = {
            "layers": [{
                "id": "bg",
                "src": PROVINCES_BIG_FILE,
                "filter": {'iso_3166_2': self.code.upper()},
            }, {
                "id": 'soorp',
                "src": SOORP_FILE,
                "attributes": {
                    "code": 'nazev',
                    "name": 'nazev',
                },
                "simplify": 3,
                "filter": {'kraj': self.get_filter()},
            }, {
                "id": 'soopu',
                "src": SOOPU_FILE,
                "attributes": {
                    "code": 'nazev',
                    "name": 'nazev',
                },
                "simplify": 3,
                "filter": {'kraj': self.get_filter()},
            }, {
                "id": 'mzchu',
                "src": MZCHU_FILE,
                "attributes": {
                    "code": 'nazev',
                    "name": 'nazev',
                },
                "simplify": 2,
                "filter": {'kod_kraje': self.code[3:].upper()},
            }],
            "bounds": {
                "mode": "polygons",
                "data": {
                    "layer": 'bg',
                },
            }
        }
        return config

    def hacky_fixes(self, map_data):
        map_data = map_data.replace(
            '<g class="" id="bg">',
            '<g class="" id="bg">' +
            '<path d="M-10000.0,-10000.0L-10000.0,10000.0L10000.0,10000.0L10000.0,-10000.0Z "/>')
        return map_data

    def get_filter(self):
        return RegionsGenerator.names_dict[self.code]


class RegionsGenerator(MapGenerator):
    names_dict = {
        "cz-us": "Ústecký kraj",
        "cz-pl": "Plzeňský kraj",
        "cz-jm": "Jihomoravský kraj",
        "cz-zl": "Zlínský kraj",
        "cz-ol": "Olomoucký kraj",
        "cz-pa": "Pardubický kraj",
        "cz-ka": "Karlovarský kraj",
        "cz-jc": "Jihočeský kraj",
        "cz-vy": "Kraj Vysočina",
        "cz-st": "Středočeský kraj",
        "cz-li": "Liberecký kraj",
        "cz-kr": "Královéhradecký kraj",
        "cz-mo": "Moravskoslezský kraj",
        # "cz-pr": "Hlavní město Praha",
    }
    names_slugs = dict([
        (i, slugrepl(n.replace(' ', '')).replace('kraj', '')) for i, n in names_dict.iteritems()])
    default_codes = names_dict.keys()

    def generate_one(self, state):
        gen = RegionGenerator(state)
        gen.generate_map()
