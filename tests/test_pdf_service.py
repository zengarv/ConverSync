"""
Test the PDF service functionality
"""
import pytest
import tempfile
import os
from pathlib import Path
from services.pdf_service import PDFService

class TestPDFService:
    """Test PDF generation service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.pdf_service = PDFService()
        self.test_sections = {
            "Executive Summary": "This is a test meeting summary with key points discussed.",
            "Action Items": "1. Complete project documentation\n2. Schedule follow-up meeting\n3. Review budget proposals",
            "Decisions Made": "- Approved Q1 budget\n- Selected new vendor\n- Postponed product launch"
        }
    
    def test_pdf_service_initialization(self):
        """Test that PDF service initializes properly."""
        assert isinstance(self.pdf_service, PDFService)
    
    def test_create_simple_pdf(self):
        """Test creating a simple PDF document."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "test_simple.pdf")
            
            result = self.pdf_service.create_simple_pdf(
                title="Test Document",
                content="This is test content for the PDF document.",
                output_file=output_file
            )
            
            assert os.path.exists(result)
            assert result == output_file
    
    def test_create_minutes_pdf(self):
        """Test creating a meeting minutes PDF."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "test_minutes.pdf")
            
            result = self.pdf_service.create_minutes_pdf(
                sections=self.test_sections,
                company="Test Company",
                meeting_title="Test Meeting",
                meeting_date="2024-07-07",
                output_file=output_file
            )
            
            assert os.path.exists(result)
            assert result == output_file
    
    def test_merge_sections(self):
        """Test merging sections into text."""
        result = self.pdf_service.merge_sections(self.test_sections)
        
        assert "Executive Summary" in result
        assert "Action Items" in result
        assert "Decisions Made" in result
        assert "test meeting summary" in result
    
    def test_pdf_with_participants(self):
        """Test PDF creation with participants section."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = os.path.join(temp_dir, "test_participants.pdf")
            participants = "John Doe, Jane Smith, Mike Johnson"
            
            result = self.pdf_service.create_minutes_pdf(
                sections=self.test_sections,
                participants=participants,
                output_file=output_file
            )
            
            assert os.path.exists(result)
