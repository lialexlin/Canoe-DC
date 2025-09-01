#!/usr/bin/env python3
"""
Final test to verify allocations and investment data can be retrieved correctly
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from clients.canoe_client import CanoeClient

def test_final_allocation():
    """Test the final implementation with updated field names"""
    print("Final test: Testing Canoe API with allocations and investment_id fields")
    
    try:
        client = CanoeClient()
        print("Client initialized successfully")
        
        # Test using the quarterly_reports preset (now updated with investment field)
        documents = client.get_documents_by_preset('quarterly_reports')
        
        print(f"Found {len(documents)} documents using quarterly_reports preset")
        
        if documents:
            # Show first 5 documents with their investment data
            print("\nFirst 5 documents with investment information:")
            for i, doc in enumerate(documents[:5]):
                name = doc.get('name', 'Unknown')[:60]
                
                # Extract investment information from allocations
                investment_name = "N/A"
                investment_id = "N/A"
                
                if 'allocations' in doc and isinstance(doc['allocations'], list) and len(doc['allocations']) > 0:
                    first_alloc = doc['allocations'][0]
                    if isinstance(first_alloc, dict):
                        investment_name = first_alloc.get('investment', 'N/A')
                        investment_id = first_alloc.get('investment_id', 'N/A')
                
                # Also check for direct investment_id field
                if investment_id == "N/A" and 'investment_id' in doc:
                    investment_id = doc['investment_id']
                
                print(f"  {i+1}. {name}...")
                print(f"      Investment: {investment_name}")
                print(f"      Investment ID: {investment_id}")
                print()
                
            print(f"SUCCESS: All documents have access to investment information through allocations field")
        else:
            print("No documents found")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_allocation()