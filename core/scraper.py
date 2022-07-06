import os
import json
from configparser import ConfigParser
from datetime import datetime
from dateutil.parser import parse, ParserError

import requests
import pandas as pd
import geopy.distance
from rightmove_webscraper import RightmoveData
from bs4 import BeautifulSoup

from .models import Flat
from .constants import API_KEYS, POIS, TOTENHAM_COURT_ROAD_COORDINATES

OR = "%2C"
URL = "https://www.rightmove.co.uk/property-to-rent/find.html?"

PARAMS = {
    "locationIdentifier": "STATION%5E245",
    "minBedrooms": 1,
    "maxPrice": 1750,
    "radius": 5.0,
    "maxDaysSinceAdded": 1,
    "includeLetAgreed": "false",
    "dontShow": OR.join(["houseShare", "retirement", "student"]),
}

config = ConfigParser()
config.read(API_KEYS)
API_KEYS = config["DEFAULT"]


class RightmoveScraperV2(RightmoveData):
    def __init__(
        self,
        url: str,
        params: str = None,
        get_floorplans: bool = False,
        additional_info: bool = False,
    ):
        if params:
            params = self.process_params(params)
            url = f"{url}{'&'.join(params)}"

        super().__init__(url, get_floorplans)

        if additional_info:
            self.process_additional_info()

    def process_params(self, params):
        processed_params = []
        for param_name, param_value in params.items():
            if isinstance(param_value, (list, tuple)):
                param_value = OR.join(param_value)
            processed_params.append(f"{param_name}={param_value}")
        return processed_params

    def process_additional_info(self):
        # Available Date
        self._results["available_date"] = self._results.apply(
            self.get_available_date, axis=1
        )

        # Lat Lon
        self._results["lat_lon"] = self._results.apply(self.get_lat_lon, axis=1)

        # Distance from POIS
        poi_names = [os.path.splitext(poi_file)[0] for poi_file in os.listdir(POIS)]
        for poi in poi_names:
            self._results[f"closest_{poi}"] = self._results.apply(
                lambda flat_data: self.get_distance_from_closest_poi(flat_data, poi),
                axis=1,
            )

        # Minutes from Main POI by transit (work | TCR Station)
        self._results["minutes_from_TCR"] = self._results.apply(
            self.get_distance_from_main_poi, axis=1
        )

    def save_results(self, fp: str):
        self._results.to_csv(fp)

    def save_to_db(self):
        def foo(data):
            try:
                Flat(**data.to_dict()).create()
            except Exception as e:
                breakpoint()
                pass

        self._results.apply(foo, axis=1)

    @staticmethod
    def get_available_date(data):
        soup = BeautifulSoup(requests.get(data["url"]).text, features="lxml")

        # Check if any in the letting details
        for h2 in soup.find_all("h2"):
            if "Letting details" in h2.text:
                for dt in h2.parent.find_all("dt"):
                    if "Let available date:" in dt.text:
                        available_date = dt.parent.findNext("dd").text
                        if available_date:
                            try:
                                if available_date == "Now":
                                    return datetime.today()
                                else:
                                    return parse(available_date)
                            except ParserError:
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
                    available_date = parse(text_with_date, fuzzy=True)
                    return available_date
                except ParserError:
                    return None

    @staticmethod
    def get_lat_lon(data):

        url = "https://api.geoapify.com/v1/geocode/search?"
        params = {
            "apiKey": API_KEYS["GEOAPIFY"],
            "text": data["address"],
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

    @staticmethod
    def get_distance_from_closest_poi(flat_data, point_of_interest):
        if pd.isna(flat_data["lat_lon"]):
            return

        coordinates = [float(c) for c in flat_data["lat_lon"].split(",")]

        with open(os.path.join(POIS, f"{point_of_interest}.json")) as f:
            poi_data = json.load(f)

        closest_distance = None
        for poi_place in poi_data:
            try:
                poi_place_coordinates = poi_place["geocodes"]["main"]
            except KeyError:
                continue

            distance = geopy.distance.geodesic(
                coordinates, tuple(poi_place_coordinates.values())
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
        flat_data, main_poi_coordinates=TOTENHAM_COURT_ROAD_COORDINATES
    ):
        if pd.isna(flat_data["lat_lon"]):
            return

        url = "https://api.external.citymapper.com/api/1/traveltimes"
        headers = {
            "Accept": "application/json",
            "Citymapper-Partner-Key": API_KEYS["CITI_MAPPER"],
        }
        params = {
            "start": flat_data["lat_lon"],
            "end": main_poi_coordinates,
            "traveltime_types": "transit",
        }

        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return

        data = json.loads(response.text)
        return int(data["transit_time_minutes"])
