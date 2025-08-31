import requests
import os
import time
import json
import re
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
    
    def get_documents_by_filter(self, filter_config):
        """Get documents using flexible filter configuration
        
        Args:
            filter_config (dict): Configuration with API parameters
                - Can include any Canoe API parameter
                - Supports auto-date format (auto:30d)
                - Example: {'document_type': 'Quarterly Report', 'file_upload_time_start': 'auto:30d'}
        
        Returns:
            list: List of document objects matching the filter
        """
        # Process auto-dates and build API parameters
        params = self._process_filter_config(filter_config)
        
        logger.info(f"📋 API filter params: {params}")
        
        try:
            response = requests.get(
                f'{self.base_url}/v1/documents/data',
                headers=self.headers,
                params=params,
                timeout=60
            )
            response.raise_for_status()
            documents = response.json()
            
            document_types = params.get('document_type', 'documents')
            logger.info(f"📊 Found {len(documents)} {document_types}")
            
            return documents
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch documents with filter: {e}")
            raise
    
    def _process_filter_config(self, filter_config):
        """Process filter configuration and handle auto-dates
        
        Args:
            filter_config (dict): Raw filter configuration
            
        Returns:
            dict: Processed parameters ready for API
        """
        params = {}
        
        for key, value in filter_config.items():
            # Skip metadata fields
            if key in ['name', 'description']:
                continue
                
            if isinstance(value, str) and value.startswith('auto:'):
                # Handle auto-date format: auto:30d, auto:1y
                params[key] = self._calculate_auto_date(value)
            else:
                params[key] = value
        
        # Set default fields if not specified
        if 'fields' not in params:
            params['fields'] = 'id,name,document_type,data_date'
            
        return params
    
    def _calculate_auto_date(self, auto_date_str):
        """Calculate actual date from auto-date string
        
        Args:
            auto_date_str (str): Format like 'auto:30d', 'auto:1y', 'auto:6m'
            
        Returns:
            str: ISO formatted date string
        """
        try:
            # Extract number and unit from auto:30d format
            match = re.match(r'auto:(\d+)([dmyh])', auto_date_str.lower())
            if not match:
                logger.warning(f"Invalid auto-date format: {auto_date_str}")
                return auto_date_str
            
            amount = int(match.group(1))
            unit = match.group(2)
            
            now = datetime.now()
            
            if unit == 'd':  # days
                target_date = now - timedelta(days=amount)
            elif unit == 'm':  # months (approximate)
                target_date = now - timedelta(days=amount * 30)
            elif unit == 'y':  # years (approximate) 
                target_date = now - timedelta(days=amount * 365)
            elif unit == 'h':  # hours
                target_date = now - timedelta(hours=amount)
            else:
                logger.warning(f"Unknown time unit: {unit}")
                return auto_date_str
            
            # Return ISO format for file_upload_time or simple date for data_date
            return target_date.strftime('%Y-%m-%dT%H:%M:%SZ')
            
        except Exception as e:
            logger.error(f"Error calculating auto-date {auto_date_str}: {e}")
            return auto_date_str

    def load_filter_presets(self, config_file='config/document_filters.json'):
        """Load filter presets from configuration file
        
        Args:
            config_file (str): Path to configuration file
            
        Returns:
            dict: Loaded configuration with presets
        """
        try:
            # Try absolute path first, then relative to project root
            config_path = config_file
            if not os.path.isabs(config_file):
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                config_path = os.path.join(project_root, config_file)
            
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            logger.info(f"✅ Loaded filter presets from {config_path}")
            return config_data
            
        except FileNotFoundError:
            logger.error(f"Filter configuration file not found: {config_path}")
            return {'presets': {}}
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in filter configuration: {e}")
            return {'presets': {}}
    
    def get_documents_by_preset(self, preset_name, config_file='config/document_filters.json', overrides=None):
        """Get documents using a named preset configuration
        
        Args:
            preset_name (str): Name of the preset to use
            config_file (str): Path to configuration file
            overrides (dict): Optional parameter overrides
            
        Returns:
            list: List of document objects
        """
        # Input validation
        if not preset_name or not isinstance(preset_name, str):
            raise ValueError("Preset name must be a non-empty string")
        
        if overrides and not isinstance(overrides, dict):
            raise ValueError("Overrides must be a dictionary")
        
        # Load presets
        config_data = self.load_filter_presets(config_file)
        presets = config_data.get('presets', {})
        
        if preset_name not in presets:
            available = ', '.join(presets.keys())
            raise ValueError(f"Preset '{preset_name}' not found. Available: {available}")
        
        # Get preset configuration
        preset_config = presets[preset_name].copy()
        
        # Validate and apply any overrides
        if overrides:
            self._validate_filter_overrides(overrides)
            preset_config.update(overrides)
            logger.info(f"Applied overrides to preset '{preset_name}': {list(overrides.keys())}")
        
        logger.info(f"🎯 Using preset '{preset_name}': {preset_config.get('description', '')}")
        
        return self.get_documents_by_filter(preset_config)
    
    def _validate_filter_overrides(self, overrides):
        """Validate filter override parameters"""
        valid_params = {
            'document_type', 'data_date_start', 'data_date_end', 'file_upload_time_start',
            'file_upload_time_end', 'document_status', 'fund_id', 'account_id', 'fields'
        }
        
        for key, value in overrides.items():
            if key not in valid_params:
                logger.warning(f"Unknown override parameter: {key}")
            
            # Basic validation for date parameters
            if key.endswith('_date_start') or key.endswith('_date_end'):
                if isinstance(value, str) and not value.startswith('auto:'):
                    # Should be in YYYY-MM-DD format
                    if not re.match(r'^\d{4}-\d{2}-\d{2}', value):
                        logger.warning(f"Date parameter {key} may not be in correct format (YYYY-MM-DD): {value}")
            
            # Validate document_type
            if key == 'document_type' and value:
                # Should be comma-separated string or single string
                if not isinstance(value, str):
                    raise ValueError(f"document_type must be a string, got {type(value)}")
                    
        return True
    
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
