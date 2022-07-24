import os
from pathlib import Path

ROOT_PROJECT_DIR = Path(__file__).parent.parent
LONDON_FLAT_SCRAPER = Path(__file__).parent
DATASETS = os.path.join(LONDON_FLAT_SCRAPER, "datasets")
POIS = os.path.join(LONDON_FLAT_SCRAPER, "pois")
API_KEYS = os.path.join(ROOT_PROJECT_DIR, "API_KEYS.ini")
TOTENHAM_COURT_ROAD_COORDINATES = "51.516271986674376,-0.13061312923934032"
