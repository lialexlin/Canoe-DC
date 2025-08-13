#!/usr/bin/env python3
"""
Test Documents Processor
Processes all document IDs from test_document_id.text with Claude summaries
"""

import argparse
import sys
from loguru import logger

from clients.canoe_client import CanoeClient
from clients.claude_client import ClaudeClient
from clients.notion_client import NotionClient
from utils.logger import setup_logging


def read_document_ids(file_path):
    """Read and parse document IDs from test file"""
    document_ids = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Extract document ID (everything before # comment)
                    doc_id = line.split('#')[0].strip()
                    if doc_id:
                        document_ids.append(doc_id)
        return document_ids
    except FileNotFoundError:
        logger.error(f"❌ Test document file not found: {file_path}")
        return []
    except Exception as e:
        logger.error(f"❌ Error reading document IDs: {e}")
        return []


def process_single_document(canoe, claude, notion, document_id, index, total, skip_notion=False):
    """Process a single document with error handling"""
    try:
        logger.info(f"📄 [{index}/{total}] Processing document ID: {document_id}")
        
        # Step 1: Download PDF and get document name
        logger.info("   ⬇️  Downloading PDF and getting document name...")
        pdf_data, pdf_name = canoe.download_document(document_id)
        logger.success(f"   ✅ Downloaded: {pdf_name}")
        
        # Create document info
        doc_info = {
            'id': document_id,
            'name': pdf_name
        }
        
        # Step 2: Generate summary with Claude
        logger.info("   🤖 Generating Claude summary...")
        summary = claude.summarize_pdf(pdf_data, doc_info)
        logger.success("   ✅ Summary generated")
        
        # Step 3: Save to Notion (if enabled)
        if not skip_notion:
            logger.info("   💾 Saving to Notion...")
            notion.create_summary_page(doc_info, summary)
            logger.success("   ✅ Saved to Notion")
        
        logger.success(f"✅ [{index}/{total}] Completed: {pdf_name}")
        return True
        
    except Exception as e:
        logger.error(f"❌ [{index}/{total}] Failed to process {document_id}: {e}")
        return False


def main():
    """Main execution function for test documents processing"""
    parser = argparse.ArgumentParser(description='Process test documents with Claude summaries')
    parser.add_argument('--no-notion', action='store_true',
                       help='Skip saving summaries to Notion')
    parser.add_argument('--test-file', type=str, default='test_document_id.text',
                       help='Path to test document IDs file (default: test_document_id.text)')
    
    args = parser.parse_args()
    
    setup_logging()
    logger.info("🚀 Starting Test Documents Processor")
    
    try:
        # Read document IDs from test file
        logger.info(f"📋 Reading document IDs from {args.test_file}...")
        document_ids = read_document_ids(args.test_file)
        
        if not document_ids:
            logger.error("❌ No document IDs found to process")
            sys.exit(1)
        
        logger.info(f"📊 Found {len(document_ids)} documents to process")
        for i, doc_id in enumerate(document_ids, 1):
            logger.info(f"   {i}. {doc_id}")
        
        # Initialize clients
        logger.info("📡 Initializing API clients...")
        canoe = CanoeClient()
        claude = ClaudeClient()
        
        if not args.no_notion:
            notion = NotionClient()
        else:
            notion = None
        
        # Process each document
        processed_count = 0
        total_docs = len(document_ids)
        
        for i, document_id in enumerate(document_ids, 1):
            success = process_single_document(
                canoe, claude, notion, document_id, i, total_docs, args.no_notion
            )
            if success:
                processed_count += 1
        
        # Final summary
        logger.success(f"🎉 Processing complete!")
        print(f"\nProcessing Summary:")
        print(f"   Documents found: {total_docs}")
        print(f"   Documents processed: {processed_count}")
        print(f"   Success rate: {processed_count}/{total_docs}")
        if not args.no_notion:
            print(f"   Saved to Notion: Yes")
        else:
            print(f"   Saved to Notion: No (skipped)")
        
        if processed_count < total_docs:
            logger.warning(f"⚠️  {total_docs - processed_count} documents failed to process")
            
    except Exception as e:
        logger.error(f"💥 Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()