from london_flat_scraper.core.models import Property
from london_flat_scraper.core.scraper_v2 import RightmoveScraperV2

Property.remove_obsolete()
scraper = RightmoveScraperV2(
    "https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=STATION%5E245&minBedrooms=1&maxPrice=1750&radius=5.0&propertyTypes=&maxDaysSinceAdded=1&includeLetAgreed=false&mustHave=&dontShow=houseShare%2Cretirement%2Cstudent&furnishTypes=&keywords=",
    additional_info=True,
)
scraper.store()

