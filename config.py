import os
from pathlib import Path
from dotenv import load_dotenv

dotenv_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path)

STEAM_API_KEY = os.environ.get('STEAM_API_KEY')
FLASKAPP_SECRET_KEY = os.environ.get('FLASKAPP_SECRET_KEY')
