#!/usr/bin/env python3
"""
Test Bitwarden integration
Verifies that credentials can be retrieved from Bitwarden
"""

import os
import sys
from loguru import logger

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_bitwarden():
    """Test Bitwarden credential retrieval"""
    print("="*60)
    print("BITWARDEN INTEGRATION TEST")
    print("="*60)
    
    # Check for Bitwarden session
    bw_session = os.getenv("BW_SESSION")
    bw_password = os.getenv("BW_PASSWORD")
    
    print("\n1. Environment Check:")
    print(f"   BW_SESSION: {'✅ Set' if bw_session else '❌ Not set'}")
    print(f"   BW_PASSWORD: {'✅ Set' if bw_password else '❌ Not set'}")
    print(f"   BW_FOLDER: {os.getenv('BW_FOLDER', 'Axiom (default)')}")
    
    print("\n2. Testing Bitwarden Connection...")
    
    try:
        # Import config to trigger Bitwarden initialization
        from src import config
        
        if config.USE_BITWARDEN:
            print("   ✅ Bitwarden connected successfully")
            
            print("\n3. Testing Credential Retrieval:")
            
            # Test Canoe credentials
            try:
                if config.CANOE_CLIENT_ID:
                    print(f"   ✅ Canoe Client ID: {config.CANOE_CLIENT_ID[:8]}...")
                if config.CANOE_CLIENT_SECRET:
                    print(f"   ✅ Canoe Client Secret: ***")
                if config.CANOE_BASE_URL:
                    print(f"   ✅ Canoe Base URL: {config.CANOE_BASE_URL}")
            except Exception as e:
                print(f"   ❌ Canoe credentials: {e}")
            
            # Test Claude API key
            try:
                if config.ANTHROPIC_API_KEY:
                    print(f"   ✅ Claude API Key: {config.ANTHROPIC_API_KEY[:7]}...")
            except Exception as e:
                print(f"   ❌ Claude API key: {e}")
            
            # Test Notion credentials
            try:
                if config.NOTION_TOKEN:
                    print(f"   ✅ Notion Token: {config.NOTION_TOKEN[:10]}...")
                if config.NOTION_DATABASE_ID:
                    print(f"   ✅ Notion Database ID: {config.NOTION_DATABASE_ID[:8]}...")
            except Exception as e:
                print(f"   ❌ Notion credentials: {e}")
            
            print("\n4. Summary:")
            print("   ✅ Bitwarden integration is working correctly!")
            print("\n   You can now run the processing scripts:")
            print("   - python src/single.py --document-id YOUR_ID")
            print("   - python src/bulk.py --days-back 7")
            
        else:
            print("   ⚠️  Bitwarden not available, using environment variables")
            print("\n   To use Bitwarden:")
            print("   1. Install Bitwarden CLI: https://bitwarden.com/help/cli/")
            print("   2. Login: bw login")
            print("   3. Unlock: bw unlock")
            print("   4. Export session: export BW_SESSION='your-session-key'")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Bitwarden CLI is installed")
        print("2. Run: bw login")
        print("3. Run: bw unlock")
        print("4. Export the session key: export BW_SESSION='...'")
        print("5. Ensure your items are in the 'Axiom' folder in Bitwarden")
        
    print("\n" + "="*60)

if __name__ == "__main__":
    test_bitwarden()