from notion_client import Client
from datetime import datetime
from loguru import logger
from src import config

class NotionClient:
    def __init__(self):
        self.client = Client(auth=config.NOTION_TOKEN)
        self.database_id = config.NOTION_DATABASE_ID
    
    def create_summary_page(self, document_info, summary):
        """Create a new page in Notion with the summary"""
        
        # Prepare the page properties
        properties = {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": document_info.get('name', 'Untitled Document')
                        }
                    }
                ]
            },
        }
        
        # Create the page content
        children = [
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Executive Summary"}
                        }
                    ]
                }
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": summary}
                        }
                    ]
                }
            }
        ]
        
        # Create the page
        response = self.client.pages.create(
            parent={"database_id": self.database_id},
            properties=properties,
            children=children
        )
        
        logger.info(f"Created Notion page: {response['url']}")
        return response