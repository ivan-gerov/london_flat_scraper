from core.scraper import RightmoveScraperV2, URL, PARAMS
from core.constants import DATASETS
import pandas as pd

scraper = RightmoveScraperV2(url=URL, params=PARAMS, additional_info=True)
scraper.save_results(f"{DATASETS}/demo_available.csv")
scraper.save_to_db()
