#!/usr/bin/env python3
"""
Main entry point for Canoe-DC Document Processor
Provides a simple interface to run bulk or single document processing
"""
import sys
import os

def main():
    """Display available commands and usage"""
    print("\n" + "="*60)
    print("CANOE-DC DOCUMENT PROCESSOR")
    print("="*60)
    print("\nAvailable Commands:")
    print("-"*40)
    
    print("\n1. BULK PROCESSING:")
    print("   python src/bulk.py --preset quarterly_reports --google-sheets")
    print("   python src/bulk.py --list-presets")
    print("   python src/bulk.py --resume latest --google-sheets")
    print("   python src/bulk.py --retry-failed --google-sheets")
    
    print("\n2. SINGLE DOCUMENT:")
    print("   python src/single.py --document-id DOC_ID --google-sheets")
    
    print("\n3. TESTING:")
    print("   python tests/test_sheets_config.py  # Test Google Sheets")
    print("   python tests/test_bitwarden.py      # Test Bitwarden")
    
    print("\n4. HELP:")
    print("   python src/bulk.py --help")
    print("   python src/single.py --help")
    
    print("\n" + "="*60)
    print("For detailed documentation, see README.md")
    print("For project structure, see PROJECT_STRUCTURE.md")
    print("="*60 + "\n")
    
    # If arguments provided, suggest running the appropriate script
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if 'bulk' in arg:
            print("💡 To run bulk processing, use:")
            print("   python src/bulk.py [options]")
        elif 'single' in arg:
            print("💡 To process a single document, use:")
            print("   python src/single.py --document-id DOC_ID [options]")
        elif 'test' in arg:
            print("💡 Available tests in tests/ directory:")
            tests_dir = os.path.join(os.path.dirname(__file__), 'tests')
            for file in os.listdir(tests_dir):
                if file.startswith('test_') and file.endswith('.py'):
                    print(f"   python tests/{file}")

if __name__ == "__main__":
    main()