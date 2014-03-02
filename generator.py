# -*- coding: utf-8 -*-
from kartograph import Kartograph
import re
import unicodedata


class MapGenerator():

    def generate(self, codes):
        codes = self.default_codes if len(codes) == 0 else codes
        for code in codes:
            self.generate_one(code)

    def generate_map(self, config, name):
        K = Kartograph()
        file_name = 'map/' + name + '.svg'
        K.generate(config, outfile=file_name)
        codes_hacks(file_name)
        print "generated map:", file_name


def codes_hacks(file_name):
    mapFile = open(file_name)
    map_data = mapFile.read()
    mapFile.close()

    mapFile = open(file_name, 'w')

    map_data = re.sub(r'"[A-Z]{2}"', dashrepl, map_data)
    map_data = re.sub(r'\-name="[^"]*"', slugrepl, map_data)
    map_data = state_related_fix(map_data, file_name)

    map_data = re.sub(r'("[A-Z]{2})\.([A-Z0-9]{2}")', "\\1-\\2", map_data)
    map_data = re.sub(r'"[A-Z]{2}\-[A-Z0-9]{2}"', dashrepl, map_data)
    if "europe" in file_name:
        # set missing iso codes of Kosovo xk
        map_data = map_data.replace('"-99"', '"xk"')
        map_data = map_data.replace('r="2"', 'r="10"')
        map_data = map_data.replace('-name="San Marino"', '-name="San_Marino"')
        # Move Vienna to the west
        map_data = map_data.replace('cx="485.279892452"', 'cx="480.279892452"')
        # Move Bratislava to the east
        map_data = map_data.replace('cx="495.028537448"', 'cx="500.028537448"')
    elif "namerica" in file_name:
        map_data = map_data.replace('r="2"', 'r="8"')
    elif "world" in file_name:
        map_data = map_data.replace('r="2"', 'r="4"')
        # set missing iso codes of Kosovo and Somaliland to xk and xs
        map_data = map_data.replace('data-name="-99" data-realname="Kosovo"',
                                    'data-name="xk" data-realname="Kosovo"')
        map_data = map_data.replace('data-name="-99" data-realname="Somaliland"',
                                    'data-name="xs" data-realname="Somaliland"')
        # TODO: set missing iso code of Northern Cyprus. But what code?
    mapFile.write(map_data)
    mapFile.close()


def slugrepl(matchobj):
    text = matchobj.group(0).replace(" ", "_").decode("utf-8")
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore')


def dashrepl(matchobj):
    return matchobj.group(0).lower()


def state_related_fix(map_data, file_name):
    if "/it.svg" in file_name:
        map_data = fix_italy(map_data)
    elif "/fr.svg" in file_name:
        map_data = fix_france(map_data)
    elif "/cn.svg" in file_name:
        map_data = map_data.replace('"CN-"', '"CN-35"')
    elif "/de.svg" in file_name:
        map_data = map_data.replace('"DE."', '"DE.BB"')
    elif "/us.svg" in file_name:
        map_data = map_data.replace(',559', ',564')
        map_data = map_data.replace('r="2"', 'r="8"')
    elif "/in.svg" in file_name:
        map_data = map_data.replace('data-name="IN." data-realname="Gujarat"',
                                    'data-name="IN.GJ" data-realname="Gujarat"')
        map_data = map_data.replace('data-name="IN." data-realname="Tamil Nadu"',
                                    'data-name="IN.TN" data-realname="Tamil Nadu"')
    elif "/cz.svg" in file_name:
        map_data = map_data.replace(
            "M0.000000,0.000000L0.000000,567.267337" +
            "L1000.000000,567.267337L1000.000000,0.000000L0.000000,0.000000Z",
            "M-5000.0,-5000.0L-5000.0,5000.0L5000.0,5000.0L5000.0,-5000.0L-5000.0,-5000.0Z")
    return map_data


def fix_italy(map_data):
    CODES = {
        u'Abruzzo': u'IT-65',
        u'Apulia': u'IT-75',
        u'Basilicata': u'IT-77',
        u'Calabria': u'IT-78',
        u'Campania': u'IT-72',
        u'Emilia-Romagna': u'IT-45',
        u'Friuli-Venezia Giulia': u'IT-36',
        u'Lazio': u'IT-62',
        u'Liguria': u'IT-42',
        u'Lombardia': u'IT-25',
        u'Marche': u'IT-57',
        u'Molise': u'IT-67',
        u'Piemonte': u'IT-21',
        u'Sardegna': u'IT-88',
        u'Sicily': u'IT-82',
        u'Toscana': u'IT-52',
        u'Trentino-Alto Adige': u'IT-32',
        u'Umbria': u'IT-55',
        u'Valle d\'Aosta': u'IT-23',
        u'Veneto': u'IT-34',
    }
    pattern = re.compile('-name="(' + '|'.join(CODES.keys()) + ')"')
    map_data = pattern.sub(lambda x: u'-name="' + CODES[x.group(1)] + u'"', map_data)
    return map_data


def fix_france(map_data):
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
        u'Franche-Comté': u'FR-I',
        u'Haute-Normandie': u'FR-Q',
        u'Île-de-France': u'FR-J',
        u'Languedoc-Roussillon': u'FR-K',
        u'Limousin': u'FR-L',
        u'Lorraine': u'FR-M',
        u'Midi-Pyrénées': u'FR-N',
        u'Nord-Pas-de-Calais': u'FR-O',
        u'Pays de la Loire': u'FR-R',
        u'Picardie': u'FR-S',
        u'Poitou-Charentes': u'FR-T',
        u'Provence-Alpes-Côte-d\'Azur': u'FR-U',
        u'Rhône-Alpes': u'FR-V',
    }
    pattern = re.compile(u'-name="(' + u'|'.join(CODES.keys()) + u')"')
    map_data = map_data.decode("utf-8")
    map_data = pattern.sub(lambda x: u'-name="' + CODES[x.group(1)] + u'"', map_data)
    map_data = re.sub(r'"[A-Z]{2}\-[A-Z]"', dashrepl, map_data)
    map_data = map_data.encode("utf-8")
    return map_data
