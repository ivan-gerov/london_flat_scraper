import os
import json
import urllib
import dateutil
from typing import Dict
from datetime import datetime
from configparser import ConfigParser


import requests
import geopy.distance
from bs4 import BeautifulSoup

from .models import Property, session
from .constants import API_KEYS, POIS, TOTENHAM_COURT_ROAD_COORDINATES, DATASETS
from .schemas import PropertySchema

config = ConfigParser()
config.read(API_KEYS)
API_KEYS = config["DEFAULT"]


class RightmoveScraperV2:
    def __init__(
        self,
        url: str = None,
        params: Dict[str, str] = None,
        additional_info: bool = False,
    ):
        if not url and not params:
            raise ValueError("Provide a url or params!")

        self._process_api_params(url)
        self.properties = self._scrape_properties(
            api_url="https://www.rightmove.co.uk/api/_search?",
            api_params=params or self._process_api_params(url),
        )

        if additional_info:
            self.process_additional_info()

    @staticmethod
    def store(data):
        schema = PropertySchema(many=True)
        loaded_data = schema.load(data)
        from pprint import pprint

        breakpoint()

        # breakpoint()
        # with open(f"{DATASETS}/demo_export.json", "w") as f: f.write(schema.dump(self.properties))
        # properties = schema.load(self.properties)
        # for property in properties:
        #     Property(**property).create()

    @staticmethod
    def _process_api_params(url):
        parsed_url = urllib.parse.urlsplit(url)
        initial_params = {
            "index": "0",
            "viewType": "LIST",
            "channel": "RENT" if "rent" in parsed_url.path else "BUY",
            "areaSizeUnit": "sqft",
            "currencyCode": "GBP",
            "isFetching": "false",
        }
        secondary_params = urllib.parse.parse_qs(parsed_url.query)
        return {**initial_params, **secondary_params}

    @staticmethod
    def _scrape_properties(api_url, api_params):
        start_page = json.loads(requests.get(api_url, params=api_params).text)

        with open("./datasets/example_response.json", "w") as f:
            json.dump(start_page, f)
        properties = [*start_page["properties"]]
        pages = [
            page["value"]
            for page in start_page["pagination"]["options"]
            if page["value"] != "0"
        ]
        for page in pages:
            api_params["index"] = page
            page = json.loads(requests.get(api_url, params=api_params).text)
            properties.extend(page["properties"])
        return properties

    def process_additional_info(self):
        poi_names = [os.path.splitext(poi_file)[0] for poi_file in os.listdir(POIS)]

        for property in self.properties:
            property_lat_long = tuple(property["location"].values())

            # Available Date
            property["available_date"] = self.get_available_date(property["id"])

            # Distance from POIS (Place of Interest)
            for poi in poi_names:
                property[f"closest_{poi}"] = self.get_distance_from_closest_poi(
                    property_lat_long, poi
                )

            # Minutes from Main POI by transit (work | TCR Station)
            property["minutes_from_TCR"] = self.get_distance_from_main_poi(
                property_lat_long, TOTENHAM_COURT_ROAD_COORDINATES
            )

    @staticmethod
    def get_available_date(property_id):
        property_url = (
            f"https://www.rightmove.co.uk/properties/{property_id}#/?channel=RES_LET"
        )
        soup = BeautifulSoup(requests.get(property_url).text, features="lxml")

        # Check if any in the letting details
        for h2 in soup.find_all("h2"):
            if "Letting details" in h2.text:
                for dt in h2.parent.find_all("dt"):
                    if "Let available date:" in dt.text:
                        available_date = dt.parent.findNext("dd").text
                        if available_date:
                            try:
                                if available_date == "Now":
                                    return datetime.today().strftime(
                                        "%Y-%m-%d %H:%M:%S"
                                    )
                                else:
                                    return dateutil.parser.parse(
                                        available_date
                                    ).strftime("%Y-%m-%d %H:%M:%S")
                            except dateutil.parser.ParserError:
                                pass
                    break
                break

        # Check the property description itself for the date
        for h2 in soup.find_all("h2"):
            if "Property description" in h2.text:
                property_description = h2.parent.findNext("div").text
                property_description = property_description.replace("\xa0", "").lower()

                # Looking for something like "Available date/ Date available: 19 September 2022"
                available_pos = property_description.find("available")

                # If there is a date it should be in the next 50 characters
                text_with_date = property_description[
                    available_pos : available_pos + 50
                ]
                try:
                    available_date = dateutil.parser.parse(
                        text_with_date, fuzzy=True
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    return available_date
                except dateutil.parser.ParserError:
                    return None

    @staticmethod
    def get_distance_from_closest_poi(property_lat_lon, point_of_interest):
        with open(os.path.join(POIS, f"{point_of_interest}.json")) as f:
            poi_data = json.load(f)

        closest_distance = None
        for poi_place in poi_data:
            try:
                poi_place_coordinates = poi_place["geocodes"]["main"]
            except KeyError:
                continue

            distance = geopy.distance.geodesic(
                property_lat_lon, tuple(poi_place_coordinates.values())
            ).km
            if closest_distance and distance < closest_distance:
                closest_distance = distance
            elif not closest_distance:
                closest_distance = distance
            else:
                pass

        return round(closest_distance, 2)

    @staticmethod
    def get_distance_from_main_poi(
        property_lat_lon, main_poi_coordinates=TOTENHAM_COURT_ROAD_COORDINATES
    ):
        url = "https://api.external.citymapper.com/api/1/traveltimes"
        headers = {
            "Accept": "application/json",
            "Citymapper-Partner-Key": API_KEYS["CITI_MAPPER"],
        }
        params = {
            "start": f"{property_lat_lon[0]},{property_lat_lon[1]}",
            "end": main_poi_coordinates,
            "traveltime_types": "transit",
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return None

        data = json.loads(response.text)
        return int(data["transit_time_minutes"])
