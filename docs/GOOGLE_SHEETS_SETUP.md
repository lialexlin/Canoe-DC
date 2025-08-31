# Google Sheets Setup Guide

This guide will help you set up Google Sheets integration for the Canoe-DC workflow.

## Prerequisites

1. Google Cloud account
2. Google Sheets API enabled
3. Service account with appropriate permissions

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your project ID

### 2. Enable Google Sheets API

1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Sheets API"
3. Click on it and press "Enable"

### 3. Create Service Account

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "Service Account"
3. Fill in service account details:
   - Name: `canoe-dc-sheets`
   - Description: "Service account for Canoe-DC Google Sheets integration"
4. Click "Create and Continue"
5. Skip the optional roles (click "Continue")
6. Click "Done"

### 4. Generate Service Account Key

1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Choose "JSON" format
5. Click "Create" - a JSON file will be downloaded
6. **Keep this file secure** - it contains your credentials

### 5. Create and Share Google Sheet

1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new spreadsheet
3. Name it "Canoe Quarterly Reports" (or your preference)
4. Copy the spreadsheet ID from the URL:
   - URL format: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
5. Share the spreadsheet with your service account:
   - Click "Share" button
   - Enter the service account email (found in the JSON key file)
   - Give "Editor" permission
   - Click "Send"

### 6. Configure Credentials

You have two options:

#### Option A: Using Bitwarden (Recommended)

1. Create a new item in Bitwarden folder "Axiom" called `GoogleSheets`
2. Add these fields:
   - Password or Custom Field `credentials_json`: Paste the entire contents of the JSON key file
   - Custom Field `spreadsheet_id`: Paste the spreadsheet ID from step 5

#### Option B: Using Environment Variables

1. Add to your `.env` file:
```bash
GOOGLE_SHEETS_CREDENTIALS_JSON='{"type": "service_account", ...}'  # Full JSON content
GOOGLE_SHEETS_SPREADSHEET_ID='your-spreadsheet-id-here'
```

### 7. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage with Google Sheets

```bash
# Save to both Notion and Google Sheets
python src/bulk.py --days-back 7 --google-sheets

# Save to Google Sheets only
python src/bulk.py --days-back 7 --sheets-only
```

### Single Document Processing

```bash
# Process single document and save to both
python src/single.py --document-id YOUR_ID --google-sheets

# Save to Google Sheets only
python src/single.py --document-id YOUR_ID --sheets-only
```

## Features

- **Automatic Headers**: The first run creates headers automatically
- **Auto-formatting**: Headers are bold with blue background
- **Auto-resize**: Columns adjust to content width
- **Batch Processing**: Multiple documents can be added efficiently
- **Statistics**: Track total documents and processing status
- **Direct Links**: Each row can include Notion URL for cross-reference

## Spreadsheet Structure

| Column | Description |
|--------|-------------|
| Fund Name | Original filename from Canoe |
| Document ID | Canoe document identifier |
| Date Processed | When the summary was generated |
| Data Date | Report date from document metadata |
| Summary | Claude AI generated summary (max 500 chars) |
| Document Type | Type of document (e.g., Quarterly Report) |
| Processing Status | Success/Failed status |
| Notion URL | Link to Notion page (if created) |

## Troubleshooting

### "Permission denied" error
- Ensure you've shared the spreadsheet with the service account email
- Verify the service account has "Editor" permission

### "Spreadsheet not found" error
- Double-check the spreadsheet ID in your configuration
- Ensure the ID doesn't include any extra characters

### "API not enabled" error
- Go to Google Cloud Console and ensure Google Sheets API is enabled
- Wait a few minutes after enabling for it to propagate

## Benefits Over Notion-Only

1. **Better Bulk Analysis**: Sort, filter, and analyze multiple reports easily
2. **Data Visualization**: Create charts and pivot tables
3. **Export Options**: Easy export to CSV, Excel, or other formats
4. **Collaboration**: Share with team members who don't have Notion access
5. **Performance**: Faster for viewing large datasets
6. **Search**: Powerful search and filter capabilities