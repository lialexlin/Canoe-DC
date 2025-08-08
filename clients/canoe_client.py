import requests
from datetime import datetime, timedelta
from loguru import logger
import config

class CanoeClient:
    def __init__(self):
        self.base_url = config.CANOE_BASE_URL
        self.client_id = config.CANOE_CLIENT_ID
        self.client_secret = config.CANOE_CLIENT_SECRET
        self.access_token = None
        self.headers = {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }
        
        # Get access token on initialization
        self._get_access_token()
    
    def _get_access_token(self):
        """Get access token using client credentials"""
        logger.info("🔑 Getting Canoe access token...")
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(
            f'{self.base_url}/oauth/token',
            data=data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        response.raise_for_status()
        
        token_data = response.json()
        self.access_token = token_data['access_token']
        
        # Update headers with token
        self.headers['Authorization'] = f'Bearer {self.access_token}'
        logger.success("✅ Access token obtained")
    
    def get_new_quarterly_reports(self, days_back=7):
        """Get quarterly reports from last N days"""
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
        
        params = {
            'document_type': 'Quarterly Report',
            'document_status': 'Complete',
            'data_date_start': start_date,
            'data_date_end': end_date,
            'fields': 'id,name,document_type,data_date'
        }
        
        response = requests.get(
            f'{self.base_url}/v1/documents/data',
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def download_pdf(self, document_id):
        """Download a specific PDF"""
        response = requests.get(
            f'{self.base_url}/v1/documents/{document_id}',
            headers=self.headers
        )
        response.raise_for_status()
        return response.content