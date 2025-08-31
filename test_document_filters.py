#!/usr/bin/env python3
"""
Test Document Filtering System
Tests the new preset-based filtering without processing documents
"""

import sys
import os
from loguru import logger

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from clients.canoe_client import CanoeClient
from utils.logger import setup_logging

def test_filter_system():
    """Test the new document filtering system"""
    setup_logging()
    
    print("="*60)
    print("DOCUMENT FILTERING SYSTEM TEST")
    print("="*60)
    
    try:
        # Initialize Canoe client
        logger.info("📡 Initializing Canoe client...")
        canoe = CanoeClient()
        logger.success("✅ Canoe client initialized")
        
        # Test 1: List available presets
        print("\n1. 📋 Testing Preset Loading...")
        config_data = canoe.load_filter_presets()
        presets = config_data.get('presets', {})
        
        print(f"   Found {len(presets)} presets:")
        for preset_name, preset_config in presets.items():
            print(f"   - {preset_name}: {preset_config.get('name', 'N/A')}")
        
        # Test 2: Test auto-date calculation  
        print("\n2. 📅 Testing Auto-Date Calculation...")
        test_dates = ['auto:7d', 'auto:30d', 'auto:1y', 'auto:6m']
        
        for auto_date in test_dates:
            calculated = canoe._calculate_auto_date(auto_date)
            print(f"   {auto_date} → {calculated}")
        
        # Test 3: Test filter config processing
        print("\n3. ⚙️  Testing Filter Config Processing...")
        
        test_config = {
            'name': 'Test Config',
            'description': 'This should be ignored',
            'document_type': 'Quarterly Report',
            'file_upload_time_start': 'auto:30d',
            'data_date_start': '2024-01-01',
            'fields': 'id,name,document_type'
        }
        
        processed = canoe._process_filter_config(test_config)
        print(f"   Original config: {test_config}")
        print(f"   Processed params: {processed}")
        
        # Test 4: Test preset retrieval (without actual API call)
        print("\n4. 🎯 Testing Preset Selection...")
        
        available_presets = list(presets.keys())
        if available_presets:
            test_preset = available_presets[0]
            print(f"   Testing preset: {test_preset}")
            
            preset_config = presets[test_preset].copy()
            processed_preset = canoe._process_filter_config(preset_config)
            print(f"   Preset config: {preset_config}")
            print(f"   Processed params: {processed_preset}")
        
        # Test 5: Test with overrides
        print("\n5. 🔧 Testing Parameter Overrides...")
        
        if available_presets:
            overrides = {
                'document_type': 'Annual Report',
                'data_date_start': '2024-06-01'
            }
            
            base_config = presets[test_preset].copy()
            base_config.update(overrides)
            processed_override = canoe._process_filter_config(base_config)
            
            print(f"   Base preset: {test_preset}")
            print(f"   Overrides: {overrides}")
            print(f"   Final params: {processed_override}")
        
        print("\n" + "="*60)
        print("✅ FILTER SYSTEM TEST COMPLETED SUCCESSFULLY")
        print("="*60)
        
        print("\n💡 Ready to test with actual API calls:")
        print("   - python src/bulk.py --list-presets")
        print("   - python src/bulk.py --preset quarterly_reports --no-notion")
        print("   - python src/bulk.py --preset annual_reports_2024 --document-type 'Quarterly Report'")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_filter_system()