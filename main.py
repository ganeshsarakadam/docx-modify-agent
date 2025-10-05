"""
Main entry point for the DOCX Modification Service
"""

import uvicorn
import argparse
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import app


def main():
    """Main function to start the service"""
    parser = argparse.ArgumentParser(description='DOCX Modification Service')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    parser.add_argument('--workers', type=int, default=1, help='Number of worker processes')
    
    args = parser.parse_args()
    
    print(f"Starting DOCX Modification Service on {args.host}:{args.port}")
    print(f"API documentation available at: http://{args.host}:{args.port}/docs")
    print(f"OpenAPI schema available at: http://{args.host}:{args.port}/openapi.json")
    
    uvicorn.run(
        "src.api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers
    )


if __name__ == "__main__":
    main()