import json
from configparser import ConfigParser

import requests

from .constants import API_KEYS, POIS

config = ConfigParser()
config.read(API_KEYS)
API_KEY = config["DEFAULT"]["FOURSPACE"]
MILES_6_METERS = 9660


def get_pois_around_angel(
    poi_name: str, radius_meters: int = MILES_6_METERS, API_KEY: str = API_KEY
):
    ANGEL = "51.5327841,-0.1058706"

    url = f"https://api.foursquare.com/v3/places/search"
    params = {"query": poi_name, "ll": ANGEL, "radius": radius_meters}
    headers = {"Accept": "application/json", "Authorization": API_KEY}
    response = json.loads(requests.get(url, params=params, headers=headers).text)
    locations = response["results"]
    with open(f"{POIS}/{poi_name}.json", "w") as f:
        json.dump(locations, f)


def fourspace_poi_finder():
    POIS = ["sainsburys", "lidl", "aldi", "asda", "tesco", "boots", "superdrug"]

    for poi in POIS:
        get_pois_around_angel(poi)
