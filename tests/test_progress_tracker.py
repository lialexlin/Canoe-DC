#!/usr/bin/env python3
"""
Test script for Progress Tracker functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.progress_tracker import ProgressTracker
from loguru import logger

def test_progress_tracker():
    """Test the progress tracker with mock documents"""
    logger.info("🧪 Testing Progress Tracker...")
    
    # Create test documents
    test_documents = [
        {"id": "DOC001", "name": "Q3 2024 Report - Fund A", "document_type": "Quarterly Report"},
        {"id": "DOC002", "name": "Q3 2024 Report - Fund B", "document_type": "Quarterly Report"},
        {"id": "DOC003", "name": "Q3 2024 Report - Fund C", "document_type": "Quarterly Report"},
        {"id": "DOC004", "name": "Annual Report 2024", "document_type": "Annual Report"},
        {"id": "DOC005", "name": "Capital Call Notice", "document_type": "Capital Call"},
    ]
    
    # Initialize tracker
    tracker = ProgressTracker("test_session")
    tracker.initialize_documents(test_documents)
    
    # Simulate processing documents
    for i, doc in enumerate(test_documents):
        tracker.mark_processing(doc['id'], doc['name'])
        
        # Simulate success for first 3, failure for 4th, success for 5th
        if i == 3:
            tracker.mark_failed(doc['id'], doc['name'], "Simulated download error")
        else:
            tracker.mark_completed(doc['id'], doc['name'], f"Summary for {doc['name']}")
    
    # Generate report
    report = tracker.generate_summary_report()
    print(report)
    
    # Test loading session
    logger.info("\n🔄 Testing session resume...")
    new_tracker = ProgressTracker()
    if new_tracker.load_session("test_session.json"):
        logger.success("✅ Session loaded successfully")
        logger.info(f"   Processed: {new_tracker.progress_data['processed_count']}")
        logger.info(f"   Failed: {new_tracker.progress_data['failed_count']}")
        logger.info(f"   Remaining: {len(new_tracker.get_remaining_documents())}")
    
    # Test failed documents
    logger.info("\n❌ Testing failed documents retrieval...")
    failed_docs = ProgressTracker.load_failed_documents()
    if failed_docs:
        logger.info(f"Found {len(failed_docs)} failed documents:")
        for doc in failed_docs:
            logger.info(f"   - {doc['name']}: {doc['error']}")
    
    logger.success("\n✅ Progress Tracker test completed!")

if __name__ == "__main__":
    test_progress_tracker()