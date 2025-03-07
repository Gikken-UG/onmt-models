#!/usr/bin/env python3

# https://github.com/tatuylonen/wiktextract

import os
import json
import argparse
from pathlib import Path

# Configure
sl = os.environ['sl']
tl = os.environ['tl']

parser = argparse.ArgumentParser()
parser.add_argument('wikidata', help=
        'path to JSON file from wiktextract for source lang')
parser.add_argument('wikidata2', help=
        'path to JSON file from wiktextract for source lang')
args = parser.parse_args()

# Read JSON
wikidata = []
with open(args.wikidata) as f:
    for line in f:
        wikidata.append(json.loads(line))
with open(args.wikidata2) as f:
    for line in f:
        wikidata.append(json.loads(line))
print('Read JSON into memory')

# Helper methods
def get_forms(data):
    """Takes a JSON data object and returns a list of its forms"""
    to_return = []
    forms = data.get('forms')
    if forms:
        for form in forms:
            form_value = form.get('form')
            if form_value != None:
                to_return.append(form_value)
    word = data.get('word')
    if word:
        to_return.append(word)
    return to_return

# Extract single word translation data
source_data = []
target_data = []
for data in wikidata:
    if data.get('lang_code') != sl:
        print('Skipping data not in source lang: ' +
                str(data.get('lang_code')))
        continue
    senses = data.get('senses')
    if not senses:
        # Data doesn't have translations
        continue
    translations = []
    for sense in senses:
        translation = sense.get('translations')
        if translation:
            translations += translation
    forms = get_forms(data)
    for translation in translations:
        if translation.get('code') == tl:
            translation_value = translation.get('word')
            if translation_value == None:
                continue
            for form in forms:
                source_data.append(form)
                target_data.append(translation_value)

# Special token <define>
DEFINE_TOKEN = '<define>'
for data in wikidata:
    if data.get('lang_code') not in [sl, tl]:
        print('Skipping data not in source lang: ' +
                str(data.get('lang_code')))
        continue
    senses = data.get('senses')
    if not senses:
        # Data doesn't have translations
        continue
    definitions = []
    forms = get_forms(data)
    for sense in senses:
        glosses = sense.get('glosses')
        if not glosses:
            continue
        for gloss in glosses:
            for form in forms:
                source_data.append(DEFINE_TOKEN + ' ' + form)
                target_data.append(gloss)

# Write to file
for filename, data in [
        ('raw_data/wiktionary.' + sl, source_data),
        ('raw_data/wiktionary.' + tl, target_data)]:
    filename = Path(filename)
    assert(not filename.exists())
    data_file = open(filename, 'w')
    data_file.write('\n'.join(data))
    data_file.close()
print('Wrote to raw_data/wiktionary.*')

