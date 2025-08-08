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
        document_id = "519fbe4d-1651-4096-a9c5-75d40e0f991a"
        logger.info(f"📄 Processing specific document: {document_id}")
        
        try:
            # Download PDF
            pdf_data = canoe.download_pdf(document_id)
            
            # Create mock doc_info for compatibility with existing functions
            doc_info = {"id": document_id, "name": "Specific Document"}
            
            # Generate summary
            summary = claude.summarize_pdf(pdf_data, doc_info)
            
            # Save to Notion
            notion.create_summary_page(doc_info, summary)
            
            logger.success(f"✅ Successfully processed {document_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process {document_id}: {e}")
        
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()