"""
Example usage of the DOCX Modification Service
"""

import requests
import json
import io
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.docx_processor import create_sample_docx


class DocxServiceClient:
    """Client for interacting with the DOCX Modification Service"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def create_sample_document(self, save_path: str = None) -> bytes:
        """Create a sample DOCX document"""
        response = requests.post(f"{self.base_url}/api/create-sample")
        response.raise_for_status()
        
        content = response.content
        
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(content)
            print(f"Sample document saved to: {save_path}")
        
        return content
    
    def simple_replace(
        self, 
        docx_path: str, 
        search_text: str, 
        replace_text: str,
        preserve_formatting: bool = True,
        case_sensitive: bool = True,
        save_path: str = None
    ) -> bytes:
        """Perform simple text replacement"""
        
        with open(docx_path, 'rb') as f:
            files = {'file': (os.path.basename(docx_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {
                'search_text': search_text,
                'replace_text': replace_text,
                'preserve_formatting': preserve_formatting,
                'case_sensitive': case_sensitive
            }
            
            response = requests.post(f"{self.base_url}/api/edit-docx-simple", files=files, data=data)
            response.raise_for_status()
            
            content = response.content
            
            if save_path:
                with open(save_path, 'wb') as output_f:
                    output_f.write(content)
                print(f"Modified document saved to: {save_path}")
            
            # Print response headers for debugging
            replacements = response.headers.get('X-Replacements-Made', 'Unknown')
            print(f"Replacements made: {replacements}")
            
            return content
    
    def complex_edit(
        self, 
        docx_path: str, 
        operations: list,
        save_path: str = None
    ) -> bytes:
        """Perform complex editing operations"""
        
        with open(docx_path, 'rb') as f:
            files = {'file': (os.path.basename(docx_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            data = {
                'operations': json.dumps(operations)
            }
            
            response = requests.post(f"{self.base_url}/api/edit-docx", files=files, data=data)
            response.raise_for_status()
            
            content = response.content
            
            if save_path:
                with open(save_path, 'wb') as output_f:
                    output_f.write(content)
                print(f"Modified document saved to: {save_path}")
            
            # Print response headers for debugging
            operations_performed = response.headers.get('X-Operations-Performed', 'Unknown')
            errors = response.headers.get('X-Errors', '[]')
            document_info = response.headers.get('X-Document-Info', '{}')
            
            print(f"Operations performed: {operations_performed}")
            if errors != '[]':
                print(f"Errors: {errors}")
            print(f"Document info: {document_info}")
            
            return content
    
    def get_document_info(self, docx_path: str) -> dict:
        """Get information about a DOCX document"""
        
        with open(docx_path, 'rb') as f:
            files = {'file': (os.path.basename(docx_path), f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
            
            response = requests.post(f"{self.base_url}/api/document-info", files=files)
            response.raise_for_status()
            
            return response.json()


def main():
    """Main example function"""
    print("DOCX Modification Service - Example Usage")
    print("=" * 50)
    
    # Initialize client
    client = DocxServiceClient()
    
    try:
        # Create sample document
        print("\n1. Creating sample document...")
        sample_path = "sample_documents/original_sample.docx"
        os.makedirs("sample_documents", exist_ok=True)
        client.create_sample_document(sample_path)
        
        # Get document info
        print("\n2. Getting document information...")
        doc_info = client.get_document_info(sample_path)
        print(f"Document info: {json.dumps(doc_info, indent=2)}")
        
        # Simple replacement example
        print("\n3. Performing simple text replacement...")
        simple_output_path = "sample_documents/simple_replaced.docx"
        client.simple_replace(
            docx_path=sample_path,
            search_text="Sample Document",
            replace_text="Modified Document",
            save_path=simple_output_path
        )
        
        # Complex operations example
        print("\n4. Performing complex operations...")
        complex_operations = [
            {
                "operation_type": "replace",
                "search_text": "bold",
                "replace_text": "BOLD",
                "preserve_formatting": True,
                "case_sensitive": True
            },
            {
                "operation_type": "replace",
                "search_text": "italic text",
                "replace_text": "ITALIC TEXT",
                "preserve_formatting": True,
                "case_sensitive": False
            },
            {
                "operation_type": "add_paragraph",
                "new_text": "This paragraph was added by the API service!"
            }
        ]
        
        complex_output_path = "sample_documents/complex_modified.docx"
        client.complex_edit(
            docx_path=sample_path,
            operations=complex_operations,
            save_path=complex_output_path
        )
        
        print("\n5. Example completed successfully!")
        print(f"Check the 'sample_documents' folder for generated files:")
        print(f"  - {sample_path}")
        print(f"  - {simple_output_path}")
        print(f"  - {complex_output_path}")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the service.")
        print("Make sure the service is running: python main.py")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()