"""
Custom exceptions for the DOCX modification service
"""


class DocxProcessingError(Exception):
    """Base exception for DOCX processing errors"""
    pass


class InvalidDocxFileError(DocxProcessingError):
    """Raised when the provided file is not a valid DOCX file"""
    pass


class EditOperationError(DocxProcessingError):
    """Raised when an edit operation fails"""
    pass


class TextNotFoundError(DocxProcessingError):
    """Raised when text to be replaced is not found in the document"""
    pass


class StylePreservationError(DocxProcessingError):
    """Raised when style preservation fails during editing"""
    pass