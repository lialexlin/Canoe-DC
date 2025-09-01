#!/usr/bin/env python3
"""
Single Document Processor
Downloads and processes a specific document by ID with Claude summary
"""

import argparse
import sys
import os
from loguru import logger

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clients.canoe_client import CanoeClient
from clients.claude_client import ClaudeClient
from clients.notion_client import NotionClient
from utils.logger import setup_logging


def main():
    """Main execution function for single document processing"""
    parser = argparse.ArgumentParser(description='Process a single document with Claude summary')
    parser.add_argument('--document-id', type=str,
                       help='Specific document ID to process (if not provided, uses default test document)')
    parser.add_argument('--no-summary', action='store_true',
                       help='Skip generating Claude summary (download only)')
    parser.add_argument('--no-notion', action='store_true',
                       help='Skip saving summary to Notion')
    parser.add_argument('--google-sheets', action='store_true',
                       help='Also save summary to Google Sheets')
    parser.add_argument('--sheets-only', action='store_true',
                       help='Save to Google Sheets only (skip Notion)')
    parser.add_argument('--save-pdf', type=str,
                       help='Save PDF to specified file path')
    
    args = parser.parse_args()
    
    setup_logging()
    logger.info("🚀 Starting Single Document Processor")
    
    try:
        # Handle sheets-only option
        if args.sheets_only:
            args.no_notion = True
            args.google_sheets = True
        
        # Initialize clients
        logger.info("📡 Initializing API clients...")
        canoe = CanoeClient()
        
        if not args.no_summary:
            claude = ClaudeClient()
        
        notion = None
        google_sheets = None
        
        if not args.no_notion and not args.no_summary:
            notion = NotionClient()
            
        if (args.google_sheets or args.sheets_only) and not args.no_summary:
            try:
                from clients.google_sheets_client import GoogleSheetsClient
                google_sheets = GoogleSheetsClient()
                logger.success("✅ Google Sheets client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Sheets: {e}")
                google_sheets = None
        
        # Download document
        if not args.document_id:
            logger.error("❌ Document ID is required. Use --document-id to specify which document to process.")
            sys.exit(1)
            
        logger.info(f"📄 Processing document ID: {args.document_id}")
        
        # First, get document metadata including investment info
        logger.info("   📋 Getting document metadata...")
        filter_config = {
            'document_id': args.document_id,
            'fields': 'id,name,document_type,data_date,allocations,investment,investment_id'
        }
        documents = canoe.get_documents_by_filter(filter_config)
        
        # Extract investment name from the document metadata
        investment_name = 'Unknown'
        if documents and len(documents) > 0:
            doc = documents[0]
            if 'allocations' in doc and isinstance(doc['allocations'], list) and len(doc['allocations']) > 0:
                first_alloc = doc['allocations'][0]
                if isinstance(first_alloc, dict) and 'investment' in first_alloc:
                    investment_name = first_alloc['investment']
        
        # Step 1: Download PDF and get document name
        logger.info("   ⬇️  Downloading PDF and getting document name...")
        pdf_data, pdf_name = canoe.download_document(args.document_id)
        logger.success(f"   ✅ Downloaded: {pdf_name}")
        
        # Create document info
        doc_info = {
            'id': args.document_id,
            'name': pdf_name,
            'investment': investment_name  # Add investment name
        }
        
        # Save PDF if requested
        if args.save_pdf:
            with open(args.save_pdf, 'wb') as f:
                f.write(pdf_data)
            logger.success(f"💾 PDF saved to: {args.save_pdf}")
        
        # Generate summary if not skipped
        summary = None
        if not args.no_summary:
            logger.info("🤖 Generating Claude summary...")
            summary = claude.summarize_pdf(pdf_data, doc_info)
            logger.success("✅ Summary generated")
            
            # Print summary
            print(f"\nDocument Summary:")
            print(f"   Document: {doc_info['name']}")
            print(f"   ID: {doc_info['id']}")
            print(f"\nSummary:\n{summary}\n")
        
        # Save to Notion if enabled
        notion_url = None
        if not args.no_notion and not args.no_summary and summary and notion:
            logger.info("💾 Saving summary to Notion...")
            response = notion.create_summary_page(doc_info, summary)
            notion_url = response.get('url', '')
            logger.success("✅ Summary saved to Notion")
        
        # Save to Google Sheets if enabled
        if google_sheets and summary:
            logger.info("📊 Saving summary to Google Sheets...")
            sheets_url = google_sheets.add_summary_row(doc_info, summary, notion_url)
            logger.success(f"✅ Summary saved to Google Sheets")
            print(f"Spreadsheet URL: {sheets_url}")
        
        logger.success(f"🎉 Successfully processed document: {doc_info['name']}")
        
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()