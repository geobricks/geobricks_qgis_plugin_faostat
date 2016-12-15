import urllib
import urllib2
import json
from qgis.core import QgsMessageLog

BASE_URL    = 'http://fenixservices.fao.org/faostat/api/v1/'
CODES_URL   = 'codes/'
DATA_URL    = 'data/'


def get_items(domain_code, lang='en'):
    out = []
    try:
        r = BASE_URL + lang + '/codes/items/' + domain_code
    except TypeError:
        raise TypeError('Domain code is null')
    req = urllib2.Request(r)
    fp = urllib2.urlopen(req)
    response = ''
    while 1:
        data = fp.read()
        if not data:
            break
        response += data
    json_data = response
    items = json.loads(json_data)['data']
    for item in items:
        out.append({
            'code': item['code'],
            'label': item['label']
        })
    return out


def get_elements(domain_code, lang='en'):
    out = []
    try:
        r = BASE_URL + lang + '/codes/elements/' + domain_code
    except TypeError:
        raise TypeError('Domain code is null')
    req = urllib2.Request(r)
    fp = urllib2.urlopen(req)
    response = ''
    while 1:
        data = fp.read()
        if not data:
            break
        response += data
    json_data = response
    try:
        elements = json.loads(json_data)['data']
        for element in elements:
            out.append({
                'code': element['code'],
                'label': element['label']
            })
        return out
    except ValueError:
        raise ValueError('No elements available for this domain.')


def get_groups(lang='en'):
    out = []
    url = BASE_URL + lang + '/groups/'
    req = urllib2.Request(url)
    fp = urllib2.urlopen(req)
    response = ''
    while 1:
        data = fp.read()
        if not data:
            break
        response += data
    json_data = response
    groups = json.loads(json_data)['data']
    for group in groups:
        out.append({
            'code': group['code'],
            'label': group['label']
        })
    return out


def get_domains(groups_code, lang='en'):
    out = []
    blacklist = ['TM', 'FT', 'EA', 'HS']
    url = BASE_URL + lang + '/domains/' + groups_code
    req = urllib2.Request(url)
    fp = urllib2.urlopen(req)
    response = ''
    while 1:
        data = fp.read()
        if not data:
            break
        response += data
    json_data = response
    domains = json.loads(json_data)['data']
    for domain in domains:
        if str(domain['code']) not in blacklist:
            out.append({
                'code': domain['code'],
                'label': domain['label']
            })
    return out


def get_data(domain_code, element_code, item_code, lang='en'):
    out = []
    url = BASE_URL + lang + '/data/' + domain_code + '?'
    values = {
        'area': '_1',
        'area_cs': 'FAO',
        'element': element_code,
        'item': item_code,
        'year': '_1',
        'show_code': True,
        'show_unit': True,
        'show_flags': False,
        'null_values': False,
        'limit': -1,
        'output_type': 'objects'
    }
    data = urllib.urlencode(values, True)
    data_url = str(url) + str(data)
    fp = urllib2.urlopen(data_url)
    response = ''
    while 1:
        data = fp.read()
        if not data:
            break
        response += data
    json_data = response
    rows = json.loads(json_data)['data']
    for row in rows:
        if 'Value' in row and 'Area Code' in row:
            out.append({
                'code': row['Area Code'],
                'value': row['Value'],
                'year': row['Year']
            })
        if 'Value' in row and 'Country Code' in row:
            out.append({
                'code': row['Country Code'],
                'value': row['Value'],
                'year': row['Year']
            })
    return out


def create_years_parameter():
    years = []
    for y in range(1961, 2015):
        years.append(str(y))
    return years


def create_countries_parameter(domain_code, lang='en'):
    out = []
    r = BASE_URL + lang + '/codes/countries/' + domain_code
    req = urllib2.Request(r)
    fp = urllib2.urlopen(req)
    response = ''
    while 1:
        data = fp.read()
        if not data:
            break
        response += data
    json_data = response
    countries = json.loads(json_data)['data']
    for country in countries:
        out.append(str(country['code']))
    return out
