"""
Test cases for the DOCX processor module
"""

import pytest
import io
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.docx_processor import DocxProcessor, create_sample_docx
from src.exceptions import InvalidDocxFileError, EditOperationError


class TestDocxProcessor:
    """Test cases for DocxProcessor class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = DocxProcessor()
        self.sample_buffer = create_sample_docx()
    
    def test_load_from_buffer_success(self):
        """Test successful loading of DOCX from buffer"""
        self.processor.load_from_buffer(self.sample_buffer)
        assert self.processor.document is not None
        assert len(self.processor.document.paragraphs) > 0
    
    def test_load_from_buffer_invalid_file(self):
        """Test loading invalid file raises exception"""
        invalid_buffer = io.BytesIO(b"This is not a DOCX file")
        
        with pytest.raises(InvalidDocxFileError):
            self.processor.load_from_buffer(invalid_buffer)
    
    def test_get_document_text(self):
        """Test extracting text from document"""
        self.processor.load_from_buffer(self.sample_buffer)
        text = self.processor.get_document_text()
        
        assert "Sample Document" in text
        assert "bold" in text
        assert "italic text" in text
    
    def test_find_and_replace_text_case_sensitive(self):
        """Test case-sensitive text replacement"""
        self.processor.load_from_buffer(self.sample_buffer)
        
        # Replace with exact case
        replacements = self.processor.find_and_replace_text(
            search_text="bold",
            replace_text="BOLD",
            case_sensitive=True
        )
        
        assert replacements == 1
        text = self.processor.get_document_text()
        assert "BOLD" in text
        assert "bold" not in text
    
    def test_find_and_replace_text_case_insensitive(self):
        """Test case-insensitive text replacement"""
        self.processor.load_from_buffer(self.sample_buffer)
        
        # Replace ignoring case
        replacements = self.processor.find_and_replace_text(
            search_text="SAMPLE",
            replace_text="EXAMPLE",
            case_sensitive=False
        )
        
        assert replacements >= 1
        text = self.processor.get_document_text()
        assert "EXAMPLE" in text
    
    def test_find_and_replace_text_not_found(self):
        """Test replacement when text is not found"""
        self.processor.load_from_buffer(self.sample_buffer)
        
        replacements = self.processor.find_and_replace_text(
            search_text="nonexistent_text",
            replace_text="replacement"
        )
        
        assert replacements == 0
    
    def test_add_paragraph(self):
        """Test adding a new paragraph"""
        self.processor.load_from_buffer(self.sample_buffer)
        original_count = len(self.processor.document.paragraphs)
        
        self.processor.add_paragraph("This is a new paragraph")
        
        assert len(self.processor.document.paragraphs) == original_count + 1
        text = self.processor.get_document_text()
        assert "This is a new paragraph" in text
    
    def test_get_document_info(self):
        """Test getting document information"""
        self.processor.load_from_buffer(self.sample_buffer)
        info = self.processor.get_document_info()
        
        assert "paragraph_count" in info
        assert "table_count" in info
        assert "style_count" in info
        assert info["paragraph_count"] > 0
    
    def test_save_to_buffer(self):
        """Test saving document to buffer"""
        self.processor.load_from_buffer(self.sample_buffer)
        
        # Make a modification
        self.processor.find_and_replace_text("Sample", "Test")
        
        # Save to buffer
        output_buffer = self.processor.save_to_buffer()
        
        assert output_buffer is not None
        assert len(output_buffer.getvalue()) > 0
        
        # Verify the saved document can be loaded
        new_processor = DocxProcessor()
        new_processor.load_from_buffer(output_buffer)
        text = new_processor.get_document_text()
        assert "Test Document" in text
    
    def test_operations_without_loaded_document(self):
        """Test that operations fail when no document is loaded"""
        with pytest.raises(EditOperationError):
            self.processor.find_and_replace_text("test", "replacement")
        
        with pytest.raises(EditOperationError):
            self.processor.add_paragraph("test")
        
        with pytest.raises(EditOperationError):
            self.processor.save_to_buffer()


class TestCreateSampleDocx:
    """Test cases for sample document creation"""
    
    def test_create_sample_docx(self):
        """Test creating a sample DOCX document"""
        buffer = create_sample_docx()
        
        assert buffer is not None
        assert len(buffer.getvalue()) > 0
        
        # Verify it can be loaded
        processor = DocxProcessor()
        processor.load_from_buffer(buffer)
        
        text = processor.get_document_text()
        assert "Sample Document" in text
        assert "bold" in text
        assert "italic text" in text


if __name__ == "__main__":
    pytest.main([__file__])