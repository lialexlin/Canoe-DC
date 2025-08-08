#!/usr/bin/env python3
"""
PDF Summarizer - Main Script
Downloads PDFs from Canoe, summarizes with Claude, saves to Notion
"""

import os
import sys
from datetime import datetime
from loguru import logger

from clients.canoe_client import CanoeClient
from clients.claude_client import ClaudeClient
from clients.notion_client import NotionClient
from utils.logger import setup_logging
import config

def main():
    """Main execution function"""
    setup_logging()
    logger.info("🚀 Starting PDF Summarizer")
    
    try:
        # Initialize clients
        logger.info("📡 Initializing API clients...")
        canoe = CanoeClient()
        claude = ClaudeClient()
        notion = NotionClient()
        
        # Step 1: Process specific document
        try:
            # Process document (uses default test document ID)
            pdf_data, doc_info = canoe.process_specific_document()
            
            # Generate summary
            summary = claude.summarize_pdf(pdf_data, doc_info)
            
            # Save to Notion
            notion.create_summary_page(doc_info, summary)
            
            logger.success(f"✅ Successfully processed {doc_info['id']}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process document: {e}")
        
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()