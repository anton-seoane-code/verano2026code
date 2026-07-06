import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com/v1')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.8'))
MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1024'))
CONTEXT_TURNS = int(os.getenv('CONTEXT_TURNS', '8'))
