import json

import requests


LONDON_BOUNDARIES = {
    "boundEastLongitude": 0.2471,
    "boundNorthLatitude": 51.820821,
    "boundSouthLatitude": 51.103847,
    "boundWestLongitude": -0.5740,
}


def extract_superdrug_locations_london():
    url = "https://api.superdrug.com/api/v2/sd/stores?"
    headers = {
        "content-type": "application/json",
        "origin": "https://www.superdrug.com",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    }
    params = {
        "country": "GB",
        "fields": "FULL",
        "currentPage": "0",
        "pageSize": "100",
        "lang": "en_GB",
        "curr": "GBP",
    }

    locations = []
    initial = json.loads(requests.get(url, headers=headers, params=params).text)

    no_pages = initial["pagination"]["totalPages"]

    for page_no in range(no_pages):
        params["currentPage"] = page_no
        response = json.loads(requests.get(url, headers=headers, params=params).text)
        for store in response["stores"]:
            if bound_to_london(store["geoPoint"]):
                locations.append(store)

    with open("pois/manual/superdrug_locations.json", "w") as f:
        json.dump(locations, f)


def bound_to_london(store_lat_lon):
    if (
        not LONDON_BOUNDARIES["boundWestLongitude"]
        <= store_lat_lon["longitude"]
        <= LONDON_BOUNDARIES["boundEastLongitude"]
    ):
        return False

    if (
        not LONDON_BOUNDARIES["boundSouthLatitude"]
        <= store_lat_lon["latitude"]
        <= LONDON_BOUNDARIES["boundNorthLatitude"]
    ):
        return False

    return True


extract_superdrug_locations_london()
