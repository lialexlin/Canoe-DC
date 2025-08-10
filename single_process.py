#!/usr/bin/env python3
"""
Single Document Processor
Downloads and processes a specific document by ID with Claude summary
"""

import argparse
import sys
from loguru import logger

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
    parser.add_argument('--save-pdf', type=str,
                       help='Save PDF to specified file path')
    
    args = parser.parse_args()
    
    setup_logging()
    logger.info("🚀 Starting Single Document Processor")
    
    try:
        # Initialize clients
        logger.info("📡 Initializing API clients...")
        canoe = CanoeClient()
        
        if not args.no_summary:
            claude = ClaudeClient()
        
        if not args.no_notion and not args.no_summary:
            notion = NotionClient()
        
        # Download document
        if not args.document_id:
            logger.error("❌ Document ID is required. Use --document-id to specify which document to process.")
            sys.exit(1)
            
        logger.info(f"📄 Processing document ID: {args.document_id}")
        
        # Step 1: Download PDF and get document name
        logger.info("   ⬇️  Downloading PDF and getting document name...")
        pdf_data, pdf_name = canoe.download_document(args.document_id)
        logger.success(f"   ✅ Downloaded: {pdf_name}")
        
        # Create document info
        doc_info = {
            'id': args.document_id,
            'name': pdf_name
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
            print(f"\n📋 Document Summary:")
            print(f"   Document: {doc_info['name']}")
            print(f"   ID: {doc_info['id']}")
            print(f"\n📝 Summary:\n{summary}\n")
        
        # Save to Notion if enabled
        if not args.no_notion and not args.no_summary and summary:
            logger.info("💾 Saving summary to Notion...")
            notion.create_summary_page(doc_info, summary)
            logger.success("✅ Summary saved to Notion")
        
        logger.success(f"🎉 Successfully processed document: {doc_info['name']}")
        
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()