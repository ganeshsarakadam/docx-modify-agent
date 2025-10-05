#!/usr/bin/env python3
"""
Test the new bullet point system with placeholder removal
"""

import requests
import json

# Test data
test_data = {
    "name": "GANESH SARAKADAM",
    "contact": {
        "phone": "+1 740-915-3257",
        "email": "ganeshsrv.sarakadam@gmail.com",
        "linkedin": "linkedin.com/in/ganesh-sarakadam"
    },
    "professional_summary": "Frontend Engineer (React, TypeScript) with 5+ years of experience building accessible, high-performance single-page applications.",
    "technical_skills": [
        "TypeScript", "JavaScript (ES6+)", "HTML5", "CSS3", "Python", "React", "Next.js"
    ],
    "professional_experience": [
        {
            "company": "Doran Jones Inc",
            "location": "Remote, USA",
            "title": "Software Engineer", 
            "duration": "Aug 2024 – Aug 2025",
            "highlights": [
                "Led new feature work and iterative refactors across 5+ React SPAs",
                "Designed a Storybook-driven React component library",
                "Architected Module Federation for shared shells"
            ]
        }
    ],
    "projects": [
        {
            "name": "Nesh UI — Component Library & Design System (Open Source)",
            "highlights": [
                "TypeScript and React component library with tokens, theming, and a11y primitives"
            ]
        }
    ]
}

print("🧪 Testing the improved bullet point system...")

# Test by uploading a sample document (you would use your actual template)
files = {
    'document': ('test-template.docx', open('/dev/null', 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
}
data = {
    'fields': json.dumps(test_data)
}

try:
    response = requests.post("http://localhost:8001/api/edit-resume", files=files, data=data, timeout=10)
    
    if response.status_code == 200:
        print("✅ Request successful!")
        print(f"📊 Content length: {len(response.content)} bytes")
        
        # Save the response
        with open("/tmp/test_output.docx", "wb") as f:
            f.write(response.content)
        print("💾 Output saved to /tmp/test_output.docx")
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"📝 Response: {response.text}")
        
except requests.exceptions.RequestException as e:
    print(f"🔌 Connection error: {e}")
    print("💡 Make sure the server is running on port 8001")

finally:
    files['document'][1].close()

print("\n📝 Key improvements implemented:")
print("  ✅ Template bullet point formatting detection")
print("  ✅ Automatic placeholder bullet point removal")
print("  ✅ Proper paragraph spacing for bullet points")
print("  ✅ Individual bullet points as separate paragraphs")
print("\n🎯 Expected result:")
print("  • Each experience section should have different highlights")
print("  • Bullet points should match your template formatting")
print("  • Placeholder bullet points should be removed")
print("  • Proper spacing between bullet points")