import urllib2
import json

BASE_URL = 'http://fenixapps2.fao.org/api/v1.0/'
DATASOURCE = 'faostat'
CODES_URL = 'codes/'

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

