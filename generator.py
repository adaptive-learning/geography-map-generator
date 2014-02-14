from kartograph import Kartograph
import re


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

    def dashrepl(matchobj):
        return matchobj.group(0).lower()
    map_data = re.sub(r'"[A-Z]{2}"', dashrepl, map_data)
    if "/de.svg" in file_name:
        map_data = re.sub(r'"DE."', '"DE.BR"', map_data)
    map_data = re.sub(r'("[A-Z]{2})\.([A-Z0-9]{2}")', "\\1-\\2", map_data)
    map_data = re.sub(r'"[A-Z]{2}\-[A-Z0-9]{2}"', dashrepl, map_data)
    if "europe" in file_name:
        # set missing iso codes of Kosovo xk
        map_data = re.sub(r'"-99"', '"xk"', map_data)
        map_data = re.sub(r'r="2"', 'r="10"', map_data)
    elif "world" in file_name:
        map_data = re.sub(r'r="2"', 'r="4"', map_data)
        # set missing iso codes of Kosovo and Somaliland to xk and xs
        map_data = map_data.replace('data-name="-99" data-realname="Kosovo"',
                                    'data-name="xk" data-realname="Kosovo"')
        map_data = map_data.replace('data-name="-99" data-realname="Somaliland"',
                                    'data-name="xs" data-realname="Somaliland"')
        # TODO: set missing iso code of Northern Cyprus. But what code?
    elif "/it.svg" in file_name:
        map_data = re.sub(r'r="2"', 'r="16"', map_data)
    else:
        map_data = re.sub(r'r="2"', 'r="8"', map_data)
    mapFile.write(map_data)
    mapFile.close()
