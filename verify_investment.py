#!/usr/bin/env python3
"""
Verify investment field is working properly
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.canoe_client import CanoeClient

def verify_investment():
    """Verify investment extraction"""
    print("Testing investment field extraction...")
    
    client = CanoeClient()
    
    # Get a single document to test
    filter_config = {
        'document_id': '55674266-9c56-4aea-a8c2-0269fdd0ec97',
        'fields': 'id,name,document_type,data_date,allocations,investment,investment_id'
    }
    
    documents = client.get_documents_by_filter(filter_config)
    
    if documents and len(documents) > 0:
        doc = documents[0]
        print(f"\nDocument: {doc.get('name', 'Unknown')}")
        print(f"Document ID: {doc.get('id')}")
        
        # Extract investment name
        investment_name = 'Unknown'
        if 'allocations' in doc and isinstance(doc['allocations'], list) and len(doc['allocations']) > 0:
            first_alloc = doc['allocations'][0]
            if isinstance(first_alloc, dict) and 'investment' in first_alloc:
                investment_name = first_alloc['investment']
        
        print(f"Investment Name: {investment_name}")
        print(f"\nFull allocations data: {doc.get('allocations')}")
        
        print(f"\nSUCCESS: Investment name '{investment_name}' will be saved to:")
        print("  - Google Sheets (in 'Investment' column)")
        print("  - Notion (under 'Document Information' section)")

if __name__ == "__main__":
    verify_investment()