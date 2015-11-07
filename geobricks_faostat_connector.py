import urllib
import urllib2
import json
import os

BASE_URL = 'http://fenixapps2.fao.org/api/v1.0/'
DATASOURCE = 'production'
CODES_URL = 'codes/'
DATA_URL = 'data/'

def get_items(domain_code, lang='en'):
    r = BASE_URL + lang + "/" + CODES_URL + 'item/' + domain_code + '/?datasource=production&output_type=objects&api_key=n.a.&client_key=n.a.&domains=QC&group_subdimensions=false&subcodelists=&show_lists=&show_full_metadata=&ord='
    print r
    req = urllib2.Request(r)
    response = urllib2.urlopen(req)
    json_data = response.read()
    return json.loads(json_data)['data']


def get_elements(domain_code, lang='en'):
    r = BASE_URL + lang + "/" + CODES_URL + 'element/' + domain_code + '/?datasource=production&output_type=objects&api_key=n.a.&client_key=n.a.&domains=QC&group_subdimensions=false&subcodelists=&show_lists=&show_full_metadata=&ord='
    print r
    req = urllib2.Request(r)
    response = urllib2.urlopen(req)
    json_data = response.read()
    return json.loads(json_data)['data']

def get_domains(lang='en'):
    out = []
    url = BASE_URL + lang + '/groupsanddomains/'
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    json_data = response.read()
    domains = json.loads(json_data)['data']
    print domains
    for domain in domains:
        out.append({
            'code': domain['DomainCode'],
            'label': domain['label'] + ': ' + domain['DomainNameE']
        })
    return out

def get_data(domain_code, elements, items, lang='en'):
    # TODO implement getData call
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "qc.json")) as data:
        return json.load(data)


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
