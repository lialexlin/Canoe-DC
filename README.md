# Canoe to Notion Workflow

Automatically downloads PDFs from Canoe, summarizes them with Claude AI, and saves summaries to Notion.

## Features

- 🔐 **Secure credential management** with 1Password CLI integration
- 🤖 **Intelligent PDF summarization** using Claude AI
- 📝 **Automatic Notion page creation** with summaries
- 📋 **Structured logging** with timestamps
- ⚙️ **Configurable processing** settings

## Quick Start

**Local Development Setup:**

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install 1Password CLI:**
   - **macOS:** `brew install 1password-cli`
   - **Linux:** See [1Password CLI installation guide](https://developer.1password.com/docs/cli/get-started)
   - **Windows:** Download from [1Password CLI releases](https://app-updates.agilebits.com/product_history/CLI2)

3. **Sign in to 1Password:**
   ```bash
   op signin
   ```

## 1Password Setup

Create these items in your 1Password vault:

### 1. Canoe API Credentials
- **Item name:** `canoe-api`
- **Fields:**
  - `client_id` (your Canoe client ID)
  - `client_secret` (your Canoe client secret)
  - `base_url` (usually `https://api.canoesoftware.com`)

### 2. Anthropic API
- **Item name:** `anthropic-api`
- **Fields:**
  - `api_key` (your Anthropic API key from https://console.anthropic.com/)

### 3. Notion Integration
- **Item name:** `notion-integration`
- **Fields:**
  - `token` (your Notion integration token)
  - `database_id` (your Notion database ID)

### Setup Instructions:

1. **Create Notion Integration:**
   - Go to https://www.notion.so/my-integrations
   - Create a new integration
   - Copy the token

2. **Create Notion Database:**
   - Create a database with a "Title" property
   - Share the database with your integration
   - Copy the database ID from the URL

3. **Add to 1Password:**
   ```bash
   # Example: Create Canoe API item
   op item create \
     --category="API Credential" \
     --title="canoe-api" \
     --vault="Personal" \
     client_id="your_client_id" \
     client_secret="your_client_secret" \
     base_url="https://api.canoesoftware.com"
   ```

## Configuration

### Environment Variables (Optional Fallback)

If 1Password is unavailable, create a `.env` file:

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