#!/usr/bin/env python3
"""
Quarterly Reports Processor
Downloads quarterly reports from the last N days and generates Claude summaries
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
    """Main execution function for quarterly reports processing"""
    parser = argparse.ArgumentParser(description='Process documents with Claude summaries using flexible filters')
    
    # Filter options (mutually exclusive groups)
    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument('--preset', type=str,
                             help='Use a predefined filter preset (e.g., quarterly_reports)')
    filter_group.add_argument('--days-back', type=int, default=None,
                             help='Number of days back to search (legacy mode, default: 14)')
    
    # Configuration
    parser.add_argument('--filter-file', type=str, default='config/document_filters.json',
                       help='Path to filter configuration file')
    parser.add_argument('--list-presets', action='store_true',
                       help='List available presets and exit')
    
    # Parameter overrides (can be used with presets)
    parser.add_argument('--document-type', type=str,
                       help='Override document type filter')
    parser.add_argument('--data-date-start', type=str,
                       help='Override data date start (YYYY-MM-DD)')
    parser.add_argument('--data-date-end', type=str,
                       help='Override data date end (YYYY-MM-DD)')
    
    # Storage options
    parser.add_argument('--no-notion', action='store_true',
                       help='Skip saving summaries to Notion')
    parser.add_argument('--google-sheets', action='store_true',
                       help='Also save summaries to Google Sheets')
    parser.add_argument('--sheets-only', action='store_true',
                       help='Save to Google Sheets only (skip Notion)')
    
    args = parser.parse_args()
    
    setup_logging()
    logger.info("🚀 Starting Document Processor with Flexible Filtering")
    
    try:
        # Initialize clients
        logger.info("📡 Initializing API clients...")
        canoe = CanoeClient()
        
        # Handle --list-presets option
        if args.list_presets:
            print("\n📋 Available Filter Presets:")
            print("="*50)
            config_data = canoe.load_filter_presets(args.filter_file)
            presets = config_data.get('presets', {})
            
            if not presets:
                print("❌ No presets found in configuration file")
                return
            
            for preset_name, preset_config in presets.items():
                print(f"\n🎯 {preset_name}")
                print(f"   Name: {preset_config.get('name', 'N/A')}")
                print(f"   Description: {preset_config.get('description', 'N/A')}")
                
                # Show key parameters
                key_params = {}
                for key in ['document_type', 'data_date_start', 'data_date_end', 'file_upload_time_start']:
                    if key in preset_config:
                        key_params[key] = preset_config[key]
                
                if key_params:
                    print(f"   Parameters: {key_params}")
            
            print(f"\n💡 Usage: python src/bulk.py --preset <preset_name>")
            return
        
        # Determine filter method and get documents
        overrides = {}
        if args.document_type:
            overrides['document_type'] = args.document_type
        if args.data_date_start:
            overrides['data_date_start'] = args.data_date_start
        if args.data_date_end:
            overrides['data_date_end'] = args.data_date_end
            
        if args.preset:
            # Use preset-based filtering
            logger.info(f"🎯 Using preset filter: {args.preset}")
            reports = canoe.get_documents_by_preset(args.preset, args.filter_file, overrides)
            processing_method = f"preset '{args.preset}'"
        elif args.days_back is not None:
            # Legacy mode: days-back filtering
            logger.info(f"📊 Using legacy mode: last {args.days_back} days")
            reports = canoe.get_new_quarterly_reports(days_back=args.days_back)
            processing_method = f"last {args.days_back} days"
        else:
            # Default: use quarterly_reports preset
            logger.info("📊 No filter specified, using default 'quarterly_reports' preset")
            reports = canoe.get_documents_by_preset('quarterly_reports', args.filter_file, overrides)
            processing_method = "default preset 'quarterly_reports'"
        
        claude = ClaudeClient()
        
        # Initialize storage clients based on arguments
        notion = None
        google_sheets = None
        
        if args.sheets_only:
            args.no_notion = True
            args.google_sheets = True
        
        if not args.no_notion:
            notion = NotionClient()
            
        if args.google_sheets or args.sheets_only:
            try:
                from clients.google_sheets_client import GoogleSheetsClient
                google_sheets = GoogleSheetsClient()
                logger.success("✅ Google Sheets client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Sheets: {e}")
                google_sheets = None
        
        if not reports:
            logger.info(f"No documents found matching filter ({processing_method})")
            return
        
        logger.info(f"Found {len(reports)} documents to process ({processing_method})")
        
        # Process each document individually: download → summarize → save
        processed_count = 0
        for i, report in enumerate(reports, 1):
            document_id = report['id']
            document_name = report.get('name', 'Unknown Document')
            
            logger.info(f"📄 [{i}/{len(reports)}] Processing: {document_name} (ID: {document_id})")
            
            try:
                # Step 1: Download PDF and get original filename
                logger.info("   ⬇️  Downloading PDF and getting document name...")
                pdf_data, pdf_name = canoe.download_document(document_id)
                logger.success(f"   ✅ Downloaded: {pdf_name}")
                
                # Create document info using original filename
                doc_info = {
                    'id': document_id,
                    'name': pdf_name,  # Use original filename for Notion title
                    'document_type': report.get('document_type'),
                    'data_date': report.get('data_date')
                }
                
                # Step 2: Generate summary with Claude
                logger.info("   🤖 Generating Claude summary...")
                summary = claude.summarize_pdf(pdf_data, doc_info)
                logger.success("   ✅ Summary generated")
                
                # Step 3: Save to Notion (if enabled)
                notion_url = None
                if not args.no_notion and notion:
                    logger.info("   💾 Saving to Notion...")
                    response = notion.create_summary_page(doc_info, summary)
                    notion_url = response.get('url', '')
                    logger.success("   ✅ Saved to Notion")
                
                # Step 4: Save to Google Sheets (if enabled)
                if google_sheets:
                    logger.info("   📊 Saving to Google Sheets...")
                    sheets_url = google_sheets.add_summary_row(doc_info, summary, notion_url)
                    logger.success("   ✅ Saved to Google Sheets")
                
                processed_count += 1
                logger.success(f"✅ [{i}/{len(reports)}] Completed: {document_name}")
                
            except Exception as e:
                logger.error(f"❌ [{i}/{len(reports)}] Failed to process {document_name}: {e}")
                continue
        
        logger.success(f"🎉 Successfully processed {processed_count}/{len(reports)} documents")
        
        # Print summary
        print(f"\nProcessing Summary:")
        print(f"   Filter method: {processing_method}")
        print(f"   Documents found: {len(reports)}")
        print(f"   Documents processed: {processed_count}")
        if args.preset:
            print(f"   Preset used: {args.preset}")
        if overrides:
            print(f"   Parameter overrides: {overrides}")
        
        if not args.no_notion and notion:
            print(f"   Saved to Notion: Yes")
        else:
            print(f"   Saved to Notion: No (skipped)")
            
        if google_sheets:
            print(f"   Saved to Google Sheets: Yes")
            stats = google_sheets.get_summary_statistics()
            if stats:
                print(f"   Total in Sheets: {stats['total_documents']}")
                print(f"   Spreadsheet URL: {stats['spreadsheet_url']}")
        else:
            print(f"   Saved to Google Sheets: No")
            
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()