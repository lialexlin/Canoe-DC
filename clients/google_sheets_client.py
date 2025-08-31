import os
import json
import time
from datetime import datetime
from loguru import logger
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from src import config

# Constants for Google Sheets API
MAX_SUMMARY_LENGTH = 500  # Maximum characters for summary in sheets
MAX_RETRIES = 3  # Maximum API call retries
RATE_LIMIT_DELAY = 0.1  # Seconds between API calls
BATCH_SIZE = 100  # Maximum rows per batch operation

class GoogleSheetsClient:
    def __init__(self):
        """Initialize Google Sheets client with credentials"""
        self.spreadsheet_id = None
        self.service = None
        self.last_api_call = 0  # Track last API call for rate limiting
        self._initialize_service()
    
    def _rate_limit(self):
        """Simple rate limiting to avoid hitting API quotas"""
        now = time.time()
        time_since_last_call = now - self.last_api_call
        if time_since_last_call < RATE_LIMIT_DELAY:
            time.sleep(RATE_LIMIT_DELAY - time_since_last_call)
        self.last_api_call = time.time()
    
    def _validate_input(self, data, max_length=None):
        """Validate and sanitize input data"""
        if data is None:
            return ""
        
        # Convert to string and limit length
        data_str = str(data).strip()
        if max_length and len(data_str) > max_length:
            data_str = data_str[:max_length-3] + "..."
            logger.warning(f"Truncated data to {max_length} characters")
        
        return data_str
    
    def _initialize_service(self):
        """Initialize Google Sheets API service"""
        try:
            # Get credentials from config (Bitwarden or env variables)
            credentials_json = config.get_config_value(
                "google-sheets", "credentials_json", "GOOGLE_SHEETS_CREDENTIALS_JSON"
            )
            self.spreadsheet_id = config.get_config_value(
                "google-sheets", "spreadsheet_id", "GOOGLE_SHEETS_SPREADSHEET_ID"
            )
            
            # Parse credentials JSON
            if isinstance(credentials_json, str):
                creds_dict = json.loads(credentials_json)
            else:
                creds_dict = credentials_json
            
            # Create credentials object
            credentials = service_account.Credentials.from_service_account_info(
                creds_dict,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Build service
            self.service = build('sheets', 'v4', credentials=credentials)
            logger.success("✅ Google Sheets API initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets API: {e}")
            raise
    
    def create_or_get_sheet(self, sheet_name="Quarterly Reports"):
        """Create a new sheet or get existing one"""
        try:
            # Validate sheet name
            sheet_name = self._validate_input(sheet_name, max_length=100)
            if not sheet_name:
                sheet_name = "Quarterly Reports"
            
            # Rate limit API call
            self._rate_limit()
            
            # Get all sheets in spreadsheet
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheets = sheet_metadata.get('sheets', [])
            
            # Check if sheet already exists
            for sheet in sheets:
                if sheet['properties']['title'] == sheet_name:
                    logger.info(f"📊 Using existing sheet: {sheet_name}")
                    return sheet['properties']['sheetId']
            
            # Create new sheet if doesn't exist
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name,
                            'gridProperties': {
                                'rowCount': 1000,
                                'columnCount': 10
                            }
                        }
                    }
                }]
            }
            
            response = self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=request_body
            ).execute()
            
            sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
            logger.success(f"✅ Created new sheet: {sheet_name}")
            
            # Add headers to the new sheet
            self._add_headers(sheet_name)
            
            return sheet_id
            
        except HttpError as e:
            logger.error(f"Failed to create/get sheet: {e}")
            raise
    
    def _add_headers(self, sheet_name):
        """Add headers to a new sheet"""
        headers = [
            ['Fund Name', 'Document ID', 'Date Processed', 'Data Date', 
             'Summary', 'Document Type', 'Processing Status', 'Notion URL']
        ]
        
        range_name = f"{sheet_name}!A1:H1"
        
        body = {
            'values': headers
        }
        
        self.service.spreadsheets().values().update(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Format headers (bold, background color)
        self._format_headers(sheet_name)
    
    def _format_headers(self, sheet_name):
        """Format header row with bold text and background color"""
        try:
            # Get sheet ID
            sheet_metadata = self.service.spreadsheets().get(
                spreadsheetId=self.spreadsheet_id
            ).execute()
            
            sheet_id = None
            for sheet in sheet_metadata['sheets']:
                if sheet['properties']['title'] == sheet_name:
                    sheet_id = sheet['properties']['sheetId']
                    break
            
            if sheet_id is None:
                return
            
            requests = [
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.2,
                                    'green': 0.5,
                                    'blue': 0.8
                                },
                                'textFormat': {
                                    'bold': True,
                                    'foregroundColor': {
                                        'red': 1.0,
                                        'green': 1.0,
                                        'blue': 1.0
                                    }
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                },
                {
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': sheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': 8
                        }
                    }
                }
            ]
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={'requests': requests}
            ).execute()
            
        except Exception as e:
            logger.warning(f"Failed to format headers: {e}")
    
    def add_summary_row(self, document_info, summary, notion_url=None, sheet_name="Quarterly Reports"):
        """Add a summary row to the spreadsheet"""
        try:
            # Ensure sheet exists
            self.create_or_get_sheet(sheet_name)
            
            # Get the next available row
            range_name = f"{sheet_name}!A:A"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            next_row = len(values) + 1
            
            # Prepare row data with input validation
            row_data = [
                self._validate_input(document_info.get('name', 'Unknown'), max_length=100),
                self._validate_input(document_info.get('id', ''), max_length=50),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                self._validate_input(document_info.get('data_date', ''), max_length=50),
                self._validate_input(summary, max_length=MAX_SUMMARY_LENGTH) if summary else 'NA',
                self._validate_input(document_info.get('document_type', 'Quarterly Report'), max_length=50),
                'Completed',
                self._validate_input(notion_url or '', max_length=200)
            ]
            
            # Add row to sheet
            range_name = f"{sheet_name}!A{next_row}:H{next_row}"
            body = {
                'values': [row_data]
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.success(f"✅ Added summary to Google Sheets (row {next_row})")
            
            # Return spreadsheet URL
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit#gid=0"
            
        except HttpError as e:
            logger.error(f"Failed to add summary row: {e}")
            raise
    
    def batch_add_summaries(self, summaries_data, sheet_name="Quarterly Reports"):
        """Add multiple summaries at once for better performance"""
        try:
            # Ensure sheet exists
            self.create_or_get_sheet(sheet_name)
            
            # Get the next available row
            range_name = f"{sheet_name}!A:A"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            next_row = len(values) + 1
            
            # Prepare batch data
            rows = []
            for data in summaries_data:
                row = [
                    data['document_info'].get('name', 'Unknown'),
                    data['document_info'].get('id', ''),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    data['document_info'].get('data_date', ''),
                    data['summary'][:500] if data.get('summary') else 'NA',
                    data['document_info'].get('document_type', 'Quarterly Report'),
                    'Completed',
                    data.get('notion_url', '')
                ]
                rows.append(row)
            
            # Add all rows at once
            range_name = f"{sheet_name}!A{next_row}:H{next_row + len(rows) - 1}"
            body = {
                'values': rows
            }
            
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.success(f"✅ Added {len(rows)} summaries to Google Sheets")
            
            return f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}/edit#gid=0"
            
        except HttpError as e:
            logger.error(f"Failed to batch add summaries: {e}")
            raise
    
    def get_summary_statistics(self, sheet_name="Quarterly Reports"):
        """Get statistics about processed documents"""
        try:
            range_name = f"{sheet_name}!A:H"
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            
            if len(values) <= 1:  # Only headers or empty
                return {
                    'total_documents': 0,
                    'documents_with_summaries': 0,
                    'documents_without_summaries': 0
                }
            
            # Skip header row
            data_rows = values[1:]
            
            total = len(data_rows)
            with_summaries = sum(1 for row in data_rows if len(row) > 4 and row[4] != 'NA')
            without_summaries = total - with_summaries
            
            return {
                'total_documents': total,
                'documents_with_summaries': with_summaries,
                'documents_without_summaries': without_summaries,
                'spreadsheet_url': f"https://docs.google.com/spreadsheets/d/{self.spreadsheet_id}"
            }
            
        except HttpError as e:
            logger.error(f"Failed to get statistics: {e}")
            return None