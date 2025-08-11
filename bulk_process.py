#!/usr/bin/env python3
"""
Quarterly Reports Processor
Downloads quarterly reports from the last N days and generates Claude summaries
"""

import argparse
import sys
from loguru import logger

from clients.canoe_client import CanoeClient
from clients.claude_client import ClaudeClient
from clients.notion_client import NotionClient
from utils.logger import setup_logging


def main():
    """Main execution function for quarterly reports processing"""
    parser = argparse.ArgumentParser(description='Process quarterly reports with Claude summaries')
    parser.add_argument('--days-back', type=int, default=7, 
                       help='Number of days back to search for reports (default: 7)')
    parser.add_argument('--no-notion', action='store_true',
                       help='Skip saving summaries to Notion')
    
    args = parser.parse_args()
    
    setup_logging()
    logger.info("🚀 Starting Quarterly Reports Processor")
    
    try:
        # Initialize clients
        logger.info("📡 Initializing API clients...")
        canoe = CanoeClient()
        claude = ClaudeClient()
        
        if not args.no_notion:
            notion = NotionClient()
        
        # Get list of quarterly reports
        logger.info(f"📊 Getting quarterly reports from last {args.days_back} days...")
        reports = canoe.get_new_quarterly_reports(days_back=args.days_back)
        
        if not reports:
            logger.info("No quarterly reports found to process")
            return
        
        logger.info(f"Found {len(reports)} quarterly reports to process")
        
        # Process each report individually: download → summarize → save to Notion
        processed_count = 0
        for i, report in enumerate(reports, 1):
            document_id = report['id']
            document_name = report.get('name', 'Unknown Document')
            
            logger.info(f"📄 [{i}/{len(reports)}] Processing: {document_name} (ID: {document_id})")
            
            try:
                # Step 1: Download PDF
                logger.info("   ⬇️  Downloading PDF...")
                pdf_data = canoe.download_pdf(document_id)
                logger.success("   ✅ PDF downloaded")
                
                # Create document info
                doc_info = {
                    'id': document_id,
                    'name': document_name,
                    'document_type': report.get('document_type'),
                    'data_date': report.get('data_date')
                }
                
                # Step 2: Generate summary with Claude
                logger.info("   🤖 Generating Claude summary...")
                summary = claude.summarize_pdf(pdf_data, doc_info)
                logger.success("   ✅ Summary generated")
                
                # Step 3: Save to Notion (if enabled)
                if not args.no_notion:
                    logger.info("   💾 Saving to Notion...")
                    notion.create_summary_page(doc_info, summary)
                    logger.success("   ✅ Saved to Notion")
                
                processed_count += 1
                logger.success(f"✅ [{i}/{len(reports)}] Completed: {document_name}")
                
            except Exception as e:
                logger.error(f"❌ [{i}/{len(reports)}] Failed to process {document_name}: {e}")
                continue
        
        logger.success(f"🎉 Successfully processed {processed_count}/{len(reports)} quarterly reports")
        
        # Print summary
        print(f"\n📋 Processing Summary:")
        print(f"   Reports found: {len(reports)}")
        print(f"   Reports processed: {processed_count}")
        print(f"   Days searched: {args.days_back}")
        if not args.no_notion:
            print(f"   Saved to Notion: ✅")
        else:
            print(f"   Saved to Notion: ❌ (skipped)")
            
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()