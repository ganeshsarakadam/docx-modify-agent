"""
REST API for the DOCX modification service using FastAPI
"""

import io
import json
from typing import Dict, List, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, APIRouter, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from .docx_processor import DocxProcessor
from .resume_processor import ResumeProcessor, create_resume_template
from .exceptions import (
    DocxProcessingError,
    InvalidDocxFileError,
    EditOperationError,
    TextNotFoundError
)


class ResumeData(BaseModel):
    """Model for resume data"""
    name: str = Field(..., description="Full name")
    contact: Dict[str, str] = Field(..., description="Contact information (phone, email, linkedin)")
    professional_summary: str = Field(..., description="Professional summary text")
    technical_skills: Optional[List[str]] = Field(None, description="List of technical skills")
    professional_experience: Optional[List[Dict[str, Any]]] = Field(None, description="Work experience entries")
    projects: Optional[List[Dict[str, Any]]] = Field(None, description="Project entries")
    education: Optional[List[Dict[str, Any]]] = Field(None, description="Education entries")


class ResumeEditResponse(BaseModel):
    """Model for resume edit operation response"""
    success: bool
    message: str
    replacements_made: Dict[str, int]
    validation_results: Optional[Dict[str, Any]] = None
    errors: List[str] = []


class EditOperation(BaseModel):
    """Model for text replacement operations"""
    operation_type: str = Field(..., description="Type of operation: 'replace', 'insert', 'add_paragraph'")
    search_text: Optional[str] = Field(None, description="Text to search for (required for 'replace')")
    replace_text: Optional[str] = Field(None, description="Text to replace with (required for 'replace')")
    new_text: Optional[str] = Field(None, description="New text to insert or add")
    preserve_formatting: bool = Field(True, description="Whether to preserve original formatting")
    case_sensitive: bool = Field(True, description="Whether search should be case sensitive")
    bookmark_name: Optional[str] = Field(None, description="Bookmark name for insert operations")
    style_name: Optional[str] = Field(None, description="Style name for new paragraphs")


class EditRequest(BaseModel):
    """Model for edit request containing multiple operations"""
    operations: List[EditOperation] = Field(..., description="List of edit operations to perform")


class EditResponse(BaseModel):
    """Model for edit operation response"""
    success: bool
    message: str
    operations_performed: int
    document_info: Optional[Dict[str, Any]] = None
    errors: List[str] = []


# Initialize FastAPI app
app = FastAPI(
    title="DOCX Modification Service",
    description="A service for editing DOCX files while preserving formatting and styles",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create API router with /api prefix
api_router = APIRouter(prefix="/api", tags=["DOCX Operations"])


@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "DOCX Modification Service",
        "version": "1.0.0",
        "description": "Upload DOCX files and edit them while preserving formatting",
        "endpoints": {
            "POST /api/edit-docx": "Edit a DOCX file with specified operations",
            "POST /api/edit-docx-simple": "Simple text replacement in DOCX file",
            "POST /api/edit-resume": "Generate resume from DOCX template and JSON data",
            "POST /api/create-resume-template": "Create a resume template with placeholders",
            "POST /api/process-document": "Universal document processing endpoint",
            "GET /api/health": "Health check endpoint",
            "POST /api/create-sample": "Create a sample DOCX file for testing",
            "POST /api/document-info": "Get document information"
        }
    }


@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DOCX Modification Service"}


@api_router.post("/edit-docx", response_model=EditResponse)
async def edit_docx(
    file: UploadFile = File(..., description="DOCX file to edit"),
    operations: str = Form(..., description="JSON string of edit operations")
):
    """
    Edit a DOCX file with multiple operations while preserving formatting
    
    Args:
        file: Uploaded DOCX file
        operations: JSON string containing list of edit operations
        
    Returns:
        StreamingResponse with the modified DOCX file
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="File must be a DOCX document")
    
    try:
        # Parse operations
        operations_data = json.loads(operations)
        edit_request = EditRequest(operations=operations_data)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in operations parameter")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid operations data: {str(e)}")
    
    processor = DocxProcessor()
    errors = []
    operations_performed = 0
    
    try:
        # Load the document
        file_content = await file.read()
        file_buffer = io.BytesIO(file_content)
        processor.load_from_buffer(file_buffer)
        
        # Perform edit operations
        for operation in edit_request.operations:
            try:
                if operation.operation_type == "replace":
                    if not operation.search_text or operation.replace_text is None:
                        errors.append("Replace operation requires search_text and replace_text")
                        continue
                    
                    replacements = processor.find_and_replace_text(
                        search_text=operation.search_text,
                        replace_text=operation.replace_text,
                        preserve_formatting=operation.preserve_formatting,
                        case_sensitive=operation.case_sensitive
                    )
                    
                    if replacements > 0:
                        operations_performed += 1
                    else:
                        errors.append(f"Text '{operation.search_text}' not found in document")
                
                elif operation.operation_type == "add_paragraph":
                    if not operation.new_text:
                        errors.append("Add paragraph operation requires new_text")
                        continue
                    
                    processor.add_paragraph(
                        text=operation.new_text,
                        style=operation.style_name
                    )
                    operations_performed += 1
                
                elif operation.operation_type == "insert":
                    if not operation.bookmark_name or not operation.new_text:
                        errors.append("Insert operation requires bookmark_name and new_text")
                        continue
                    
                    success = processor.insert_text_at_bookmark(
                        bookmark_name=operation.bookmark_name,
                        text=operation.new_text
                    )
                    
                    if success:
                        operations_performed += 1
                    else:
                        errors.append(f"Bookmark '{operation.bookmark_name}' not found")
                
                else:
                    errors.append(f"Unknown operation type: {operation.operation_type}")
            
            except Exception as e:
                errors.append(f"Operation failed: {str(e)}")
        
        # Get document info
        document_info = processor.get_document_info()
        
        # Save the modified document
        output_buffer = processor.save_to_buffer()
        
        # Return the file
        return StreamingResponse(
            io.BytesIO(output_buffer.read()),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=modified_{file.filename}",
                "X-Operations-Performed": str(operations_performed),
                "X-Errors": json.dumps(errors) if errors else "[]",
                "X-Document-Info": json.dumps(document_info)
            }
        )
        
    except HTTPException:
        raise  # Re-raise HTTPExceptions to preserve status codes
    except InvalidDocxFileError:
        raise HTTPException(status_code=400, detail="Invalid DOCX file provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@api_router.post("/edit-docx-simple")
async def edit_docx_simple(
    file: UploadFile = File(..., description="DOCX file to edit"),
    search_text: str = Form(..., description="Text to search for"),
    replace_text: str = Form(..., description="Text to replace with"),
    preserve_formatting: bool = Form(True, description="Whether to preserve formatting"),
    case_sensitive: bool = Form(True, description="Whether search should be case sensitive")
):
    """
    Simple text replacement in a DOCX file
    
    Args:
        file: Uploaded DOCX file
        search_text: Text to search for
        replace_text: Text to replace with
        preserve_formatting: Whether to preserve original formatting
        case_sensitive: Whether search should be case sensitive
        
    Returns:
        StreamingResponse with the modified DOCX file
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="File must be a DOCX document")
    
    processor = DocxProcessor()
    
    try:
        # Load the document
        file_content = await file.read()
        file_buffer = io.BytesIO(file_content)
        processor.load_from_buffer(file_buffer)
        
        # Perform replacement
        replacements = processor.find_and_replace_text(
            search_text=search_text,
            replace_text=replace_text,
            preserve_formatting=preserve_formatting,
            case_sensitive=case_sensitive
        )
        
        if replacements == 0:
            raise HTTPException(status_code=404, detail=f"Text '{search_text}' not found in document")
        
        # Save the modified document
        output_buffer = processor.save_to_buffer()
        
        # Return the file
        return StreamingResponse(
            io.BytesIO(output_buffer.read()),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=modified_{file.filename}",
                "X-Replacements-Made": str(replacements)
            }
        )
        
    except HTTPException:
        raise  # Re-raise HTTPExceptions to preserve status codes
    except InvalidDocxFileError:
        raise HTTPException(status_code=400, detail="Invalid DOCX file provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@api_router.post("/create-sample")
async def create_sample_docx():
    """
    Create a sample DOCX document for testing
    
    Returns:
        StreamingResponse with a sample DOCX file
    """
    try:
        from .docx_processor import create_sample_docx
        
        sample_buffer = create_sample_docx()
        
        return StreamingResponse(
            io.BytesIO(sample_buffer.read()),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=sample_document.docx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sample document: {str(e)}")


@api_router.post("/document-info")
async def get_document_info(file: UploadFile = File(..., description="DOCX file to analyze")):
    """
    Get information about a DOCX document without modifying it
    
    Args:
        file: Uploaded DOCX file
        
    Returns:
        Document information including paragraph count, styles, etc.
    """
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="File must be a DOCX document")
    
    processor = DocxProcessor()
    
    try:
        # Load the document
        file_content = await file.read()
        file_buffer = io.BytesIO(file_content)
        processor.load_from_buffer(file_buffer)
        
        # Get document info
        document_info = processor.get_document_info()
        
        return {
            "filename": file.filename,
            "document_info": document_info,
            "text_preview": processor.get_document_text()[:500] + "..." if len(processor.get_document_text()) > 500 else processor.get_document_text()
        }
        
    except InvalidDocxFileError:
        raise HTTPException(status_code=400, detail="Invalid DOCX file provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@api_router.post("/edit-resume")
async def edit_resume(
    request: Request,
    document: UploadFile = File(...),
    fields: str = Form(...)
):
    """
    Generate a resume by replacing placeholders in a DOCX template with JSON data
    
    Args:
        document: DOCX template file with placeholders like {{NAME}}, {{EMAIL}}, etc.
        fields: JSON string containing resume information
        
    Returns:
        StreamingResponse with the generated resume DOCX file
    """
    # Log request details for debugging
    print(f"\n=== EDIT RESUME REQUEST DEBUG ===")
    print(f"Content-Type: {request.headers.get('content-type')}")
    print(f"Document received: {document.filename if document else 'None'}")
    print(f"Document content type: {document.content_type if document else 'None'}")
    print(f"Document size: {document.size if document and hasattr(document, 'size') else 'Unknown'}")
    print(f"Fields type: {type(fields)}")
    print(f"Fields preview: {fields[:200] if fields else 'None'}...")
    print(f"Form fields received: {list(request.headers.keys())}")
    print("=== END DEBUG ===\n")
    
    # Basic validation
    if not document.filename or not document.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="File must be a DOCX document")
    
    processor = ResumeProcessor()
    errors = []
    
    try:
        # Load the template document
        print("DEBUG: About to read document content...")
        file_content = await document.read()
        file_buffer = io.BytesIO(file_content)
        print("DEBUG: About to load document into processor...")
        processor.load_from_buffer(file_buffer)
        print("DEBUG: Document loaded successfully")
        
        # Set resume data
        try:
            print("DEBUG: About to set resume data...")
            processor.set_resume_data(fields)
            print("DEBUG: Resume data set successfully")
        except Exception as e:
            print(f"DEBUG: Error setting resume data: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid resume data format: {str(e)}")
        
        # Validate resume data
        print("DEBUG: About to validate resume data...")
        validation_results = processor.validate_resume_data()
        print(f"DEBUG: Validation results: {validation_results}")
        if not validation_results["valid"]:
            errors.extend(validation_results["errors"])
            # Don't fail on validation errors, just log warnings
            print(f"Validation warnings: {validation_results.get('warnings', [])}")
        
        # Apply all resume data to the document
        print("DEBUG: About to apply resume data to document...")
        
        # Use JSON template replacement (handles individual placeholders like {{company1}}, {{highlights1}})
        replacements_made = processor.apply_json_template_replacement()
        print(f"JSON template replacements made: {replacements_made}")

        print(f"Replacements made: {replacements_made}")
        print("DEBUG: Resume data applied successfully")
        
        # Save the modified document
        output_buffer = processor.save_to_buffer()
        
        # Return the file
        return StreamingResponse(
            io.BytesIO(output_buffer.read()),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": f"attachment; filename=resume_{document.filename}",
                "X-Replacements-Made": json.dumps(replacements_made),
                "X-Validation-Results": json.dumps(validation_results),
                "X-Errors": json.dumps(errors) if errors else "[]"
            }
        )
        
    except HTTPException:
        raise
    except InvalidDocxFileError:
        raise HTTPException(status_code=400, detail="Invalid DOCX file provided")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume processing error: {str(e)}")


@api_router.post("/create-resume-template")
async def create_resume_template_endpoint():
    """
    Create a sample resume template with placeholders for testing
    
    Returns:
        StreamingResponse with a resume template DOCX file
    """
    try:
        template_buffer = create_resume_template()
        
        return StreamingResponse(
            io.BytesIO(template_buffer.read()),
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={
                "Content-Disposition": "attachment; filename=resume_template.docx",
                "X-Template-Info": json.dumps({
                    "placeholders": [
                        "{{NAME}}", "{{PHONE}}", "{{EMAIL}}", "{{LINKEDIN}}",
                        "{{PROFESSIONAL_SUMMARY}}", "{{TECHNICAL_SKILLS}}",
                        "{{PROFESSIONAL_EXPERIENCE}}", "{{PROJECTS}}", 
                        "{{EDUCATION}}", "{{CURRENT_DATE}}"
                    ]
                })
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create resume template: {str(e)}")


@api_router.get("/resume-placeholders")
async def get_resume_placeholders():
    """
    Get list of available resume placeholders for templates
    
    Returns:
        JSON object with available placeholders and their descriptions
    """
    processor = ResumeProcessor()
    placeholders = processor.get_resume_placeholders()
    
    placeholder_info = {
        "{{NAME}}": "Full name from resume data",
        "{{PHONE}}": "Phone number from contact info",
        "{{EMAIL}}": "Email address from contact info", 
        "{{LINKEDIN}}": "LinkedIn URL from contact info",
        "{{PROFESSIONAL_SUMMARY}}": "Professional summary text",
        "{{TECHNICAL_SKILLS}}": "Comma-separated list of technical skills",
        "{{PROFESSIONAL_EXPERIENCE}}": "Formatted work experience entries",
        "{{PROJECTS}}": "Formatted project entries",
        "{{EDUCATION}}": "Formatted education entries",
        "{{CURRENT_DATE}}": "Current date in 'Month Year' format"
    }
    
    return {
        "placeholders": placeholders,
        "descriptions": placeholder_info,
        "usage": "Use these placeholders in your DOCX template, and they will be replaced with data from your JSON"
    }


@api_router.post("/debug-frontend-request")
async def debug_frontend_request(
    document: UploadFile = File(..., description="DOCX file"),
    fields: str = Form(..., description="JSON string")
):
    """
    Debug endpoint to check request format for frontend integration
    """
    try:
        # Check file
        file_info = {
            "filename": document.filename,
            "content_type": document.content_type,
            "size": len(await document.read())
        }
        
        # Check JSON
        try:
            parsed_data = json.loads(fields)
            json_info = {
                "valid_json": True,
                "keys": list(parsed_data.keys()) if isinstance(parsed_data, dict) else "Not a dict",
                "sample": str(parsed_data)[:200] + "..." if len(str(parsed_data)) > 200 else str(parsed_data)
            }
        except json.JSONDecodeError as e:
            json_info = {
                "valid_json": False,
                "error": str(e),
                "sample": fields[:200] + "..." if len(fields) > 200 else fields
            }
        
        return {
            "file_info": file_info,
            "json_info": json_info,
            "status": "Debug info retrieved successfully"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "Debug failed"
        }


@api_router.post("/debug-resume-request")
async def debug_resume_request(
    file: UploadFile = File(..., description="DOCX file"),
    resume_data: str = Form(..., description="JSON string")
):
    """
    Debug endpoint to check request format for resume processing
    """
    try:
        # Check file
        file_info = {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(await file.read())
        }
        
        # Check JSON
        try:
            parsed_data = json.loads(resume_data)
            json_info = {
                "valid_json": True,
                "keys": list(parsed_data.keys()) if isinstance(parsed_data, dict) else "Not a dict",
                "sample": str(parsed_data)[:200] + "..." if len(str(parsed_data)) > 200 else str(parsed_data)
            }
        except json.JSONDecodeError as e:
            json_info = {
                "valid_json": False,
                "error": str(e),
                "sample": resume_data[:200] + "..." if len(resume_data) > 200 else resume_data
            }
        
        return {
            "file_info": file_info,
            "json_info": json_info,
            "status": "Debug info retrieved successfully"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "Debug failed"
        }


@api_router.post("/simple-test")
async def simple_test(
    file: UploadFile = File(...),
    data: str = Form(...)
):
    """
    Very simple test endpoint to verify basic form submission
    """
    return {
        "filename": file.filename,
        "file_size": len(await file.read()),
        "data_received": data[:100] + "..." if len(data) > 100 else data,
        "status": "success"
    }


@api_router.post("/debug-any-request")
async def debug_any_request(request: Request):
    """
    Debug endpoint to capture any request and show what's being sent
    """
    try:
        print(f"\n=== DEBUG ANY REQUEST ===")
        print(f"Method: {request.method}")
        print(f"URL: {request.url}")
        print(f"Headers: {dict(request.headers)}")
        print(f"Content-Type: {request.headers.get('content-type')}")
        
        # Try to read the body
        try:
            body = await request.body()
            print(f"Body size: {len(body)}")
            print(f"Body preview: {body[:500]}")
        except Exception as e:
            print(f"Could not read body: {e}")
        
        print("=== END DEBUG ===\n")
        
        return {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "content_type": request.headers.get('content-type'),
            "message": "Request logged to console"
        }
        
    except Exception as e:
        return {"error": str(e)}


# Include the API router
app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)