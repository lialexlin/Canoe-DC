import anthropic
from loguru import logger
import config

class ClaudeClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    
    def summarize_pdf(self, pdf_data, document_info):
        """Summarize PDF content using Claude"""
        # Convert PDF to text (simplified - you might need better PDF processing)
        text_content = self._extract_text_from_pdf(pdf_data)
        
        prompt = f"""
        Please provide a concise executive summary of this quarterly report.
        
        Document: {document_info.get('name', 'Unknown Document')}
        
        Focus on:
        - Key financial metrics and performance
        - Major business developments
        - Risk factors and outlook
        - Investment recommendations if any
        
        Keep the summary under {config.SUMMARY_MAX_LENGTH} words.
        
        Document content:
        {text_content[:10000]}  # Limit content to fit in context
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    
    def _extract_text_from_pdf(self, pdf_data):
        """Extract text from PDF (basic implementation)"""
        # This is a simplified version - you might want better PDF processing
        try:
            import PyPDF2
            import io
            
            pdf_file = io.BytesIO(pdf_data)
            reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {e}")
            return "PDF text extraction failed"