import urllib
import urllib2
import json
import os

BASE_URL = 'http://fenixapps2.fao.org/api/v1.0/'
DATASOURCE = 'production'
CODES_URL = 'codes/'
DATA_URL = 'data/'

def get_items(domain_code, lang='en'):
    out = []
    try:
        r = BASE_URL + lang + '/codes/items/' + domain_code
    except TypeError:
        raise TypeError('Domain code is null')
    req = urllib2.Request(r)
    response = urllib2.urlopen(req)
    json_data = response.read()
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
    response = urllib2.urlopen(req)
    json_data = response.read()
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
    response = urllib2.urlopen(req)
    json_data = response.read()
    groups = json.loads(json_data)['data']
    for group in groups:
        out.append({
            'code': group['code'],
            'label': group['label']
        })
    return out

def get_domains(groups_code, lang='en'):
    out = []
    blacklist = ['TM', 'FT', 'EA']
    url = BASE_URL + lang + '/domains/' + groups_code
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    json_data = response.read()
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
    url = BASE_URL + lang + '/data/'
    values = {
        'domain_code': domain_code,
        'List1Codes': create_countries_parameter(domain_code, lang),
        'List2Codes': element_code,
        'List3Codes': item_code,
        'List4Codes': create_years_parameter(),
        'group_by': '',
        'order_by': '',
        'operator': ''
    }
    data = urllib.urlencode(values, True)
    print data
    req = urllib2.Request(url, data)
    response = urllib2.urlopen(req)
    print response
    json_data = response.read()
    print json_data
    rows = json.loads(json_data)['data']
    for row in rows:
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
    response = urllib2.urlopen(req)
    json_data = response.read()
    countries = json.loads(json_data)['data']
    print countries
    for country in countries:
        out.append(str(country['code']))
    return out


# def get_available_years(data):
#     year_key = None
#     value_key = None
#     country_code_key = None
#     years = []
#
#     for c in data['metadata']['dsd']:
#         print c
#         if 'dimension_id' in c:
#             if 'year' in c['dimension_id'] and 'label' in c['type']:
#                 year_key = c['key']
#             if 'area' in c['dimension_id'] and 'code' in c['type']:
#                 country_code_key = c['key']
#             if 'value' in c['dimension_id'] and 'value' in c['type']:
#                 year_key = c['key']
#
#     for d in data['data']:
#         print d
#         if d[year_key] not in years:
#             years.append(d[year_key])
#
#     return years, year_key, value_key, country_code_key
#
#
# def get_data_by_year(data, year_key, country_code_key, value_key, year):
#     year = str(year)
#     data_yearly = []
#     for d in data:
#         # TODO: Get Value Key by Domain Schema
#         if d[year_key] == year and d['Value'] is not None:
#             data_yearly.append(d)
#     return data_yearly
