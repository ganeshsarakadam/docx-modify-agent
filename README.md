# DOCX Modification Service

A Python service that accepts DOCX file buffers, allows content editing while preserving formatting and styles, and returns the modified document.

## Features

- Accept DOCX files via REST API
- Edit text content while preserving formatting
- Maintain document structure and styles
- Return modified DOCX files
- Support for various editing operations

## Project Structure

```
doxc-modify-agent/
├── src/
│   ├── __init__.py
│   ├── docx_processor.py      # Core DOCX processing logic
│   ├── api.py                 # REST API endpoints
│   └── exceptions.py          # Custom exceptions
├── tests/
│   ├── __init__.py
│   ├── test_docx_processor.py
│   └── test_api.py
├── examples/
│   ├── example_usage.py
│   └── sample_documents/
├── requirements.txt
├── main.py                    # Service entry point
└── README.md
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the service:
```bash
python main.py
```

## API Usage

### POST /edit-docx

Upload a DOCX file and specify editing operations.

**Request:**
- File: DOCX file buffer
- JSON payload with editing instructions

**Response:**
- Modified DOCX file

## Examples

See the `examples/` directory for usage examples.