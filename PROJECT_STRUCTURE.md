# Project Structure

## Directory Layout

```
Canoe-DC/
├── .git/                    # Git repository data
├── .claude/                 # Claude IDE configuration
├── clients/                 # API client modules
│   ├── __pycache__/        # Python cache (gitignored)
│   ├── canoe_client.py     # Canoe API integration
│   ├── claude_client.py    # Claude AI integration
│   ├── google_sheets_client.py  # Google Sheets integration
│   └── notion_client.py    # Notion API integration
├── config/                  # Configuration files
│   └── document_filters.json  # Document filter presets
├── data/                    # Data storage (gitignored)
│   ├── progress/           # Progress tracking files
│   │   ├── session_*.json  # Session progress files
│   │   └── failed_documents.json  # Failed documents log
│   └── temp_pdfs/          # Temporary PDF storage
├── docs/                    # Documentation
│   ├── API_DOCUMENTATION.md
│   └── GOOGLE_SHEETS_SETUP.md
├── logs/                    # Application logs (gitignored)
│   └── pdf_summarizer.log
├── prompts/                 # AI prompt templates
│   └── claude_summary_prompt.txt
├── src/                     # Main application code
│   ├── __pycache__/        # Python cache (gitignored)
│   ├── bulk.py             # Bulk document processor
│   ├── config.py           # Configuration management
│   └── single.py           # Single document processor
├── tests/                   # Test files
│   ├── test.py             # Legacy test file
│   ├── test_bitwarden.py   # Bitwarden integration tests
│   ├── test_document_filters.py  # Filter system tests
│   ├── test_pdf_extraction.py    # PDF processing tests
│   ├── test_progress_tracker.py  # Progress tracking tests
│   ├── test_security_fixes.py    # Security tests
│   ├── test_sheets_config.py     # Google Sheets tests
│   └── test_document_id.text     # Test document ID
├── utils/                   # Utility modules
│   ├── __pycache__/        # Python cache (gitignored)
│   ├── logger.py           # Logging configuration
│   └── progress_tracker.py # Progress tracking system
├── .env                    # Environment variables (gitignored)
├── .gitattributes         # Git attributes
├── .gitignore             # Git ignore rules
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── CLAUDE.md              # Claude Code instructions
├── PROJECT_STRUCTURE.md  # This file
├── README.md              # Project documentation
└── requirements.txt       # Python dependencies
```

## Key Directories

### `/clients`
Contains all external API client implementations. Each client is responsible for integrating with a specific service.

### `/src`
Main application entry points and core configuration. The `bulk.py` and `single.py` scripts are the primary user interfaces.

### `/config`
Stores configuration files like document filter presets. These are version-controlled settings.

### `/data`
Runtime data storage including progress tracking and temporary files. This directory is gitignored except for the structure.

### `/tests`
All test files are consolidated here for easy testing and maintenance.

### `/utils`
Shared utility modules used across the application.

### `/prompts`
AI prompt templates used by the Claude client for generating summaries.

### `/docs`
Project documentation including setup guides and API documentation.

### `/logs`
Application logs are stored here. This directory is gitignored but the structure is maintained.

## Files Not in Version Control

The following are excluded via `.gitignore`:
- `.env` - Environment variables and secrets
- `/data/` contents - Runtime data and progress files
- `/logs/` contents - Application logs
- `__pycache__/` directories - Python bytecode
- `*.pyc` files - Compiled Python files

## Development Workflow

1. **Main Scripts**: Run `python src/bulk.py` or `python src/single.py`
2. **Testing**: Run tests from project root: `python tests/test_*.py`
3. **Configuration**: Edit `config/document_filters.json` for filter presets
4. **Credentials**: Use Bitwarden or `.env` file for API credentials
5. **Logs**: Check `logs/pdf_summarizer.log` for debugging
6. **Progress**: Monitor `data/progress/` for processing status