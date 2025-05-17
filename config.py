import os

# Basic configuration
VERSION = '1.0.0'
PORT = int(os.environ.get('PORT', 5000))
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# LLM configuration
LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'openai')  # 'openai', 'anthropic', or 'local'
LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-4')
LLM_TEMPERATURE = float(os.environ.get('LLM_TEMPERATURE', 0.7))
LLM_MAX_TOKENS = int(os.environ.get('LLM_MAX_TOKENS', 500))

# Cambodia-specific settings
DEFAULT_CITY = 'Phnom Penh'
SUPPORTED_CITIES = ['Phnom Penh', 'Siem Reap', 'Battambang', 'Sihanoukville', 'Kampot']

# Cache settings
ENABLE_CACHE = os.environ.get('ENABLE_CACHE', 'True').lower() == 'true'
CACHE_EXPIRY = int(os.environ.get('CACHE_EXPIRY', 3600))  # 1 hour default