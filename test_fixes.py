#!/usr/bin/env python3
"""
Test script to verify the fixes for placeholder issues and bullet point formatting
"""

import requests
import json

# Test data matching the user's example
test_data = {
    "name": "GANESH SARAKADAM",
    "contact": {
        "phone": "+1 740-915-3257",
        "email": "ganeshsrv.sarakadam@gmail.com",
        "linkedin": "linkedin.com/in/ganesh-sarakadam"
    },
    "professional_summary": "Frontend Engineer (React, TypeScript) with 5+ years of experience building accessible, high-performance single-page applications.",
    "technical_skills": [
        "TypeScript", "JavaScript (ES6+)", "HTML5", "CSS3", "Python", "React", "Next.js", "Redux Toolkit", "Recoil", "Angular", "Tailwind CSS"
    ],
    "professional_experience": [
        {
            "company": "Doran Jones Inc",
            "location": "Remote, USA",
            "title": "Software Engineer", 
            "duration": "Aug 2024 – Aug 2025",
            "highlights": [
                "Led new feature work and iterative refactors across 5+ React SPAs, aligned backlog with product goals and prioritized tech debt to keep velocity steady.",
                "Designed a Storybook-driven React component library (typed props, unidirectional data flow, templated components) that standardized UI across 4+ risk apps; cut integration issues 75%.",
                "Architected Module Federation for shared shells and independently deployed feature modules, improving release cadence and maintainability across compliance dashboards."
            ]
        },
        {
            "company": "Berkadia, Platform Development Team",
            "location": "Hyderabad, India",
            "title": "Software Engineer",
            "duration": "Mar 2021 – Aug 2022",
            "highlights": [
                "Refactored complex state management logic using TypeScript and Redux, improving code maintainability and simplifying asynchronous event handling in the ticketing workflow system.",
                "Built a reusable @mention component and form patterns, accelerated feature delivery and increased consistency across teams.",
                "Tuned Webpack/Babel for code-splitting and lazy-loading, ensured cross-browser/device support and improved bundle delivery in high-traffic environments."
            ]
        },
        {
            "company": "Berkadia, Platform Development Team",
            "location": "Hyderabad, India",
            "title": "Associate Software Engineer",
            "duration": "Mar 2018 – Mar 2021",
            "highlights": [
                "Designed an interactive property search interface with React and Elasticsearch, implementing lazy-loaded map tiles and listing components to achieve sub-second geospatial query results across 50K+ property listings and increase broker engagement by 30%.",
                "Piloted Recoil for localized state scenarios alongside Redux Toolkit, evaluated MUI vs. headless approaches for form-heavy screens and documented adoption guidance.",
                "Implemented a custom WebGL shader in a property-listing experience to render scenic map overlays inside a canvas-based view, improving visual clarity on dense geo layers."
            ]
        }
    ],
    "projects": [
        {
            "name": "Nesh UI — Component Library & Design System (Open Source)",
            "highlights": [
                "TypeScript and React component library with tokens, theming, a11y primitives, and Storybook docs, integrates Material Design concepts and MUI compatibility patterns."
            ]
        },
        {
            "name": "Browser Agent — Headless Automation & Web App",
            "highlights": [
                "Built a Puppeteer/Headless Chrome agent with a React/TypeScript dashboard to orchestrate scripted tasks, report statuses, and replay sessions via a custom canvas/video player with frame-accurate scrubbing."
            ]
        }
    ]
}

def test_with_template():
    """Test with the corrected template"""
    print("🧪 Testing fixes with corrected template...")
    
    try:
        # Read the corrected template as text to create a DOCX template
        with open('corrected_template.txt', 'r') as f:
            template_content = f.read()
        
        print("📄 Template content preview:")
        print(template_content[:500] + "..." if len(template_content) > 500 else template_content)
        
        # First create a resume template
        print("\n📋 Creating resume template...")
        response = requests.post("http://localhost:8001/api/create-resume-template")
        if response.status_code == 200:
            template_path = "/tmp/test_template.docx"
            with open(template_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Template created: {template_path}")
        else:
            print(f"❌ Failed to create template: {response.status_code}")
            return
        
        # Test the template with our data
        print("\n🔄 Processing resume with test data...")
        files = {
            'document': ('template.docx', open(template_path, 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        data = {
            'fields': json.dumps(test_data)
        }
        
        response = requests.post("http://localhost:8001/api/edit-resume", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            output_path = "/tmp/generated_resume_fixed.docx"
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Resume generated: {output_path}")
            
            # Print headers for debugging
            print("\n📊 Response headers:")
            replacements = response.headers.get('X-Replacements-Made', 'Unknown')
            validation = response.headers.get('X-Validation-Results', '{}')
            errors = response.headers.get('X-Errors', '[]')
            
            print(f"  Replacements made: {replacements}")
            print(f"  Validation results: {validation}")
            print(f"  Errors: {errors}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text}")
            
        files['document'][1].close()
        
    except requests.exceptions.RequestException as e:
        print(f"🔌 Connection error: {e}")
        print("💡 Make sure the server is running on port 8001")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_placeholder_removal():
    """Test if placeholder bullet points are being removed"""
    print("\n🧹 Testing placeholder removal...")
    
    # Create simple test data with missing projects to see if placeholders are removed
    simple_data = {
        "name": "Test User",
        "contact": {
            "phone": "+1 123-456-7890",
            "email": "test@example.com",
            "linkedin": "linkedin.com/in/test"
        },
        "professional_summary": "Test summary",
        "technical_skills": ["Python", "JavaScript"],
        "professional_experience": [
            {
                "company": "Test Company",
                "location": "Test Location",
                "title": "Test Title",
                "duration": "2020-2024",
                "highlights": [
                    "Test highlight 1",
                    "Test highlight 2"
                ]
            }
        ]
        # Note: No projects data - this should trigger placeholder removal
    }
    
    try:
        response = requests.post("http://localhost:8001/api/create-resume-template")
        if response.status_code == 200:
            template_path = "/tmp/simple_test_template.docx"
            with open(template_path, "wb") as f:
                f.write(response.content)
        
        files = {
            'document': ('template.docx', open(template_path, 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        data = {
            'fields': json.dumps(simple_data)
        }
        
        response = requests.post("http://localhost:8001/api/edit-resume", files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            output_path = "/tmp/simple_test_output.docx"
            with open(output_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Simple test output: {output_path}")
            
            replacements = response.headers.get('X-Replacements-Made', 'Unknown')
            print(f"📊 Replacements made: {replacements}")
        else:
            print(f"❌ Simple test failed: {response.status_code}")
            
        files['document'][1].close()
        
    except Exception as e:
        print(f"❌ Simple test error: {e}")

if __name__ == "__main__":
    print("🚀 Testing DOCX fixes for placeholder and formatting issues")
    print("=" * 60)
    
    test_with_template()
    test_placeholder_removal()
    
    print("\n🎯 Expected improvements:")
    print("  ✅ No 'project2_highlights' placeholder in output")
    print("  ✅ No 'Add highlights with this style' placeholder bullets")
    print("  ✅ Consistent bullet point formatting")
    print("  ✅ Proper spacing between sections")
    print("\n📁 Check the generated files in /tmp/ to verify the fixes!")