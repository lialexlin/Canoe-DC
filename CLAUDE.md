# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Automated PDF document processing workflow that downloads PDFs from Canoe, summarizes them with Claude AI, and saves summaries to Notion and Google Sheets. Enhanced with flexible filtering, security improvements, and dual storage options.

## Development Commands
- **Install dependencies**: `pip install -r requirements.txt`
- **Format code**: `black .`
- **Lint code**: `flake8 .`
- **Pre-commit hooks**: `pre-commit run --all-files` (install with `pre-commit install`)
- **Run single document**: `python src/single.py --document-id DOCUMENT_ID`
- **Run bulk processing**: `python src/bulk.py --preset quarterly_reports --google-sheets`
- **List filter presets**: `python src/bulk.py --list-presets`

## Architecture Overview

**Client-Based Design**: Four independent API clients handle external services:
- `CanoeClient`: Downloads PDFs, OAuth token management, configurable filtering with presets
- `ClaudeClient`: Enhanced PDF text extraction (PyMuPDF blocks) + Claude API summarization  
- `NotionClient`: Creates structured pages in Notion database
- `GoogleSheetsClient`: Spreadsheet integration with rate limiting and auto-formatting

**Configuration System**: `src/config.py` implements secure dual-source credential management:
1. **Primary**: Bitwarden CLI with `BitwardenConfig` class (SECURITY ENHANCED)
2. **Fallback**: Environment variables via `.env` file
3. **Bitwarden Folder Structure**: All items in `Axiom` folder
   - `Canoe`: Username=client_id, Password=client_secret, URI=base_url
   - `Claude`: Password=api_key
   - `Notion`: Password=token, Notes=database_id
   - `GoogleSheets`: credentials_json, spreadsheet_id, user_email

**Processing Flow**:
1. **Single**: `src/single.py` → Download specific document ID → Summarize → Save to Notion/Sheets
2. **Bulk**: `src/bulk.py` → Query using presets/filters → Process each → Dual storage
3. **Configurable Filtering**: 8 presets + custom parameters (document_type, data_date ranges, etc.)

## Key Technical Details

**Security Enhancements**: 
- Bitwarden password handling via stdin (no CLI args exposure)
- Session token validation with timeout protection
- Secure logging (credentials never logged, even in debug)
- Input validation and sanitization across all clients

**Error Handling**: 3-attempt retry with exponential backoff, 180-second PDF timeouts, comprehensive validation.

**PDF Processing**: Enhanced PyMuPDF with structured blocks extraction, intelligent section detection, text cleaning.

**Claude Integration**: 
- Model: `claude-3-5-sonnet-20241022`
- Focus: Macroeconomic analysis from quarterly reports
- Content limit: 10,000 characters, Output: 200 words max
- Enhanced text preprocessing for better accuracy

**Document Filtering**: Flexible preset system supporting all Canoe API parameters
- Auto-date calculation: `auto:30d`, `auto:1y`, etc.
- Available presets: quarterly_reports, annual_reports_2024, capital_calls_recent, etc.
- Command-line overrides: `--document-type`, `--data-date-start`, `--data-date-end`

**Google Sheets Integration**:
- Auto-formatting with headers and column sizing
- Rate limiting and API quota protection  
- Input validation and length limits
- Batch operations for efficiency

## Usage Examples

### Basic Usage
```bash
# List available filter presets
python src/bulk.py --list-presets

# Use preset with Google Sheets
python src/bulk.py --preset quarterly_reports --google-sheets

# Process single document to both storages
python src/single.py --document-id DOC_ID --google-sheets

# Override preset parameters
python src/bulk.py --preset annual_reports_2024 --data-date-start 2024-07-01
```

### Advanced Filtering
```bash
# Multiple document types
python src/bulk.py --preset multi_type_recent --document-type "Annual Report,Capital Call Notice"

# Custom date ranges
python src/bulk.py --preset custom_date_range --data-date-start 2024-01-01 --data-date-end 2024-06-30

# Google Sheets only
python src/bulk.py --preset quarterly_reports --sheets-only
```

## Bitwarden Setup Requirements
Items in the `Axiom` folder (configurable via `BW_FOLDER`):
- **Canoe**: Username=client_id, Password=client_secret, URI=base_url
- **Claude**: Password=api_key
- **Notion**: Password=token, Notes/Custom Field=database_id
- **GoogleSheets**: Password/Custom Field=credentials_json, Custom Field=spreadsheet_id

Required environment variables for session management:
```bash
export BW_SESSION="session-key-after-bw-unlock"
export BW_PASSWORD="master-password"  # Optional auto-unlock
export BW_FOLDER="Axiom"  # Optional custom folder
```

## Code Standards
- **Black formatter**: 88 character line length
- **Flake8**: Extended ignore for E203
- **Import organization**: Standard library, third-party, local imports
- **Constants**: Named constants instead of magic numbers
- **Security**: No credential logging, secure session handling
- **Error logging**: Use logger with appropriate level (info/warning/error/success)

## Testing & Validation
Available test utilities:
- `test_bitwarden.py` - Validate Bitwarden integration
- `test_pdf_extraction.py` - Test enhanced PDF processing
- `test_document_filters.py` - Validate filtering system
- `test_security_fixes.py` - Verify security improvements

## Working Preferences
When implementing features:
1. **Propose 3 implementation options** with pros/cons and complexity levels
2. **Use non-technical language** - user has no coding experience
3. **Follow existing patterns**: Client-based architecture, Bitwarden for secrets, structured logging
4. **Security first**: Validate inputs, secure credential handling, rate limiting
5. **Allow user choice** before implementing
6. **This is an MVP** - prioritize working functionality over perfect code

## Recent Major Enhancements
- **Security overhaul**: Bitwarden integration with secure session management
- **Enhanced PDF processing**: Structured text extraction with intelligent cleaning
- **Flexible filtering**: Preset-based document queries with auto-date support
- **Google Sheets integration**: Professional spreadsheet output with formatting
- **Dual storage**: Simultaneous Notion and Sheets saving
- **Comprehensive testing**: Security validation and integration tests