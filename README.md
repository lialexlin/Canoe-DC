# Canoe to Notion Workflow

Automatically downloads PDFs from Canoe, summarizes them with Claude AI, and saves summaries to Notion.

## Features

- 🔐 **Secure credential management** with Bitwarden CLI integration
- 🤖 **Intelligent PDF summarization** using Claude AI
- 📝 **Automatic Notion page creation** with summaries
- 📊 **Google Sheets integration** for data analysis
- 📋 **Structured logging** with timestamps
- ⚙️ **Configurable processing** settings

## Quick Start

**Local Development Setup:**

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Bitwarden CLI:**
   - **macOS:** `brew install bitwarden-cli`
   - **Linux:** `sudo snap install bw` or download from [Bitwarden CLI](https://bitwarden.com/help/cli/)
   - **Windows:** Download from [Bitwarden CLI releases](https://github.com/bitwarden/cli/releases)

3. **Sign in to Bitwarden:**
   ```bash
   bw login
   # Then unlock your vault
   bw unlock
   # Export the session key
   export BW_SESSION="your-session-key"
   ```

## Bitwarden Setup

Create these items in your Bitwarden vault under the `Axiom` folder:

### 1. Canoe API Credentials
- **Item name:** `Canoe`
- **Folder:** `Axiom`
- **Fields:**
  - Username: Your Canoe client ID
  - Password: Your Canoe client secret
  - URI: `https://api.canoesoftware.com`

### 2. Anthropic API
- **Item name:** `Claude`
- **Folder:** `Axiom`
- **Fields:**
  - Password: Your Anthropic API key from https://console.anthropic.com/

### 3. Notion Integration
- **Item name:** `Notion`
- **Folder:** `Axiom`
- **Fields:**
  - Password: Your Notion integration token
  - Notes or Custom Field: `database_id: your-database-id-here`

### Setup Instructions:

1. **Create Notion Integration:**
   - Go to https://www.notion.so/my-integrations
   - Create a new integration
   - Copy the token

2. **Create Notion Database:**
   - Create a database with a "Title" property
   - Share the database with your integration
   - Copy the database ID from the URL

## Configuration

### Environment Variables

Set these for Bitwarden session management:

```bash
# Required after unlock
export BW_SESSION="your-session-key"

# Optional: Auto-unlock with password
export BW_PASSWORD="your-master-password"

# Optional: Custom folder (default: Axiom)
export BW_FOLDER="Axiom"
```

### Fallback Configuration

If Bitwarden is unavailable, create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your credentials as fallback.

### Application Settings

Edit `config.py` to customize:
- Document types to process
- Summary length and style  
- Batch processing settings
- File size limits

## Development

### Code Formatting
```bash
# Format code
black .

# Lint code
flake8 .

# Run tests
pytest
```

### Pre-commit Hooks
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Security Best Practices

✅ **1Password CLI** for credential management  
✅ **No secrets in code** or environment files  

## Troubleshooting

### 1Password Issues
```bash
# Check authentication
op account list

# Re-authenticate if needed
op signin --force

# Verify item access
op item get canoe-api
```

### Python Issues
```bash
# Check dependencies
pip list

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

## Requirements

- **Python 3.11+**
- **1Password CLI** and account
- **Valid API keys** for Canoe, Anthropic, and Notion
- **Internet connection** for API calls

## Architecture

```
📁 Project Structure
├── 📁 clients/                # API client classes
│   ├── canoe_client.py        # Canoe API integration
│   ├── claude_client.py       # Claude AI summarization
│   └── notion_client.py       # Notion database storage
├── 📁 utils/                  # Utility modules
│   └── logger.py              # Logging configuration
├── 📁 data/                   # Data storage (gitignored)
├── 📁 logs/                   # Application logs
├── config.py                  # Configuration with 1Password
├── main.py                    # Main application entry point
└── requirements.txt           # Python dependencies
```