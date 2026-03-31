# central config for everything - hw pins, display specs, ai models, paths
# pull from .env where possible so nothing sensitive is hardcoded

import os
from dotenv import load_dotenv

load_dotenv()

# eink display
VCOM           = float(os.getenv("VCOM", -2.06))
SPI_HZ         = int(os.getenv("SPI_HZ", 24000000))
DISPLAY_WIDTH  = 1872
DISPLAY_HEIGHT = 1404
GREY_LEVELS    = 16

# rotary encoder gpio pins (bcm numbering)
ENCODER_CLK         = int(os.getenv("ENCODER_CLK", 17))
ENCODER_DT          = int(os.getenv("ENCODER_DT", 18))
ENCODER_SW          = int(os.getenv("ENCODER_SW", 27))
ENCODER_DEBOUNCE_MS = 5

# reddit
SUBREDDITS  = os.getenv("SUBREDDITS", "worldnews,technology,science").split(",")
FETCH_LIMIT = int(os.getenv("FETCH_LIMIT", 10))

# ai / llm
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
EMBED_MODEL  = os.getenv("EMBED_MODEL", "all-MiniLM-L6-v2")

# scheduler
REFRESH_INTERVAL_MINUTES = int(os.getenv("REFRESH_INTERVAL_MINUTES", 30))

# paths
BASE_DIR       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH        = os.path.join(BASE_DIR, "data", "chromadb")
LOG_PATH       = os.path.join(BASE_DIR, "logs", "nexus_ink.log")
FONT_PATH      = os.path.join(BASE_DIR, "assets", "fonts", "DejaVuSans.ttf")
FONT_BOLD_PATH = os.path.join(BASE_DIR, "assets", "fonts", "DejaVuSans-Bold.ttf")
