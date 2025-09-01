#!/usr/bin/env python3
"""
Test script to verify allocation.investment field can be retrieved from Canoe API
"""
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.canoe_client import CanoeClient

def test_allocation_field():
    """Test if we can retrieve allocation.investment field"""
    print("Initializing Canoe client...")
    
    try:
        client = CanoeClient()
        print("Client initialized successfully")
        
        # Test with various allocation-related field names
        filter_config = {
            'document_type': 'Quarterly Report',
            'data_date_start': '2025-01-01',
            'data_date_end': '2025-03-31',
            'fields': 'id,name,document_type,data_date,fund_id,fund_sponsor,allocations,allocation,allocation_investment,investment,investment_entity_id,investment_id,investment_name'
        }
        
        print(f"Testing API call with filter: {filter_config}")
        
        documents = client.get_documents_by_filter(filter_config)
        
        print(f"Found {len(documents)} documents")
        
        if documents:
            # Show first document with all fields
            first_doc = documents[0]
            print("\nFirst document fields:")
            for key, value in first_doc.items():
                print(f"  {key}: {value}")
            
            # Check different allocation field structures
            print("\nChecking allocation fields:")
            
            # Check for singular 'allocation' field
            if 'allocation' in first_doc:
                print(f"allocation field found: {first_doc['allocation']}")
                if isinstance(first_doc['allocation'], dict) and 'investment' in first_doc['allocation']:
                    print(f"allocation.investment field found: {first_doc['allocation']['investment']}")
                else:
                    print("allocation.investment field not found in allocation object")
            else:
                print("allocation field not found")
                
            # Check for plural 'allocations' field
            if 'allocations' in first_doc:
                print(f"allocations field found: {first_doc['allocations']}")
                if isinstance(first_doc['allocations'], list) and len(first_doc['allocations']) > 0:
                    first_allocation = first_doc['allocations'][0]
                    print(f"first allocation object: {first_allocation}")
                    if isinstance(first_allocation, dict) and 'investment' in first_allocation:
                        print(f"investment field in allocations[0]: {first_allocation['investment']}")
                    else:
                        print("investment field not found in allocations[0]")
            else:
                print("allocations field not found")
                
            # Check for investment-related fields
            investment_fields = ['investment', 'investment_entity_id', 'investment_id', 'investment_name', 'allocation_investment']
            for field in investment_fields:
                if field in first_doc:
                    print(f"{field} field found: {first_doc[field]}")
                    
            # Show first 3 documents allocation info:
            print(f"\nFirst 3 documents investment info:")
            for i, doc in enumerate(documents[:3]):
                allocation_info = "N/A"
                
                # Check for any investment-related fields  
                for field in investment_fields:
                    if field in doc:
                        allocation_info = f"{field}: {doc[field]}"
                        break
                
                # Check allocations array for investment data
                if allocation_info == "N/A" and 'allocations' in doc and isinstance(doc['allocations'], list) and len(doc['allocations']) > 0:
                    first_alloc = doc['allocations'][0]
                    if isinstance(first_alloc, dict):
                        for field in ['investment', 'investment_id', 'investment_name']:
                            if field in first_alloc:
                                allocation_info = f"allocations[0].{field}: {first_alloc[field]}"
                                break
                        if allocation_info == "N/A":
                            allocation_info = f"allocations[0] keys: {list(first_alloc.keys())}"
                
                print(f"  {i+1}. {doc.get('name', 'Unknown')[:50]}... | investment data: {allocation_info}")
        else:
            print("No documents found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_allocation_field()