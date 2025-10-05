"""
Test cases for the API endpoints
"""

import pytest
import json
import io
import sys
import os
from fastapi.testclient import TestClient

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api import app
from src.docx_processor import create_sample_docx


class TestAPI:
    """Test cases for API endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.sample_buffer = create_sample_docx()
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert data["service"] == "DOCX Modification Service"
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = self.client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_create_sample_docx(self):
        """Test creating a sample DOCX document"""
        response = self.client.post("/api/create-sample")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert len(response.content) > 0
    
    def test_edit_docx_simple_success(self):
        """Test simple DOCX editing with valid input"""
        files = {
            "file": ("test.docx", self.sample_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "search_text": "Sample Document",
            "replace_text": "Test Document",
            "preserve_formatting": True,
            "case_sensitive": True
        }
        
        response = self.client.post("/api/edit-docx-simple", files=files, data=data)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert "X-Replacements-Made" in response.headers
        assert int(response.headers["X-Replacements-Made"]) > 0
    
    def test_edit_docx_simple_text_not_found(self):
        """Test simple editing when text is not found"""
        files = {
            "file": ("test.docx", self.sample_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "search_text": "nonexistent_text",
            "replace_text": "replacement",
            "preserve_formatting": True,
            "case_sensitive": True
        }
        
        response = self.client.post("/api/edit-docx-simple", files=files, data=data)
        assert response.status_code == 404
    
    def test_edit_docx_simple_invalid_file(self):
        """Test simple editing with invalid file"""
        files = {
            "file": ("test.txt", b"This is not a DOCX file", "text/plain")
        }
        data = {
            "search_text": "test",
            "replace_text": "replacement"
        }
        
        response = self.client.post("/api/edit-docx-simple", files=files, data=data)
        assert response.status_code == 400
    
    def test_edit_docx_complex_operations(self):
        """Test complex DOCX editing with multiple operations"""
        operations = [
            {
                "operation_type": "replace",
                "search_text": "bold",
                "replace_text": "BOLD",
                "preserve_formatting": True,
                "case_sensitive": True
            },
            {
                "operation_type": "add_paragraph",
                "new_text": "This is a new paragraph added by the API"
            }
        ]
        
        files = {
            "file": ("test.docx", self.sample_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "operations": json.dumps(operations)
        }
        
        response = self.client.post("/api/edit-docx", files=files, data=data)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert "X-Operations-Performed" in response.headers
    
    def test_edit_docx_invalid_operations_json(self):
        """Test complex editing with invalid JSON"""
        files = {
            "file": ("test.docx", self.sample_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "operations": "invalid json"
        }
        
        response = self.client.post("/api/edit-docx", files=files, data=data)
        assert response.status_code == 400
    
    def test_get_document_info(self):
        """Test getting document information"""
        files = {
            "file": ("test.docx", self.sample_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        
        response = self.client.post("/api/document-info", files=files)
        assert response.status_code == 200
        data = response.json()
        assert "filename" in data
        assert "document_info" in data
        assert "text_preview" in data
        assert data["document_info"]["paragraph_count"] > 0
    
    def test_file_extension_validation(self):
        """Test that non-DOCX files are rejected"""
        files = {
            "file": ("test.pdf", b"fake pdf content", "application/pdf")
        }
        data = {
            "search_text": "test",
            "replace_text": "replacement"
        }
        
        response = self.client.post("/api/edit-docx-simple", files=files, data=data)
        assert response.status_code == 400
        assert "File must be a DOCX document" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__])