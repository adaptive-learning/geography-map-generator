#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import urllib2
import os
import csv


def main():
    with open('places.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        count = 0
        for row in reader:
            name = row[0]
            term_json = load_term(name)
            if not term_json or not term_json['name']:
                name += '_(river)'
                term_json = load_term(name)
            if term_json and term_json['name']:
                print '    ###############  ', name
                print term_json
                count += 1
        print 'Total count:', count


def load_term(name):
    term_json = load_dbpedia_page(name)
    term_key = 'http://dbpedia.org/resource/%s' % name
    if term_key not in term_json:
        return

    props = [
        'http://xmlns.com/foaf/0.1/name',
        'http://dbpedia.org/property/mouth',
        'http://dbpedia.org/property/origin',
        'http://dbpedia.org/ontology/mouth',
        'http://dbpedia.org/ontology/origin',
        'http://dbpedia.org/ontology/source',
        'http://dbpedia.org/property/city',
    ]
    term = {}
    for prop in props:
        key = prop.split('/')[-1]
        term[key] = term.get(key, term_json[term_key].get(prop, [{}])[0].get('value'))
    return term


def cache_page(fn):
    directory = '.cache'
    if not os.path.exists(directory):
        os.makedirs(directory)

    def func_wrapper(name):
        file_name = directory + '/' + name + '.json'
        if os.path.isfile(file_name):
            with open(file_name) as data_file:
                data = json.load(data_file)
        else:
            data = fn(name)
            with open(file_name, 'w') as outfile:
                json.dump(data, outfile)
        return data
    return func_wrapper


@cache_page
def load_dbpedia_page(name):
    url = 'http://dbpedia.org/data/%s.json' % name
    term_json = json.load(urllib2.urlopen(url))
    return term_json


if __name__ == '__main__':
    main()
