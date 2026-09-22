from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent

PROMPT_PATH = BASE_DIR / 'prompts'
INPUT_PATH = BASE_DIR / 'input_data/articoli.csv'
OUTPUT_PATH = BASE_DIR / 'output'


LITE_MODEL = "gemini-2.5-flash-lite"
FLASH_MODEL = "gemini-2.5-flash"
PRO_MODEL = "gemini-2.5-pro"
SEARCH_MODEL = "gemini-3-flash-preview"

MODEL_PROVIDER = "google_genai"

TAGS = 'Hi-Tech, Software, AI, Cyber-Security, Servizi-IT'

DATE = str(datetime.now().date())

CONFIG = {
    'configurable': {
        'input_path': INPUT_PATH,
        'output_path': OUTPUT_PATH,
        'thread_id': '123',
        'date': DATE
    }
}