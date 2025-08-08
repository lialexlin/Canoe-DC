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
        You are analyzing a quarterly update report from a private equity manager. Create a concise executive summary (maximum 200 words) that focuses specifically on the macroeconomic update for the country/region covered by the GP.
        
        Requirements:
        - Extract only macroeconomic information from the provided report
        - Do not add external information or analysis beyond what's explicitly stated
        - Maintain factual accuracy and objectivity
        
        Document: {document_info.get('name', 'Unknown Document')}
        
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
            # Fallback to PyPDF2 if PyMuPDF fails
            try:
                import PyPDF2
                import io
                
                pdf_file = io.BytesIO(pdf_data)
                reader = PyPDF2.PdfReader(pdf_file)
                
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                
                return text
            except Exception as fallback_error:
                logger.error(f"Fallback PDF extraction also failed: {fallback_error}")
                return "PDF text extraction failed"