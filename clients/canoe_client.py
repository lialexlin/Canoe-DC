import requests
import os
import time
from datetime import datetime, timedelta
from loguru import logger
from src import config

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
        """Get access token using client credentials with retry"""
        logger.info("🔑 Getting Canoe access token...")
        
        # Debug logging
        logger.debug(f"Base URL: {self.base_url}")
        logger.debug(f"Client ID: {self.client_id[:8]}..." if self.client_id else "Client ID: None")
        logger.debug(f"Client Secret: {'***' if self.client_secret else 'None'}")
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        for attempt in range(3):
            try:
                response = requests.post(
                    f'{self.base_url}/oauth/token',
                    data=data,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                
                # Debug response
                logger.debug(f"Response status: {response.status_code}")
                if response.status_code != 200:
                    logger.error(f"Response text: {response.text}")
                
                response.raise_for_status()
                
                token_data = response.json()
                self.access_token = token_data['access_token']
                
                # Update headers with token
                self.headers['Authorization'] = f'Bearer {self.access_token}'
                logger.success("✅ Access token obtained")
                return
                
            except requests.exceptions.RequestException as e:
                if attempt < 2:  # Don't log on final attempt
                    logger.warning(f"Token request attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s
                else:
                    raise
    
    def get_new_quarterly_reports(self, days_back=7):
        """Get quarterly reports from last N days"""
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%dT00:00:00Z')
        
        params = {
            'document_type': 'Quarterly Report',
            'file_upload_time_start': start_date,
            'fields': 'id,name,document_type,data_date'
        }
        
        logger.info(f"📋 API params: {params}")
        
        response = requests.get(
            f'{self.base_url}/v1/documents/data',
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        documents = response.json()
        
        logger.info(f"📊 Found {len(documents)} quarterly reports")
        
        return documents
    
    def get_document_metadata(self, document_id):
        """Get document metadata including original filename"""
        params = {
            'document_id': document_id,
            'fields': 'original_file_name,name'
        }
        
        for attempt in range(3):
            try:
                response = requests.get(
                    f'{self.base_url}/v1/documents/data/',
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract filename from response
                if data and len(data) > 0:
                    doc_data = data[0]
                    original_name = doc_data.get('original_file_name')
                    if original_name:
                        return original_name
                
                # Fallback to generic name if no original_file_name found
                return f"Document_{document_id}.pdf"
                
            except requests.exceptions.RequestException as e:
                if attempt < 2:
                    logger.warning(f"Metadata fetch attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(2 ** attempt)
                else:
                    logger.warning(f"Failed to fetch document metadata: {e}. Using generic filename.")
                    return f"Document_{document_id}.pdf"

    def download_document(self, document_id):
        """Download PDF with retry and get original filename from metadata"""
        # Get original filename from metadata
        pdf_name = self.get_document_metadata(document_id)
        logger.info(f"   📋 Document name: {pdf_name}")

        # Download PDF with retry
        for attempt in range(3):
            try:
                pdf_resp = requests.get(
                    f'{self.base_url}/v1/documents/{document_id}',
                    headers=self.headers,
                    timeout=180
                )
                pdf_resp.raise_for_status()
                pdf_data = pdf_resp.content
                return pdf_data, pdf_name
            except requests.exceptions.RequestException as e:
                if attempt < 2:
                    logger.warning(f"PDF download attempt {attempt + 1} failed: {e}. Retrying...")
                    time.sleep(2 ** attempt)
                else:
                    raise
    
    def download_pdf(self, document_id):
        """Download a specific PDF (for quarterly reports that already have names)"""
        response = requests.get(
            f'{self.base_url}/v1/documents/{document_id}',
            headers=self.headers,
            timeout=180
        )
        response.raise_for_status()
        return response.content
