import os
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from config import Config

class PDFService:
    """Service for generating PDF documents from meeting summaries."""
    
    def __init__(self):
        Config.ensure_directories()
    
    def create_minutes_pdf(self, sections: dict,
                          company: str = None,
                          logo_path: str = None,
                          output_file: str = None,
                          meeting_title: str = None,
                          meeting_date: str = None,
                          participants: str = None) -> str:
        """
        Build a formal Minutes-of-Meeting PDF.
        
        Args:
            sections (dict): Ordered dict {"Section Title": "Body text", ...}
            company (str, optional): Company name for header
            logo_path (str, optional): Path to company logo
            output_file (str, optional): Output PDF file path
            meeting_title (str, optional): Title of the meeting
            meeting_date (str, optional): Date of the meeting
            participants (str, optional): List of meeting participants
            
        Returns:
            str: Path to the generated PDF file
        """
        # Set defaults
        if company is None:
            company = Config.COMPANY_NAME
        if logo_path is None:
            logo_path = Config.LOGO_PATH
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(Config.OUTPUT_FOLDER / f"minutes_of_meeting_{timestamp}.pdf")
        
        c = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter
        page_num = 1
        
        def header():
            y_header = height - 50
            if logo_path and os.path.exists(logo_path):
                try:
                    c.drawImage(logo_path, 50, y_header - 20,
                               width=80, preserveAspectRatio=True, mask='auto')
                    c.setFont("Helvetica-Bold", 18)
                    c.drawString(140, y_header, company)
                except:
                    # If logo fails to load, just use text
                    c.setFont("Helvetica-Bold", 18)
                    c.drawCentredString(width / 2, y_header, company or "Minutes of the Meeting")
            else:
                c.setFont("Helvetica-Bold", 18)
                c.drawCentredString(width / 2, y_header, company or "Minutes of the Meeting")
            
            # Meeting title if provided
            if meeting_title:
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(width / 2, y_header - 25, meeting_title)
                y_offset = 40
            else:
                y_offset = 25
            
            # Meeting date
            if meeting_date:
                c.setFont("Helvetica", 12)
                c.drawCentredString(width / 2, y_header - y_offset, f"Meeting Date: {meeting_date}")
                y_offset += 15
            
            c.setFont("Helvetica", 10)
            c.drawCentredString(width / 2, y_header - y_offset,
                               f"Generated on {datetime.now():%Y-%m-%d at %H:%M}")
            
            return y_header - y_offset - 20
        
        def footer():
            c.setFont("Helvetica", 9)
            c.setFillGray(0.5)
            c.drawCentredString(width / 2, 30, f"Page {page_num}")
            c.setFillGray(0)
        
        def add_section(title, body, y):
            nonlocal page_num
            
            # Check if we need a new page for the section title
            if y < 100:
                footer()
                c.showPage()
                page_num += 1
                y = header()
            
            c.setFont("Helvetica-Bold", 13)
            c.drawString(50, y, title)
            y -= 20
            
            c.setFont("Helvetica", 11)
            lines = simpleSplit(body, "Helvetica", 11, width - 100)
            for line in lines:
                if y < 60:  # Need space for footer
                    footer()
                    c.showPage()
                    page_num += 1
                    y = header()
                
                c.drawString(50, y, line)
                y -= 14
            
            return y - 15
        
        # First page
        y_cursor = header()
        
        # Add participants section if provided
        if participants:
            y_cursor = add_section("Meeting Participants", participants, y_cursor)
        
        # Add all sections
        for sec_title, sec_body in sections.items():
            y_cursor = add_section(sec_title, sec_body, y_cursor)
        
        footer()
        c.save()
        print(f"✅ PDF saved to '{output_file}'")
        return output_file
    
    def create_simple_pdf(self, title: str, content: str, output_file: str = None) -> str:
        """
        Create a simple PDF with title and content.
        
        Args:
            title (str): Document title
            content (str): Document content
            output_file (str, optional): Output file path
            
        Returns:
            str: Path to the generated PDF file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(Config.OUTPUT_FOLDER / f"document_{timestamp}.pdf")
        
        c = canvas.Canvas(output_file, pagesize=letter)
        width, height = letter
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - 50, title)
        
        # Content
        y = height - 100
        c.setFont("Helvetica", 11)
        lines = simpleSplit(content, "Helvetica", 11, width - 100)
        
        for line in lines:
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(50, y, line)
            y -= 14
        
        c.save()
        return output_file
    
    def create_meeting_minutes_pdf(self, summary: dict, meeting_title: str = None, 
                                  meeting_date: str = None, company_name: str = None) -> dict:
        """
        Create a meeting minutes PDF from a summary dictionary.
        
        Args:
            summary (dict): Dictionary containing meeting summary sections
            meeting_title (str, optional): Title of the meeting
            meeting_date (str, optional): Date of the meeting
            company_name (str, optional): Company name
            
        Returns:
            dict: Result containing PDF file path and status
        """
        try:
            # Set defaults
            if meeting_title is None:
                meeting_title = "Meeting Minutes"
            if meeting_date is None:
                meeting_date = datetime.now().strftime("%Y-%m-%d")
            if company_name is None:
                company_name = "Company"
            
            # Generate output filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(Config.OUTPUT_FOLDER / f"minutes_of_meeting_{timestamp}.pdf")
            
            # Create the PDF
            pdf_path = self.create_minutes_pdf(
                sections=summary,
                company=company_name,
                output_file=output_file,
                meeting_title=meeting_title,
                meeting_date=meeting_date
            )
            
            return {
                'success': True,
                'pdf_file': pdf_path,
                'message': 'Meeting minutes PDF created successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to create meeting minutes PDF'
            }

    def merge_sections(self, sections: dict) -> str:
        """
        Merge all sections into a single text string.
        
        Args:
            sections (dict): Dictionary of sections
            
        Returns:
            str: Combined text of all sections
        """
        combined_text = ""
        for title, content in sections.items():
            combined_text += f"{title}\n{'='*len(title)}\n{content}\n\n"
        return combined_text
