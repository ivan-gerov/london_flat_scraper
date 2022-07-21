import json
import math

import requests


def extract_sainsburrys_locations_london():
    limit_per_page = 50
    url = "https://stores.sainsburys.co.uk/api/v1/stores/?"
    headers = {"content-type": "application/json"}
    params = {
        "fields": "slfe-list-2.21",
        "api_client_id": "slfe",
        "lat": "51.50732",
        "lon": "-0.12764746",
        "limit": f"{limit_per_page}",
        "store_type": "main,local",
        "sort": "by_distance",
        "within": "15",
        "page": "1",
    }

    locations = []
    initial = json.loads(requests.get(url, headers=headers, params=params).text)
    locations.extend(initial["results"])
    no_of_pages = math.ceil(int(initial["page_meta"]["total"]) / limit_per_page)

    for page_no in range(1, no_of_pages):
        params["page"] = page_no
        response = json.loads(requests.get(url, headers=headers, params=params).text)
        locations.extend(response["results"])

    with open("pois/manual/sainsburrys_locations.json", "w") as f:
        json.dump(locations, f)

extract_sainsburrys_locations_london()