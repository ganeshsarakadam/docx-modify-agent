# DOCX Modification Service - Usage Guide

## Overview

This service provides a REST API for editing DOCX documents while preserving their formatting and styles. You can perform various operations like text replacement, paragraph addition, and more.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the service:**
   ```bash
   python main.py
   ```

3. **Access the API documentation:**
   - Interactive docs: http://localhost:8000/docs
   - OpenAPI schema: http://localhost:8000/openapi.json

## API Endpoints

### 1. Health Check
```
GET /api/health
```
Returns service health status.

### 2. Create Sample Document
```
POST /api/create-sample
```
Creates a sample DOCX document for testing purposes.

**Response:** DOCX file download

### 3. Simple Text Replacement
```
POST /api/edit-docx-simple
```
Performs simple find-and-replace operations on a DOCX document.

**Parameters:**
- `file`: DOCX file (multipart/form-data)
- `search_text`: Text to search for
- `replace_text`: Text to replace with
- `preserve_formatting`: Whether to preserve formatting (default: true)
- `case_sensitive`: Whether search is case sensitive (default: true)

**Response:** Modified DOCX file with headers:
- `X-Replacements-Made`: Number of replacements performed

### 4. Complex Document Editing
```
POST /api/edit-docx
```
Performs multiple editing operations on a DOCX document.

**Parameters:**
- `file`: DOCX file (multipart/form-data)
- `operations`: JSON string containing array of operations

**Operation Types:**

#### Replace Operation
```json
{
  "operation_type": "replace",
  "search_text": "old text",
  "replace_text": "new text",
  "preserve_formatting": true,
  "case_sensitive": true
}
```

#### Add Paragraph Operation
```json
{
  "operation_type": "add_paragraph",
  "new_text": "New paragraph content",
  "style_name": "Normal"
}
```

#### Insert at Bookmark Operation
```json
{
  "operation_type": "insert",
  "bookmark_name": "bookmark1",
  "new_text": "Text to insert"
}
```

**Response:** Modified DOCX file with headers:
- `X-Operations-Performed`: Number of successful operations
- `X-Errors`: JSON array of any errors encountered
- `X-Document-Info`: JSON object with document metadata

### 5. Document Information
```
POST /api/document-info
```
Analyzes a DOCX document and returns metadata without modifying it.

**Parameters:**
- `file`: DOCX file (multipart/form-data)

**Response:** JSON object with document information

### 6. Resume Generation
```
POST /api/edit-resume
```
Generate a resume by replacing placeholders in a DOCX template with JSON data.

**Parameters:**
- `file`: DOCX template file with placeholders
- `resume_data`: JSON string containing resume information
- `custom_mappings`: Optional JSON string with custom placeholder mappings

**Response:** Modified DOCX file with resume data

### 7. Create Resume Template
```
POST /api/create-resume-template
```
Creates a sample resume template with placeholders.

**Response:** DOCX template file

### 8. Get Resume Placeholders
```
GET /api/resume-placeholders
```
Get list of available resume placeholders for templates.

**Response:** JSON object with available placeholders

## Python Client Example

```python
import requests
import json

# Create a client class for easier interaction
class DocxServiceClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def simple_replace(self, docx_path, search_text, replace_text):
        with open(docx_path, 'rb') as f:
            files = {'file': f}
            data = {
                'search_text': search_text,
                'replace_text': replace_text,
                'preserve_formatting': True
            }
            response = requests.post(f"{self.base_url}/api/edit-docx-simple", 
                                   files=files, data=data)
            return response.content
    
    def complex_edit(self, docx_path, operations):
        with open(docx_path, 'rb') as f:
            files = {'file': f}
            data = {'operations': json.dumps(operations)}
            response = requests.post(f"{self.base_url}/api/edit-docx", 
                                   files=files, data=data)
            return response.content

# Usage example
client = DocxServiceClient()

# Simple replacement
modified_content = client.simple_replace(
    'document.docx', 
    'old text', 
    'new text'
)

# Save the result
with open('modified_document.docx', 'wb') as f:
    f.write(modified_content)

# Complex operations
operations = [
    {
        "operation_type": "replace",
        "search_text": "Company Name",
        "replace_text": "Acme Corporation",
        "preserve_formatting": True
    },
    {
        "operation_type": "add_paragraph",
        "new_text": "This document was automatically generated."
    }
]

modified_content = client.complex_edit('template.docx', operations)
```

## Resume Generation Example

```python
import requests
import json

# Resume data matching your JSON structure
resume_data = {
    "name": "GANESH SARAKADAM",
    "contact": {
        "phone": "+1 740-915-3257",
        "email": "ganeshsrv.sarakadam@gmail.com",
        "linkedin": "linkedin.com/in/ganesh-sarakadam"
    },
    "professional_summary": "Frontend Engineer (React, TypeScript) with 5+ years of experience...",
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

# Generate resume from template
with open('resume_template.docx', 'rb') as f:
    files = {'file': f}
    data = {'resume_data': json.dumps(resume_data)}
    
    response = requests.post('http://localhost:8001/api/edit-resume', 
                           files=files, data=data)
    
    # Save generated resume
    with open('generated_resume.docx', 'wb') as output:
        output.write(response.content)
```

## cURL Examples

### Create Sample Document
```bash
curl -X POST "http://localhost:8000/api/create-sample" \
     -H "accept: application/vnd.openxmlformats-officedocument.wordprocessingml.document" \
     --output sample.docx
```

### Simple Text Replacement
```bash
curl -X POST "http://localhost:8000/api/edit-docx-simple" \
     -H "accept: application/vnd.openxmlformats-officedocument.wordprocessingml.document" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.docx" \
     -F "search_text=old text" \
     -F "replace_text=new text" \
     -F "preserve_formatting=true" \
     --output modified.docx
```

### Complex Operations
```bash
curl -X POST "http://localhost:8000/api/edit-docx" \
     -H "accept: application/vnd.openxmlformats-officedocument.wordprocessingml.document" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@document.docx" \
     -F 'operations=[{"operation_type":"replace","search_text":"old","replace_text":"new","preserve_formatting":true}]' \
     --output modified.docx
```

## Error Handling

The service returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid file, malformed JSON, etc.)
- `404`: Text not found (for simple replacement)
- `500`: Internal server error

Error responses include detailed error messages in JSON format.

## Formatting Preservation

The service is designed to preserve document formatting:

- **Character-level formatting**: Bold, italic, underline, font properties
- **Paragraph formatting**: Alignment, spacing, indentation
- **Document structure**: Tables, headers, lists
- **Styles**: Document styles are preserved and can be applied to new content

## Limitations

1. **Bookmark operations**: Limited bookmark support in current version
2. **Complex formatting**: Some advanced formatting may not be fully preserved
3. **File size**: Large documents may require longer processing time
4. **Concurrent editing**: No support for simultaneous edits on the same document

## Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_docx_processor.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src
```

## Development

### Project Structure
```
doxc-modify-agent/
├── src/
│   ├── __init__.py
│   ├── docx_processor.py      # Core DOCX processing
│   ├── api.py                 # FastAPI application
│   └── exceptions.py          # Custom exceptions
├── tests/
│   ├── test_docx_processor.py # Core functionality tests
│   └── test_api.py           # API endpoint tests
├── examples/
│   └── example_usage.py      # Usage examples
├── requirements.txt
├── main.py                   # Service entry point
└── README.md
```

### Adding New Features

1. **New operation types**: Add to `DocxProcessor` class and update API models
2. **Additional endpoints**: Add to `api.py` with proper error handling
3. **Enhanced formatting**: Extend formatting preservation logic in `docx_processor.py`

## Troubleshooting

### Common Issues

1. **"Invalid DOCX file" error**
   - Ensure the uploaded file is a valid DOCX document
   - Check file is not corrupted

2. **"Text not found" error**
   - Verify the search text exists in the document
   - Check case sensitivity settings
   - Consider using case-insensitive search

3. **Service connection errors**
   - Ensure the service is running on the correct port
   - Check firewall settings
   - Verify the base URL is correct

### Debug Mode

Start the service in debug mode for development:
```bash
python main.py --reload --host 127.0.0.1 --port 8000
```

This enables auto-reload when code changes are detected.