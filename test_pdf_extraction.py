#!/usr/bin/env python3
"""
Test script to verify enhanced PDF extraction
Compares old vs new extraction methods
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clients.canoe_client import CanoeClient
from clients.claude_client import ClaudeClient
from loguru import logger
from utils.logger import setup_logging

def test_extraction():
    """Test PDF extraction with a sample document"""
    setup_logging()
    
    # Check if test document ID is provided
    test_doc_id = input("Enter a document ID to test extraction (or press Enter to skip): ").strip()
    
    if not test_doc_id:
        logger.info("No document ID provided. Please run with a valid document ID to test.")
        return
    
    try:
        logger.info("🔬 Testing enhanced PDF extraction...")
        
        # Initialize clients
        canoe = CanoeClient()
        claude = ClaudeClient()
        
        # Download PDF
        logger.info(f"📥 Downloading document {test_doc_id}...")
        pdf_data, pdf_name = canoe.download_document(test_doc_id)
        logger.success(f"✅ Downloaded: {pdf_name}")
        
        # Extract text using enhanced method
        logger.info("📄 Extracting text with enhanced method...")
        extracted_text = claude._extract_text_from_pdf(pdf_data)
        
        # Show sample of extracted text
        logger.info("📊 Extraction Results:")
        print("\n" + "="*60)
        print("EXTRACTED TEXT SAMPLE (First 2000 characters):")
        print("="*60)
        print(extracted_text[:2000])
        print("="*60)
        
        # Show statistics
        total_chars = len(extracted_text)
        total_lines = extracted_text.count('\n')
        total_words = len(extracted_text.split())
        
        print(f"\n📈 Statistics:")
        print(f"   Total characters: {total_chars:,}")
        print(f"   Total lines: {total_lines:,}")
        print(f"   Total words: {total_words:,}")
        print(f"   Average words per line: {total_words/max(total_lines, 1):.1f}")
        
        # Test Claude summarization with enhanced text
        logger.info("\n🤖 Testing Claude summarization with enhanced text...")
        doc_info = {'id': test_doc_id, 'name': pdf_name}
        summary = claude.summarize_pdf(pdf_data, doc_info)
        
        print("\n" + "="*60)
        print("CLAUDE SUMMARY:")
        print("="*60)
        print(summary)
        print("="*60)
        
        logger.success("✅ Enhanced PDF extraction test complete!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_extraction()