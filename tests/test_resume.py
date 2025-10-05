"""
Test cases for the resume processing functionality
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
from src.resume_processor import ResumeProcessor, create_resume_template


class TestResumeAPI:
    """Test cases for resume API endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
        self.sample_resume_data = {
            "name": "GANESH SARAKADAM",
            "contact": {
                "phone": "+1 740-915-3257",
                "email": "ganeshsrv.sarakadam@gmail.com",
                "linkedin": "linkedin.com/in/ganesh-sarakadam"
            },
            "professional_summary": "Frontend Engineer (React, TypeScript) with 5+ years of experience building accessible, high-performance single-page applications.",
            "technical_skills": ["TypeScript", "JavaScript (ES6+)", "React", "Python"],
            "professional_experience": [
                {
                    "company": "Doran Jones Inc",
                    "location": "Remote, USA",
                    "title": "Software Engineer", 
                    "duration": "Aug 2024 – Aug 2025",
                    "highlights": [
                        "Led new feature work and iterative refactors across 5+ React SPAs",
                        "Designed a Storybook-driven React component library"
                    ]
                }
            ],
            "projects": [
                {
                    "name": "Nesh UI — Component Library & Design System",
                    "highlights": ["TypeScript and React component library with tokens, theming"]
                }
            ],
            "education": [
                {
                    "degree": "Master of Science in Computer Science",
                    "institution": "Ohio University",
                    "duration": "August 2022 – May 2024"
                }
            ]
        }
    
    def test_create_resume_template(self):
        """Test creating a resume template"""
        response = self.client.post("/api/create-resume-template")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert len(response.content) > 0
        assert "X-Template-Info" in response.headers
    
    def test_get_resume_placeholders(self):
        """Test getting resume placeholders"""
        response = self.client.get("/api/resume-placeholders")
        assert response.status_code == 200
        data = response.json()
        assert "placeholders" in data
        assert "descriptions" in data
        assert "{{NAME}}" in data["placeholders"]
        assert "{{EMAIL}}" in data["placeholders"]
    
    def test_edit_resume_success(self):
        """Test successful resume generation"""
        # Create a template first
        template_response = self.client.post("/api/create-resume-template")
        template_content = template_response.content
        
        files = {
            "file": ("resume_template.docx", template_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "resume_data": json.dumps(self.sample_resume_data)
        }
        
        response = self.client.post("/api/edit-resume", files=files, data=data)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        assert "X-Replacements-Made" in response.headers
        assert "X-Validation-Results" in response.headers
    
    def test_edit_resume_invalid_json(self):
        """Test resume generation with invalid JSON"""
        template_response = self.client.post("/api/create-resume-template")
        template_content = template_response.content
        
        files = {
            "file": ("resume_template.docx", template_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "resume_data": "invalid json data"
        }
        
        response = self.client.post("/api/edit-resume", files=files, data=data)
        assert response.status_code == 500  # JSON decode error
    
    def test_edit_resume_missing_required_fields(self):
        """Test resume generation with missing required fields"""
        template_response = self.client.post("/api/create-resume-template")
        template_content = template_response.content
        
        # Missing required fields
        incomplete_data = {
            "contact": {
                "email": "test@example.com"
            }
        }
        
        files = {
            "file": ("resume_template.docx", template_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "resume_data": json.dumps(incomplete_data)
        }
        
        response = self.client.post("/api/edit-resume", files=files, data=data)
        assert response.status_code == 400
        assert "Invalid resume data" in response.json()["detail"]
    
    def test_edit_resume_with_custom_mappings(self):
        """Test resume generation with custom field mappings"""
        template_response = self.client.post("/api/create-resume-template")
        template_content = template_response.content
        
        custom_mappings = {
            "{{FULL_NAME}}": "name",
            "{{PHONE_NUMBER}}": "contact.phone"
        }
        
        files = {
            "file": ("resume_template.docx", template_content, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        }
        data = {
            "resume_data": json.dumps(self.sample_resume_data),
            "custom_mappings": json.dumps(custom_mappings)
        }
        
        response = self.client.post("/api/edit-resume", files=files, data=data)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


class TestResumeProcessor:
    """Test cases for ResumeProcessor class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.processor = ResumeProcessor()
        self.sample_data = {
            "name": "John Doe",
            "contact": {
                "phone": "123-456-7890",
                "email": "john@example.com",
                "linkedin": "linkedin.com/in/johndoe"
            },
            "professional_summary": "Experienced software developer",
            "technical_skills": ["Python", "JavaScript", "React"],
            "professional_experience": [
                {
                    "company": "Tech Corp",
                    "title": "Developer",
                    "duration": "2020-2023",
                    "highlights": ["Built web applications", "Led team projects"]
                }
            ]
        }
    
    def test_set_resume_data_from_dict(self):
        """Test setting resume data from dictionary"""
        self.processor.set_resume_data(self.sample_data)
        assert self.processor.resume_data == self.sample_data
    
    def test_set_resume_data_from_json_string(self):
        """Test setting resume data from JSON string"""
        json_string = json.dumps(self.sample_data)
        self.processor.set_resume_data(json_string)
        assert self.processor.resume_data == self.sample_data
    
    def test_set_resume_data_invalid_json(self):
        """Test setting resume data with invalid JSON"""
        from src.exceptions import EditOperationError
        
        with pytest.raises(EditOperationError):
            self.processor.set_resume_data("invalid json")
    
    def test_get_nested_value(self):
        """Test getting nested values from data"""
        value = self.processor._get_nested_value(self.sample_data, "contact.email")
        assert value == "john@example.com"
        
        value = self.processor._get_nested_value(self.sample_data, "name")
        assert value == "John Doe"
        
        value = self.processor._get_nested_value(self.sample_data, "nonexistent.field")
        assert value is None
    
    def test_validate_resume_data(self):
        """Test resume data validation"""
        self.processor.set_resume_data(self.sample_data)
        validation = self.processor.validate_resume_data()
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
    
    def test_validate_resume_data_missing_required(self):
        """Test validation with missing required fields"""
        incomplete_data = {"contact": {"email": "test@example.com"}}
        self.processor.set_resume_data(incomplete_data)
        validation = self.processor.validate_resume_data()
        assert validation["valid"] is False
        assert len(validation["errors"]) > 0
    
    def test_get_resume_placeholders(self):
        """Test getting list of resume placeholders"""
        placeholders = self.processor.get_resume_placeholders()
        assert isinstance(placeholders, list)
        assert "{{NAME}}" in placeholders
        assert "{{EMAIL}}" in placeholders
        assert "{{TECHNICAL_SKILLS}}" in placeholders


if __name__ == "__main__":
    pytest.main([__file__])