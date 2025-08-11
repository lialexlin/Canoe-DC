# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Automated PDF document processing workflow that downloads PDFs from Canoe, summarizes them with Claude AI, and saves summaries to Notion. This is an MVP designed to demonstrate workflow feasibility.

## Development Commands
- **Install dependencies**: `pip install -r requirements.txt`
- **Format code**: `black .`
- **Lint code**: `flake8 .`
- **Pre-commit hooks**: `pre-commit run --all-files` (install with `pre-commit install`)
- **Run single document**: `python single_process.py --document-id DOCUMENT_ID`
- **Run bulk processing**: `python bulk_process.py --days-back 7`
- **Main script** (legacy): `python main.py`

## Architecture Overview

**Client-Based Design**: Three independent API clients handle external services:
- `CanoeClient`: Downloads PDFs, handles OAuth token management with retry logic
- `ClaudeClient`: PDF text extraction (PyMuPDF) + Claude API summarization  
- `NotionClient`: Creates structured pages in Notion database

**Configuration System**: `config.py` implements dual-source credential management:
1. **Primary**: 1Password CLI with `OnePasswordConfig` class
2. **Fallback**: Environment variables via `.env` file
3. **Vault Items Required**: `canoe-api`, `anthropic-api`, `notion-integration`

**Processing Flow**:
1. **Single**: `single_process.py` → Download specific document ID → Summarize → Save to Notion
2. **Bulk**: `bulk_process.py` → Query recent quarterly reports → Process each → Batch save
3. **Main**: `main.py` → Legacy single document processor (hardcoded test ID)

## Key Technical Details

**Error Handling**: API clients implement 3-attempt retry with exponential backoff (1s, 2s delays). 180-second timeout for large PDF downloads.

**Logging**: Loguru configuration in `utils/logger.py` with dual output (console + rotating file logs in `logs/` directory).

**PDF Processing**: Uses PyMuPDF (`fitz`) for text extraction with page-by-page processing and formatting preservation.

**Claude Integration**: 
- Model: `claude-3-5-sonnet-20241022`
- Focus: Macroeconomic analysis from quarterly reports
- Content limit: 10,000 characters
- Output limit: 200 words executive summary

## 1Password Setup Requirements
The application requires three vault items with specific field names:
- `canoe-api`: `client_id`, `client_secret`, `base_url`
- `anthropic-api`: `api_key` 
- `notion-integration`: `token`, `database_id`

Default vault: "Canoe workflow" (configurable via `OP_VAULT` environment variable).

## Code Standards
- **Black formatter**: 88 character line length
- **Flake8**: Extended ignore for E203
- **Import organization**: Standard library, third-party, local imports
- **Error logging**: Use logger with appropriate level (info/warning/error/success)

## Working Preferences
When implementing features:
1. **Propose 3 implementation options** with pros/cons and complexity levels
2. **Use non-technical language** - user has no coding experience
3. **Follow existing patterns**: Client-based architecture, 1Password for secrets, structured logging
4. **Allow user choice** before implementing
5. **This is an MVP** - prioritize working functionality over perfect code