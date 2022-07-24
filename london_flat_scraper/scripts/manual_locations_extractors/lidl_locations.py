from email import header
import json

import requests

url = "https://www.toptiplondon.com/wp-json/wpgmza/v1/features/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMrKMUdIBiRRnlBZ4uhQDBaNjgQLJpcUl+blumak5KRCxWqVaABd4FvQ"
headers = {"content-type": "application/json"}

response = json.loads(requests.get(url, headers=headers).text)
locations = response["markers"]

processed_locations = []
for location in locations:
    processed_locations.append(
        {
            "address": location["address"],
            "location": {"lat": location["lat"], "lon": location["lng"]},
        }
    )
with open("pois/manual/lidl_locations.json", "w") as f:
    json.dump(processed_locations, f)
