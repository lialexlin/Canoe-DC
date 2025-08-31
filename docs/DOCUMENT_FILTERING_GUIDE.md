# Document Filtering Guide

This guide explains how to use the configurable document filtering system in Canoe-DC.

## Overview

The new filtering system allows you to query Canoe API using flexible, reusable filter configurations instead of just `--days-back`. You can:

- Use predefined filter presets
- Create custom filter configurations
- Override parameters on the command line
- Support all Canoe API filter parameters

## Quick Start

### List Available Presets

```bash
python src/bulk.py --list-presets
```

### Use a Preset

```bash
# Use quarterly reports preset (last 30 days)
python src/bulk.py --preset quarterly_reports --google-sheets

# Use annual reports for 2024
python src/bulk.py --preset annual_reports_2024 --sheets-only
```

### Override Parameters

```bash
# Use preset but change document type
python src/bulk.py --preset quarterly_reports --document-type "Annual Report"

# Use preset but change date range
python src/bulk.py --preset custom_date_range --data-date-start 2024-07-01
```

### Legacy Mode (Still Works)

```bash
# Old way still works
python src/bulk.py --days-back 14 --google-sheets
```

## Configuration File

The filter presets are stored in `config/document_filters.json`:

```json
{
  "presets": {
    "quarterly_reports": {
      "name": "Quarterly Reports (Last 30 Days)",
      "document_type": "Quarterly Report",
      "file_upload_time_start": "auto:30d",
      "document_status": "Complete"
    }
  }
}
```

## Available Presets

| Preset | Description |
|--------|-------------|
| `quarterly_reports` | Quarterly reports from last 30 days |
| `quarterly_reports_recent` | Quarterly reports from last 14 days |
| `annual_reports_2024` | All 2024 annual reports |
| `annual_reports_2023` | All 2023 annual reports |
| `capital_calls_recent` | Capital calls from last 14 days |
| `all_statements_monthly` | Account statements from last 30 days |
| `multi_type_recent` | Multiple document types from last 21 days |
| `custom_date_range` | Template for custom date ranges |

## Auto-Date Format

Use `auto:Nd` format for relative dates:

| Format | Description |
|--------|-------------|
| `auto:7d` | 7 days ago |
| `auto:30d` | 30 days ago |
| `auto:90d` | 90 days ago |
| `auto:1y` | 1 year ago |
| `auto:6m` | 6 months ago (approximate) |

## Supported Parameters

The system supports all Canoe API parameters:

### Date Parameters
- `data_date_start` / `data_date_end` - Document data date range
- `file_upload_time_start` / `file_upload_time_end` - Upload time range
- `approval_date_start` / `approval_date_end` - Approval date range

### Filter Parameters
- `document_type` - Type of documents (comma-separated)
- `document_status` - Status filter (Complete, Processing, etc.)
- `fund_id` - Specific fund IDs (comma-separated)
- `account_id` - Specific account IDs (comma-separated)
- `fund_sponsor` - Fund sponsor filter
- `document_source` - Source filter (Email, Upload Engine, etc.)

### Field Selection
- `fields` - Which fields to return (default: id,name,document_type,data_date)

## Command Line Arguments

### Filter Selection (mutually exclusive)
- `--preset <name>` - Use a predefined preset
- `--days-back <days>` - Legacy mode (quarterly reports only)

### Configuration
- `--filter-file <path>` - Path to filter config file (default: config/document_filters.json)
- `--list-presets` - List available presets and exit

### Parameter Overrides
- `--document-type <type>` - Override document type
- `--data-date-start <date>` - Override start date (YYYY-MM-DD)
- `--data-date-end <date>` - Override end date (YYYY-MM-DD)

### Storage Options
- `--no-notion` - Skip Notion storage
- `--google-sheets` - Also save to Google Sheets
- `--sheets-only` - Google Sheets only

## Examples

### Basic Usage

```bash
# List all available presets
python src/bulk.py --list-presets

# Use default quarterly reports preset
python src/bulk.py --preset quarterly_reports

# Get recent capital calls
python src/bulk.py --preset capital_calls_recent --google-sheets
```

### Advanced Usage

```bash
# Override document type in preset
python src/bulk.py --preset quarterly_reports --document-type "Annual Report"

# Custom date range with multiple document types
python src/bulk.py --preset multi_type_recent --data-date-start 2024-06-01 --data-date-end 2024-08-31

# Use custom filter file
python src/bulk.py --filter-file my_filters.json --preset my_custom_preset
```

### Testing

```bash
# Test filter system without API calls
python test_document_filters.py

# Dry run with actual API (skip processing)
python src/bulk.py --preset quarterly_reports --no-notion --sheets-only
```

## Creating Custom Presets

Edit `config/document_filters.json` to add your own presets:

```json
{
  "presets": {
    "my_custom_preset": {
      "name": "My Custom Filter",
      "description": "Documents from specific fund in Q3 2024",
      "document_type": "Quarterly Report,Annual Report",
      "fund_id": "fund_123,fund_456",
      "data_date_start": "2024-07-01",
      "data_date_end": "2024-09-30",
      "document_status": "Complete",
      "fields": "id,name,document_type,data_date,fund_id"
    }
  }
}
```

## Migration from Legacy Mode

### Old Way
```bash
python src/bulk.py --days-back 30
```

### New Way (equivalent)
```bash
python src/bulk.py --preset quarterly_reports
```

### New Way (more flexible)
```bash
python src/bulk.py --preset multi_type_recent --document-type "Quarterly Report,Annual Report,Capital Call Notice"
```

## Troubleshooting

### "Preset not found" Error
- Run `--list-presets` to see available options
- Check spelling of preset name
- Verify `config/document_filters.json` exists

### "Invalid auto-date format" Warning
- Use format like `auto:30d`, not `auto:30days`
- Supported units: d (days), m (months), y (years), h (hours)

### No Documents Found
- Check your date ranges aren't too restrictive
- Verify document types exist in your Canoe instance
- Use broader presets like `multi_type_recent` to test

## API Reference

All filtering is done through the Canoe API `/v1/documents/data` endpoint. See the full parameter list in `docs/api-docs-v1.json` or the Canoe API documentation.