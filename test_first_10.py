#!/usr/bin/env python3
"""
Test script to process first 10 Q1 2025 quarterly reports
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.canoe_client import CanoeClient
from clients.claude_client import ClaudeClient
from clients.google_sheets_client import GoogleSheetsClient
from loguru import logger
from utils.logger import setup_logging

def process_first_10():
    """Process first 10 quarterly reports from Q1 2025"""
    setup_logging()
    logger.info("Starting test: First 10 Q1 2025 Quarterly Reports")
    
    try:
        # Initialize clients
        logger.info("Initializing clients...")
        canoe = CanoeClient()
        claude = ClaudeClient()
        google_sheets = GoogleSheetsClient()
        
        # Get Q1 2025 quarterly reports
        logger.info("Fetching Q1 2025 Quarterly Reports...")
        filter_config = {
            'document_type': 'Quarterly Report',
            'data_date_start': '2025-01-01',
            'data_date_end': '2025-03-31',
            'fields': 'id,name,document_type,data_date,fund_id,fund_sponsor,allocations,investment,investment_id'
        }
        
        documents = canoe.get_documents_by_filter(filter_config)
        logger.info(f"Found {len(documents)} quarterly reports in Q1 2025")
        
        # Process first 10 documents
        docs_to_process = documents[:10]
        logger.info(f"Processing first {len(docs_to_process)} documents...")
        
        for i, doc in enumerate(docs_to_process, 1):
            try:
                logger.info(f"\n[{i}/10] Processing: {doc.get('name', 'Unknown')}")
                
                # Download PDF
                logger.info("   Downloading PDF...")
                pdf_data, pdf_name = canoe.download_document(doc['id'])
                
                # Extract investment name
                investment_name = 'Unknown'
                if 'allocations' in doc and isinstance(doc['allocations'], list) and len(doc['allocations']) > 0:
                    first_alloc = doc['allocations'][0]
                    if isinstance(first_alloc, dict) and 'investment' in first_alloc:
                        investment_name = first_alloc['investment']
                
                logger.info(f"   Investment: {investment_name}")
                
                # Create document info
                doc_info = {
                    'id': doc['id'],
                    'name': pdf_name,
                    'document_type': doc.get('document_type', 'Quarterly Report'),
                    'data_date': doc.get('data_date', ''),
                    'investment': investment_name
                }
                
                # Generate Claude summary
                logger.info("   Generating Claude summary...")
                summary = claude.summarize_pdf(pdf_data, doc_info)
                logger.info(f"   Summary length: {len(summary)} characters")
                
                # Save to Google Sheets
                logger.info("   Saving to Google Sheets...")
                sheets_url = google_sheets.add_summary_row(doc_info, summary, notion_url=None)
                logger.success(f"   ✅ Saved to Google Sheets")
                
            except Exception as e:
                logger.error(f"   ❌ Failed: {e}")
                continue
        
        # Get final statistics
        stats = google_sheets.get_summary_statistics()
        logger.success(f"\n✅ Test complete!")
        logger.info(f"📊 Google Sheets URL: {stats['spreadsheet_url']}")
        logger.info(f"📊 Total documents in sheet: {stats['total_documents']}")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    process_first_10()