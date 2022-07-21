import json
from configparser import ConfigParser

import requests

config = ConfigParser()
config.read("API_KEYS.ini")
API_KEYS = config["DEFAULT"]


def get_lat_lon(address):

    url = "https://api.geoapify.com/v1/geocode/search?"
    params = {
        "apiKey": API_KEYS["GEOAPIFY"],
        "text": address,
        "city": "London",
        "filter": "rect:-1.415368,51.103847,0.950812,51.820821",
    }
    headers = {"Accept": "application/json"}
    response = json.loads(requests.get(url, headers=headers, params=params).text)
    try:
        address_info = response["features"][0]["properties"]
        return f'{address_info["lat"]},{address_info["lon"]}'
    except IndexError:
        return None

def geocode_tesco_locations():
    with open("datasets/tesco_locations.json") as f:
        data = json.load(f)
    
    geopoints = []
    for location in data:
        lat_lon = get_lat_lon(location)
        if lat_lon:
            geopoints.append(lat_lon)
    
    with open("pois/manual/tesco_locations.json", "w") as f:
        json.dump(geopoints, f)

def geocode_asda_locations():
    with open("datasets/asda_locations.json") as f:
        data = json.load(f)
    
    geopoints = []
    for location in data:
        lat_lon = get_lat_lon(location)
        if lat_lon:
            geopoints.append(lat_lon)
    
    with open("pois/manual/asda_locations.json", "w") as f:
        json.dump(geopoints, f)

geocode_asda_locations()