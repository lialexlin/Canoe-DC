#!/usr/bin/env python3
"""
Test Google Sheets configuration with new spreadsheet ID
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clients.google_sheets_client import GoogleSheetsClient
from loguru import logger
from utils.logger import setup_logging

def test_sheets_config():
    """Test Google Sheets with new configuration"""
    setup_logging()
    
    logger.info("Testing Google Sheets configuration...")
    logger.info("Expected Spreadsheet ID: 1fFae7B7YfDImqygh9wvEQPaDQQgLDFLTN3DH4ayuVlg")
    logger.info("Expected User Email: xelailnil@gmail.com")
    
    try:
        # Initialize client
        client = GoogleSheetsClient()
        logger.success("✅ Google Sheets client initialized successfully")
        
        # Check spreadsheet ID
        logger.info(f"Using Spreadsheet ID: {client.spreadsheet_id}")
        
        # Try to get sheet info
        sheet_id = client.create_or_get_sheet("Test Sheet")
        logger.success(f"✅ Accessed/Created sheet with ID: {sheet_id}")
        
        # Try to add a test row
        test_doc = {
            'id': 'TEST001',
            'name': 'Test Document',
            'document_type': 'Test',
            'data_date': '2024-12-01'
        }
        
        url = client.add_summary_row(test_doc, "This is a test summary", sheet_name="Test Sheet")
        logger.success(f"✅ Successfully added test row")
        logger.info(f"Spreadsheet URL: {url}")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sheets_config()