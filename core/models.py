from datetime import datetime
from dateutil.parser import parse

import requests
import pandas as pd
from bs4 import BeautifulSoup
from sqlalchemy import Column, Float, Integer, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine(f"sqlite:///main.db")
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

Base = declarative_base()


class Property(Base):
    __tablename__ = "property"
    property_id = Column(Integer, primary_key=True)
    price = Column(Integer)
    bedrooms = Column(Integer)
    address = Column(String)
    url = Column(String)
    lat_lon = Column(String)
    date_available = Column(DateTime)
    date_added = Column(DateTime)
    closest_aldi = Column(Float)
    closest_sainsburys = Column(Float)
    closest_tesco = Column(Float)
    closest_superdrug = Column(Float)
    closest_asda = Column(Float)
    closest_lidl = Column(Float)
    closest_boots = Column(Float)
    minutes_from_TCR = Column(Integer)

    def __init__(
        self,
        property_id,
        price,
        bedrooms,
        address,
        url,
        lat_lon=None,
        date_available=None,
        date_added=None,
        closest_aldi=None,
        closest_sainsburys=None,
        closest_tesco=None,
        closest_superdrug=None,
        closest_asda=None,
        closest_lidl=None,
        closest_boots=None,
        minutes_from_TCR=None,
        **kwargs,
    ):
        self.property_id = property_id
        self.price = price
        self.bedrooms = bedrooms
        self.address = address
        self.url = url
        self.lat_lon = lat_lon
        self.closest_aldi = closest_aldi
        self.closest_sainsburys = closest_sainsburys
        self.closest_tesco = closest_tesco
        self.closest_superdrug = closest_superdrug
        self.closest_asda = closest_asda
        self.closest_lidl = closest_lidl
        self.closest_boots = closest_boots
        self.minutes_from_TCR = minutes_from_TCR
        self.date_available = date_available
        self.date_added = date_added

    def create(self):
        properties = (
            session.query(self.__class__)
            .filter(Property.property_id == self.property_id)
            .all()
        )
        if properties:
            return
        else:
            session.add(self)
            session.commit()

    def remove(self):
        print(self.url)
        session.delete(self)
        session.commit()

    @classmethod
    def remove_obsolete(cls):
        properties = session.query(cls).all()
        print(f"Currently {len(properties)} properties in database.")

        date_today = datetime.today()
        for property in properties:
            # Property older than 30 days
            if (date_today - property.date_added).days > 30:
                property.remove()

            soup = BeautifulSoup(requests.get(property.url).text, features="lxml")
            # Check if property is unpublished
            if len(soup.find_all("div", class_="propertyUnpublished")):
                property.remove()

            for div in soup.find_all("div"):
                if "This property has been removed by the agent" in div.text:
                    property.remove()
                    break

            # Check if let is agreed
            for span in soup.find_all("span"):
                if "LET AGREED" in span or "UNDER OFFER" in span:
                    property.remove()
                    break

        print(f"{len(properties) - len(session.query(cls).all())} properties removed.")


Property.__table__.create(bind=engine, checkfirst=True)
