# -*- coding: utf-8 -*-
from kartograph import Kartograph
import re
import unicodedata
from subprocess import Popen, PIPE, STDOUT


class MapGenerator():

    def generate(self, codes):
        codes = self.default_codes if len(codes) == 0 else codes
        for code in codes:
            self.generate_one(code)

    def generate_map(self, config, name):
        K = Kartograph()
        file_name = 'map/' + name + '.svg'
        K.generate(config, outfile=file_name)
        SingleMapGenerator().codes_hacks(file_name)
        print "generated map:", file_name


class SingleMapGenerator(object):
    def get_map_name(self):
        return self.code.lower()

    def hacky_fixes(self, map_data):
        return map_data

    def codes_hacks(self, file_name):
        mapFile = open(file_name)
        map_data = mapFile.read()
        mapFile.close()

        mapFile = open(file_name, 'w')

        map_data = re.sub(r'"[A-Z]{2}"', dashrepl, map_data)
        map_data = re.sub(r'\-code="[^"]*"', slugrepl, map_data)
        map_data = self.hacky_fixes(map_data)

        map_data = re.sub(r'("[A-Z]{2})\.([A-Z0-9]{2}")', "\\1-\\2", map_data)
        map_data = re.sub(r'"[A-Z]{2}\-[A-Z0-9]{2}"', dashrepl, map_data)
        if "africa" in file_name:
            # set missing iso codes of Somaliland xs
            map_data = map_data.replace('"-99"', '"xs"')
        if "europe" in file_name:
            # set missing iso codes of Kosovo xk
            map_data = map_data.replace('"-99"', '"xk"')
            map_data = map_data.replace('r="2"', 'r="10"')
            map_data = map_data.replace('-code="San Marino"', '-code="San_Marino"')
            # Move Vienna to the west
            map_data = map_data.replace('cx="485.279892452"', 'cx="480.279892452"')
            # Move Bratislava to the east
            map_data = map_data.replace('cx="495.028537448"', 'cx="500.028537448"')
        elif "world" in file_name:
            map_data = map_data.replace('r="2"', 'r="4"')
            # set missing iso codes of Kosovo and Somaliland to xk and xs
            map_data = map_data.replace('data-code="-99" data-name="Kosovo"',
                                        'data-code="xk" data-name="Kosovo"')
            map_data = map_data.replace('data-code="-99" data-name="Somaliland"',
                                        'data-code="xs" data-name="Somaliland"')
            # TODO: set missing iso code of Northern Cyprus. But what code?
        map_data = map_data.replace('r="2"', 'r="16"')

        p = Popen(["xmllint", "--format", '-'], stdout=PIPE, stderr=STDOUT, stdin=PIPE)
        out, err = p.communicate(input=map_data)

        mapFile.write(out)
        mapFile.close()

    def generate_map(self):
        K = Kartograph()
        file_name = 'map/' + self.map_name + '.svg'
        K.generate(self.config, outfile=file_name)
        self.codes_hacks(file_name)
        print "generated map:", file_name


def slugrepl(matchobj):
    text = matchobj.group(0).replace(" ", "_").decode("utf-8")
    return unicodedata.normalize('NFD', text).encode('ascii', 'ignore')


def dashrepl(matchobj):
    return matchobj.group(0).lower()
