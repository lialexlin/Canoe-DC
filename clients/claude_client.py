import anthropic
from loguru import logger
from src import config
import os
import re

# Constants for PDF processing
SECTION_BREAK_THRESHOLD = 30  # Vertical pixels indicating section break between text blocks
# Claude Sonnet 4 has 200K+ token context - no need to limit response tokens
CLAUDE_MODEL = "claude-sonnet-4-20250514"  # Claude Sonnet 4.0 model (May 2025 version)
MAX_SUMMARY_WORDS = 200  # Maximum words in summary (as per prompt)

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
            document_content=text_content  # Send full content - no truncation
        )
        
        response = self.client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=4096,  # Generous limit to allow full 200-word summaries
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
        """Extract text from PDF using PyMuPDF with enhanced structure preservation"""
        try:
            import fitz  # PyMuPDF
            import io
            import re
            
            # Open PDF from bytes
            pdf_document = fitz.open("pdf", pdf_data)
            
            full_text = []
            
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Extract text blocks with structure (preserves layout better)
                blocks = page.get_text("blocks")
                
                page_text = f"\n--- Page {page_num + 1} ---\n"
                
                # Sort blocks by vertical position (top to bottom)
                blocks.sort(key=lambda b: (b[1], b[0]))  # Sort by y0, then x0
                
                current_section = []
                last_y = 0
                
                for block in blocks:
                    if len(block) >= 5:  # Text blocks have at least 5 elements
                        x0, y0, x1, y1, text = block[:5]
                        
                        # Clean the text
                        text = text.strip()
                        if not text:
                            continue
                        
                        # Add spacing between sections (large vertical gaps)
                        if last_y > 0 and (y0 - last_y) > SECTION_BREAK_THRESHOLD:
                            if current_section:
                                page_text += " ".join(current_section) + "\n\n"
                                current_section = []
                        
                        current_section.append(text)
                        last_y = y1
                
                # Add remaining text
                if current_section:
                    page_text += " ".join(current_section) + "\n"
                
                full_text.append(page_text)
            
            pdf_document.close()
            
            # Join all pages
            extracted_text = "\n".join(full_text)
            
            # Clean up excessive whitespace and formatting issues
            extracted_text = self._clean_extracted_text(extracted_text)
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Failed to extract PDF text with PyMuPDF: {e}")
            logger.error("PDF text extraction failed")
            return "PDF text extraction failed"
    
    def _clean_extracted_text(self, text):
        """Clean and format extracted text for better readability"""
        # Remove excessive newlines (more than 2 in a row)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove excessive spaces
        text = re.sub(r' {2,}', ' ', text)
        
        # Fix common OCR/extraction issues
        text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Add space between camelCase
        
        # Remove page markers if they're just numbers
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Ensure proper spacing after periods
        text = re.sub(r'\.(?=[A-Z])', '. ', text)
        
        return text.strip()