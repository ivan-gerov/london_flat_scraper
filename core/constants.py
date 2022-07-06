import os
from pathlib import Path

ROOT_PROJECT_DIR = Path(__file__).parent.parent
DATASETS = os.path.join(ROOT_PROJECT_DIR, "datasets")
API_KEYS = os.path.join(ROOT_PROJECT_DIR, "API_KEYS.ini")
POIS = os.path.join(ROOT_PROJECT_DIR, "pois")
TOTENHAM_COURT_ROAD_COORDINATES = "51.516271986674376,-0.13061312923934032"
