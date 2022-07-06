from dateutil.parser import parse

import pandas as pd
from sqlalchemy import Column, Float, Integer, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Flat(Base):
    __tablename__ = "flat"
    flat_id = Column(Integer, primary_key=True)
    price = Column(Integer)
    flat_type = Column(String)
    address = Column(String)
    url = Column(String)
    postcode = Column(String)
    full_postcode = Column(String)
    available_date = Column(DateTime)
    lat_lon = Column(String)
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
        price,
        type,
        address,
        url,
        postcode,
        full_postcode=None,
        available_date=None,
        lat_lon=None,
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
        self.price = price
        self.flat_type = type
        self.address = address
        self.url = url
        self.postcode = postcode
        self.full_postcode = full_postcode
        self.available_date = (
            parse(available_date) if not pd.isna(available_date) else None
        )
        self.lat_lon = lat_lon
        self.closest_aldi = closest_aldi
        self.closest_sainsburys = closest_sainsburys
        self.closest_tesco = closest_tesco
        self.closest_superdrug = closest_superdrug
        self.closest_asda = closest_asda
        self.closest_lidl = closest_lidl
        self.closest_boots = closest_boots
        self.minutes_from_TCR = minutes_from_TCR

    def create(self):
        flats = session.query(self.__class__).filter(Flat.address == self.address).all()
        if flats:
            return
        else:
            session.add(self)
            session.commit()

    def remove(self):
        session.delete(self)


engine = create_engine(f"sqlite:///main.db")
Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

Flat.__table__.create(bind=engine, checkfirst=True)
