import json
import requests


def extract_aldi_locations_london():
    url = "https://www.aldi.co.uk/api/store-finder/search?"

    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        "accept": "application/json",
    }

    params = {
        "q": "London",
        "address": "London",
        "latitude": "51.5072178",
        "longitude": "-0.1275862",
        "page": "1",
    }

    addresses = []
    initial = json.loads(requests.get(url, headers=headers, params=params).text)
    addresses.extend(initial["results"])
    for page_no in range(1, len(initial["pagination"]["pages"])):
        params["page"] = page_no
        response = json.loads(requests.get(url, headers=headers, params=params).text)
        addresses.extend(response["results"])

    with open("pois/manual/aldi_locations.json", "w") as f:
        json.dump(addresses, f)


extract_aldi_locations_london()
