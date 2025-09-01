import json
import os
import subprocess

from dotenv import load_dotenv
from loguru import logger

# Load environment variables (for fallback or local development)
load_dotenv()

class BitwardenConfig:
    """Bitwarden CLI integration for secure credential management"""
    
    def __init__(self, folder_name="Axiom"):
        self.folder_name = folder_name
        self.session = None
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize Bitwarden session (unlock if needed)"""
        try:
            # Check if already logged in and unlocked
            result = subprocess.run(
                ["bw", "status"],
                capture_output=True,
                text=True,
                check=False
            )
            
            status = json.loads(result.stdout)
            
            if status.get("status") == "unauthenticated":
                raise Exception("Bitwarden CLI not authenticated. Please run 'bw login'")
            
            if status.get("status") == "locked":
                # Try to unlock using environment variable BW_PASSWORD
                bw_password = os.getenv("BW_PASSWORD")
                if bw_password:
                    # SECURITY FIX: Use stdin instead of CLI args to prevent password exposure
                    unlock_process = subprocess.Popen(
                        ["bw", "unlock", "--raw"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    try:
                        stdout, stderr = unlock_process.communicate(
                            input=bw_password, 
                            timeout=30
                        )
                        
                        if unlock_process.returncode == 0:
                            self.session = stdout.strip()
                            if self._validate_session(self.session):
                                os.environ["BW_SESSION"] = self.session
                                logger.info("✅ Bitwarden unlocked with password")
                            else:
                                raise Exception("Invalid session token received from Bitwarden")
                        else:
                            logger.error(f"Bitwarden unlock failed: {stderr}")
                            raise Exception("Failed to unlock Bitwarden. Please check your password")
                    except subprocess.TimeoutExpired:
                        unlock_process.kill()
                        raise Exception("Bitwarden unlock timed out")
                    finally:
                        # Clear password from memory (best effort)
                        bw_password = None
                else:
                    # Check if BW_SESSION is already set
                    self.session = os.getenv("BW_SESSION")
                    if not self.session:
                        raise Exception("Bitwarden is locked. Please set BW_SESSION or BW_PASSWORD environment variable")
                    elif not self._validate_session(self.session):
                        raise Exception("Invalid or expired BW_SESSION. Please run 'bw unlock' manually")
            
            # If already unlocked
            if status.get("status") == "unlocked":
                self.session = os.getenv("BW_SESSION", "")
                logger.info("✅ Bitwarden CLI authenticated and unlocked")
            
        except subprocess.CalledProcessError as e:
            raise Exception(f"Bitwarden CLI error: {e}")
        except FileNotFoundError:
            raise Exception("Bitwarden CLI not found. Please install from https://bitwarden.com/help/cli/")
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Bitwarden status: {e}")
    
    def _validate_session(self, session_token):
        """Validate session token format and test access"""
        if not session_token or len(session_token) < 10:
            logger.warning("Invalid session token format")
            return False
        
        try:
            # Test access with a simple, safe command
            result = subprocess.run(
                ["bw", "status", "--session", session_token],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )
            
            if result.returncode == 0:
                status_data = json.loads(result.stdout)
                return status_data.get("status") == "unlocked"
            else:
                logger.warning("Session validation failed")
                return False
                
        except (subprocess.TimeoutExpired, json.JSONDecodeError, Exception) as e:
            logger.warning(f"Session validation error: {e}")
            return False
    
    def _sync_vault(self):
        """Sync vault to get latest data"""
        try:
            cmd = ["bw", "sync"]
            if self.session:
                cmd.extend(["--session", self.session])
            
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.debug("Bitwarden vault synced")
        except subprocess.CalledProcessError:
            logger.warning("Failed to sync Bitwarden vault, using cached data")
    
    def get_secret(self, item_name, field_name=None):
        """Get a secret from Bitwarden
        
        Args:
            item_name: Name of the item in Bitwarden (e.g., "Canoe", "Claude", "Notion")
            field_name: Specific field to extract (e.g., "client_id", "api_key")
        """
        try:
            # Sync vault first (optional, can be disabled for performance)
            # self._sync_vault()
            
            # Search for item in the specified folder
            cmd = ["bw", "list", "items", "--search", item_name]
            if self.session:
                cmd.extend(["--session", self.session])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            items = json.loads(result.stdout)
            
            # Filter items by folder name
            matching_item = None
            for item in items:
                # Check if item is in the correct folder
                folder_id = item.get("folderId")
                if folder_id:
                    # Get folder details
                    folder_cmd = ["bw", "get", "folder", folder_id]
                    if self.session:
                        folder_cmd.extend(["--session", self.session])
                    
                    folder_result = subprocess.run(
                        folder_cmd,
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    
                    if folder_result.returncode == 0:
                        folder = json.loads(folder_result.stdout)
                        if folder.get("name") == self.folder_name:
                            matching_item = item
                            break
            
            if not matching_item:
                raise Exception(f"Item '{item_name}' not found in folder '{self.folder_name}'")
            
            # Extract the requested field
            if field_name:
                # Check login fields
                if matching_item.get("login"):
                    login = matching_item["login"]
                    
                    # Common field mappings
                    if field_name in ["username", "client_id"]:
                        return login.get("username", "")
                    elif field_name in ["password", "client_secret", "api_key", "token"]:
                        return login.get("password", "")
                    elif field_name == "base_url" and login.get("uris"):
                        # Return first URI as base_url
                        return login["uris"][0].get("uri", "https://api.canoesoftware.com")
                
                # Check custom fields
                if matching_item.get("fields"):
                    for field in matching_item["fields"]:
                        if field.get("name") == field_name:
                            return field.get("value", "")
                
                # Check notes for specific fields
                if field_name == "database_id" and matching_item.get("notes"):
                    # Parse database_id from notes if stored there
                    notes = matching_item.get("notes", "")
                    if "database_id:" in notes:
                        for line in notes.split("\n"):
                            if "database_id:" in line:
                                return line.split("database_id:")[1].strip()
                
                # Default return empty string if field not found
                logger.warning(f"Field '{field_name}' not found in item '{item_name}'")
                return ""
            else:
                # Return the password by default
                if matching_item.get("login"):
                    return matching_item["login"].get("password", "")
                return ""
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get {item_name} from Bitwarden: {e}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving {item_name}.{field_name}: {e}")
            raise

# Initialize Bitwarden client
try:
    bw = BitwardenConfig(folder_name=os.getenv('BW_FOLDER', 'Axiom'))
    USE_BITWARDEN = True
    logger.info("🔐 Using Bitwarden for credential management")
except Exception as e:
    logger.warning(f"Bitwarden not available: {e}")
    logger.warning("Falling back to environment variables")
    USE_BITWARDEN = False
    bw = None

def get_config_value(bw_item, field_name, env_var, default=None):
    """Get configuration value from Bitwarden or environment variable
    
    Args:
        bw_item: Bitwarden item name mapping
        field_name: Field name in the Bitwarden item
        env_var: Environment variable name for fallback
        default: Default value if not found
    """
    # Map old 1Password items to Bitwarden items
    item_mapping = {
        "canoe-api": "Canoe",
        "anthropic-api": "Claude", 
        "notion-integration": "Notion",
        "google-sheets": "GoogleSheets"
    }
    
    actual_item = item_mapping.get(bw_item, bw_item)
    
    if USE_BITWARDEN and bw:
        try:
            value = bw.get_secret(actual_item, field_name)
            if value:
                # SECURITY FIX: Never log actual credential values
                logger.debug(f"✅ Retrieved {actual_item}.{field_name} from Bitwarden")
                return value
            if default is not None:
                logger.debug(f"Using default value for {actual_item}.{field_name}")
                return default
            logger.warning(f"Empty value from Bitwarden for {actual_item}.{field_name}, trying environment")
        except Exception as e:
            logger.warning(f"Bitwarden lookup failed for {actual_item}.{field_name}: {e}")
    
    # Fallback to environment variable
    value = os.getenv(env_var, default)
    if value is None:
        raise ValueError(f"Required configuration not found: {env_var}")
    
    # SECURITY FIX: Never log actual credential values in production
    if field_name in ['password', 'api_key', 'token', 'client_secret', 'credentials_json']:
        logger.debug(f"✅ Retrieved {env_var} from environment variables")
    else:
        logger.debug(f"✅ Retrieved {env_var}={value[:20]}{'...' if len(str(value)) > 20 else ''} from environment")
    
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