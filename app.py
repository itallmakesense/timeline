import requests
from sanic import Sanic
from sanic.response import json


APP = Sanic()

IP_API = "http://ip-api.com/json"
WHO_API = "http://apps.who.int/gho/athena/api"
LIFETIME_ENDPOINT = "GHO/WHOSIS_000001.json"
'http://apps.who.int/gho/athena/api/?filter=COUNTRY:BLR'


def _get_geo_data(request):
    ip_api = requests.get(f"{IP_API}/{request.remote_addr}")
    geo_data = ip_api.json()
    if geo_data['status'] == 'fail':
        geo_data = None
    return geo_data


def _get_coutry_code(geo_data):
    if geo_data:
        who_api = requests.get(f"{WHO_API}/COUNTRY?format=json")
        country_data = who_api.json()
        countries = country_data['dimension'][0]
        codes = [code['attr'] for code in countries['code']
                 if code['display'] == geo_data['country']][0]
        return [code['value'] for code in codes if code['category'] == 'WHO'][0]


def _prettify_facts(lifetime_expectancy_facts):
    pretty_facts = {}
    for fact in lifetime_expectancy_facts:
        publish_year = [dim['code']
                        for dim in fact['Dim'] if dim['category'] == 'YEAR'][0]
        sex = [dim['code']
               for dim in fact['Dim'] if dim['category'] == 'SEX'][0]
        pretty_facts.setdefault(
            publish_year, {}).update(
                {sex: fact['value']['numeric']})
    return pretty_facts


def _get_lifetime_expectancy(country_code):
    if country_code:
        who_api = requests.get(
            f"{WHO_API}/{LIFETIME_ENDPOINT}?filter=COUNTRY:{country_code}")
        life_exp = who_api.json()
        pretty_facts = _prettify_facts(life_exp['fact'])
        last_fact_year = str(max(int(year) for year in pretty_facts.keys()))
        return pretty_facts[last_fact_year]


@APP.route('/')
async def root(request):
    geo_data = _get_geo_data(request)
    country_code = _get_coutry_code(geo_data)
    life_exp = _get_lifetime_expectancy(country_code)
    return json({'who': life_exp})


if __name__ == '__main__':
    APP.run()
