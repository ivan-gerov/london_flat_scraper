import os
import re
from dateutil import parser
from datetime import datetime, timedelta

from marshmallow import Schema, fields, pre_load, EXCLUDE

from london_flat_scraper.constants import POIS

pois = [os.path.splitext(poi_file)[0] for poi_file in os.listdir(POIS)]
poi_fields = {f"closest_{poi}": fields.Float() for poi in pois}
PoiFields = type("PoiFields", (object,), poi_fields)


class PropertySchema(Schema, PoiFields):
    class Meta:
        unknown = EXCLUDE

    property_id = fields.Integer(data_key="id")
    date_added = fields.Date(format="%Y-%m-%d")
    date_available = fields.Date(
        data_key="available_date", format="%Y-%m-%d %H:%M:%S", allow_none=True
    )
    price = fields.Integer()
    bedrooms = fields.Integer()
    address = fields.String(data_key="displayAddress")
    lat_lon = fields.String()
    images = fields.List(fields.String())
    url = fields.Url()
    channel = fields.String()
    minutes_from_TCR = fields.Integer()
    crime_rates = fields.Integer()

    @pre_load
    def process_price(self, data, **kwargs):
        if data["price"] == "monthly":
            data["price"] = int(data["price"]["amount"].replace(",", ""))
        else:
            pcm = [
                el["displayPrice"]
                for el in data["price"]["displayPrices"]
                if "pcm" in el["displayPrice"]
            ][0]

            pcm = pcm.replace(",", "").replace(".", "")
            try:
                data["price"] = int(re.findall(r"\d+", pcm)[0])
            except Exception as e:
                breakpoint()
        return data

    @pre_load
    def process_images(self, data, **kwargs):
        propertyImages = data["propertyImages"].copy()
        if propertyImages.get("images"):
            propertyImages = propertyImages["images"]
            data["images"] = []
            for image in propertyImages:
                data["images"].append(image["srcUrl"])
        return data

    @pre_load
    def process_location(self, data, **kwargs):
        location = data["location"]
        data["lat_lon"] = f"{location['latitude']},{location['longitude']}"
        return data

    @pre_load
    def process_url(self, data, **kwargs):
        data[
            "url"
        ] = f"https://www.rightmove.co.uk/properties/{data['id']}#/?channel=RES_LET"
        return data

    @pre_load
    def process_date_added(self, data, **kwargs):
        date_added = data["addedOrReduced"]
        if "today" in date_added:
            data["date_added"] = datetime.today().date()
        elif "yesterday" in date_added:
            data["date_added"] = (datetime.today() - timedelta(days=1)).date()
        else:
            data["date_added"] = parser.parse(date_added, fuzzy=True).date()
        data["date_added"] = data["date_added"].strftime("%Y-%m-%d")
        return data
