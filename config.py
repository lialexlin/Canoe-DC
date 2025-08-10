import os
import subprocess
import json
from loguru import logger
from dotenv import load_dotenv

# Load environment variables (for fallback or local development)
load_dotenv()

class OnePasswordConfig:
    """1Password CLI integration for secure credential management"""
    
    def __init__(self, vault_name="Personal"):
        self.vault_name = vault_name
        self._check_op_cli()
    
    def _check_op_cli(self):
        """Check if 1Password CLI is available and authenticated"""
        try:
            result = subprocess.run(
                ["op", "account", "list", "--format=json"],
                capture_output=True,
                text=True,
                check=True
            )
            accounts = json.loads(result.stdout)
            if not accounts:
                raise Exception("No 1Password accounts found. Please run 'op signin'")
            logger.info("✅ 1Password CLI authenticated")
        except subprocess.CalledProcessError:
            raise Exception("1Password CLI not authenticated. Please run 'op signin'")
        except FileNotFoundError:
            raise Exception("1Password CLI not found. Please install from https://1password.com/downloads/command-line/")
    
    def get_secret(self, item_name, field_name="password"):
        """Get a secret from 1Password"""
        try:
            cmd = [
                "op", "item", "get", item_name,
                "--vault", self.vault_name,
                "--field", field_name,
                "--format", "json"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Parse the JSON response and extract the value
            response_text = result.stdout.strip()
            try:
                response_json = json.loads(response_text)
                if isinstance(response_json, dict) and 'value' in response_json:
                    return response_json['value']
                else:
                    # Simple string response
                    return response_text.strip('"')
            except json.JSONDecodeError:
                # Simple string response
                return response_text.strip('"')
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get {item_name}.{field_name} from 1Password: {e}")
            # Fallback to environment variable
            env_var = f"{item_name.upper().replace('-', '_')}_{field_name.upper()}"
            fallback = os.getenv(env_var)
            if fallback:
                logger.warning(f"Using fallback environment variable: {env_var}")
                return fallback
            raise Exception(f"Could not retrieve {item_name}.{field_name} from 1Password or environment")

# Initialize 1Password client
try:
    op = OnePasswordConfig(vault_name=os.getenv('OP_VAULT', 'Canoe workflow'))
    USE_1PASSWORD = True
    logger.info("🔐 Using 1Password for credential management")
except Exception as e:
    logger.warning(f"1Password not available: {e}")
    logger.warning("Falling back to environment variables")
    USE_1PASSWORD = False

def get_config_value(op_item, op_field, env_var, default=None):
    """Get configuration value from 1Password or environment variable"""
    if USE_1PASSWORD:
        try:
            return op.get_secret(op_item, op_field)
        except Exception as e:
            logger.warning(f"1Password lookup failed for {op_item}.{op_field}: {e}")
    
    value = os.getenv(env_var, default)
    if value is None:
        raise ValueError(f"Required configuration not found: {env_var}")
    return value

# API Configuration
CANOE_CLIENT_ID = get_config_value("canoe-api", "client_id", "CANOE_CLIENT_ID")
CANOE_CLIENT_SECRET = get_config_value("canoe-api", "client_secret", "CANOE_CLIENT_SECRET")
CANOE_BASE_URL = get_config_value("canoe-api", "base_url", "CANOE_BASE_URL", "https://api.canoesoftware.com")

ANTHROPIC_API_KEY = get_config_value("anthropic-api", "api_key", "ANTHROPIC_API_KEY")

NOTION_TOKEN = get_config_value("notion-integration", "token", "NOTION_TOKEN")
NOTION_DATABASE_ID = get_config_value("notion-integration", "database_id", "NOTION_DATABASE_ID")

# Processing Settings
MAX_RETRIES = int(os.getenv('MAX_RETRIES', 3))
BATCH_SIZE = 5  # Process 5 PDFs at a time
TEMP_DIR = 'data/temp_pdfs'

# Document Filters
DOCUMENT_TYPES = ['Quarterly Report', 'Account Statement']
MIN_FILE_SIZE = 1000  # bytes
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

# Summary Settings
SUMMARY_MAX_LENGTH = 1000  # words
SUMMARY_STYLE = 'executive'  # executive, detailed, brief