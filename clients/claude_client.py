import anthropic
from loguru import logger
from src import config
import os

class ClaudeClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def summarize_pdf(self, pdf_data, document_info):
        """Summarize PDF content using Claude"""
        # Convert PDF to text (simplified - you might need better PDF processing)
        text_content = self._extract_text_from_pdf(pdf_data)
        
        # Load prompt template from file
        prompt_template = self._load_prompt_template()
        
        prompt = prompt_template.format(
            document_name=document_info.get('name', 'Unknown Document'),
            document_content=text_content[:10000]  # Limit content to fit in context
        )
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def _load_prompt_template(self):
        """Load prompt template from file"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'claude_summary_prompt.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.error("Prompt template file not found, using fallback prompt")
            return """Extract macroeconomic updates from this report (max 200 words). Document: {document_name}. Content: {document_content}"""
    
    def _extract_text_from_pdf(self, pdf_data):
        """Extract text from PDF using PyMuPDF (better extraction quality)"""
        try:
            import fitz  # PyMuPDF
            import io
            
            # Open PDF from bytes
            pdf_document = fitz.open("pdf", pdf_data)
            
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                # Extract text with better formatting preservation
                page_text = page.get_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            pdf_document.close()
            return text.strip()
            
        except Exception as e:
            logger.error(f"Failed to extract PDF text with PyMuPDF: {e}")
            logger.error("PDF text extraction failed")
            return "PDF text extraction failed"