# Canoe to DC workflow

Automatically downloads PDFs from Canoe, summarizes them with Claude AI, and saves summaries to Notion.

## Features

- 🔐 Secure OAuth authentication with Canoe API
- 🤖 Intelligent PDF summarization using Claude AI
- 📝 Automatic Notion page creation with summaries
- 📋 Structured logging with timestamps
- ⚙️ Configurable processing settings

## Setup

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd Canoe-DC
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` with your API credentials:

- **Canoe API**: Get your client ID and secret from your Canoe dashboard
- **Anthropic API**: Get your API key from https://console.anthropic.com/
- **Notion Integration**: 
  1. Create a new integration at https://www.notion.so/my-integrations
  2. Create a database with a "Title" property
  3. Share the database with your integration
  4. Copy the database ID from the URL

### 4. Run the application
```bash
python main.py
```

## Configuration

Edit `config.py` to customize:
- Document types to process
- Summary length and style
- Batch processing settings
- File size limits

## Security

- Never commit your `.env` file to version control
- Use environment-specific API keys
- Regularly rotate your API credentials

## Requirements

- Python 3.7+
- Valid API keys for Canoe, Anthropic, and Notion
- Internet connection for API calls

