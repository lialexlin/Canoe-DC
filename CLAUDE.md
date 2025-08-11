# CLAUDE.md - Project Context

## Project Overview
- **Purpose**: Automated PDF document processing workflow that downloads PDFs from Canoe, summarizes them with Claude AI, and saves summaries to Notion
- **Key technologies**: Python 3.11+, 1Password CLI, Anthropic Claude API, Notion API, Canoe API
- **Architecture**: Client-based architecture with separate API clients for each service (Canoe, Claude, Notion)

## Development Commands
- **Install dependencies**: `pip install -r requirements.txt`
- **Format code**: `black .`
- **Lint code**: `flake8 .`
- **Run tests**: `pytest`
- **Test coverage**: `pytest --cov`
- **Pre-commit hooks**: `pre-commit run --all-files`
- **Install pre-commit**: `pre-commit install`
- **Run main script**: `python main.py`
- **Run bulk processing**: `python bulk_process.py`
- **Run single processing**: `python single_process.py`

## Project Structure
- **clients/**: API client classes for external services
  - `canoe_client.py`: Canoe API integration for PDF downloads
  - `claude_client.py`: Claude AI summarization service
  - `notion_client.py`: Notion database storage
- **utils/**: Utility modules
  - `logger.py`: Loguru-based logging configuration
- **data/temp_pdfs/**: Temporary PDF storage (gitignored)
- **logs/**: Application logs with rotation
- **config.py**: Configuration management with 1Password CLI integration
- **main.py**: Main application entry point
- **bulk_process.py**: Batch processing script
- **single_process.py**: Single document processing
- **requirements.txt**: Python dependencies
- **api-docs-v1.json**: API documentation

## Coding Standards
- **Code style**: Black formatter (line length: 88 characters)
- **Linting**: Flake8 with E203 extended ignore
- **Testing**: pytest with coverage reporting
- **Logging**: Loguru with structured logging and timestamps
- **Security**: 1Password CLI for credential management, no secrets in code
- **Git workflow**: Pre-commit hooks for code quality
- **Documentation**: Docstrings for classes and functions

## Common Tasks
- **Adding new features**: Follow client-based architecture pattern
- **Credential management**: Use 1Password CLI with env variable fallbacks
- **Environment setup**: Install 1Password CLI, authenticate, set up vault items
- **Debugging**: Check logs in `logs/pdf_summarizer.log`
- **Local development**: Use Python virtual environment

## Dependencies & Tools
- **Package manager**: pip with requirements.txt
- **Python version**: 3.11+
- **Key dependencies**: 
  - requests (API calls)
  - anthropic (Claude AI)
  - notion-client (Notion API)
  - loguru (logging)
  - pymupdf/pypdf2 (PDF processing)
  - python-dotenv (env variables)
- **Development tools**: black, flake8, pytest, pre-commit
- **External services**: Canoe API, Anthropic API, Notion API
- **Security**: 1Password CLI for credential management

## Working Preferences
When implementing new features or updating existing code:
1. **Always evaluate and propose up to 3 different implementation options**
2. **Provide detailed explanations for each option**, including:
   - What the approach does in simple terms
   - Pros and cons of each option
   - Technical complexity level (simple/moderate/complex)
   - Impact on existing code (minimal/moderate/significant)
   - Security considerations
3. **Use non-technical language when possible**, as the user has no coding experience
4. **Allow the user to choose their preferred option** before proceeding with implementation
5. **Follow existing patterns**: Use client-based architecture, 1Password for secrets, loguru for logging
6. **Test thoroughly**: Run linting, formatting, and tests before completing tasks