import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
CANOE_CLIENT_ID = os.getenv('CANOE_CLIENT_ID')
CANOE_CLIENT_SECRET = os.getenv('CANOE_CLIENT_SECRET')
CANOE_BASE_URL = os.getenv('CANOE_BASE_URL', 'https://api.canoesoftware.com')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
NOTION_TOKEN = os.getenv('NOTION_TOKEN')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

# Processing Settings
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
BATCH_SIZE = 5  # Process 5 PDFs at a time
TEMP_DIR = 'data/temp_pdfs'

# Document Filters
DOCUMENT_TYPES = ['Quarterly Report', 'Account Statement']
MIN_FILE_SIZE = 1000  # bytes
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Summary Settings
SUMMARY_MAX_LENGTH = 1000  # words
SUMMARY_STYLE = 'executive'  # executive, detailed, brief