#!/usr/bin/env python3
"""
Test script to create a template that uses a single placeholder for all professional experience
"""

import requests
import json

# Test data
test_data = {
    "name": "Raju Sundharam",
    "contact": {
        "phone": "+1 740-915-3257",
        "email": "raju@example.com",
        "linkedin": "linkedin.com/in/ganesh-sarakadam"
    },
    "professional_summary": "Experienced software developer with expertise in full-stack development, Python, and modern web technologies.",
    "technical_skills": [
        "TypeScript", "JavaScript (ES6+)", "HTML5", "CSS3", "Python", "React", "Next.js", "Redux Toolkit", "Recoil", "Angular", "Tailwind CSS"
    ],
    "professional_experience": [
        {
            "company": "Tech Corp Inc",
            "location": "San Francisco, CA",
            "title": "Senior Software Engineer", 
            "duration": "Aug 2024 – Aug 2025",
            "highlights": [
                "Led development of microservices architecture serving 1M+ users",
                "Implemented CI/CD pipelines reducing deployment time by 60%",
                "Mentored 5 junior developers and conducted code reviews"
            ]
        },
        {
            "company": "Innovation Labs",
            "location": "New York, NY", 
            "title": "Software Engineer",
            "duration": "Mar 2021 – Aug 2022",
            "highlights": [
                "Built responsive web applications using React and TypeScript",
                "Optimized database queries improving performance by 40%",
                "Collaborated with cross-functional teams on agile projects"
            ]
        },
        {
            "company": "StartupXYZ",
            "location": "Austin, TX",
            "title": "Associate Software Engineer", 
            "duration": "Mar 2018 – Mar 2021",
            "highlights": [
                "Developed RESTful APIs using Python and FastAPI",
                "Implemented automated testing achieving 90% code coverage",
                "Participated in architectural decisions for scalable solutions"
            ]
        }
    ],
    "projects": [
        {
            "name": "E-commerce Platform",
            "highlights": [
                "Full-stack web application with payment integration",
                "Built using React, Node.js, and PostgreSQL"
            ]
        }
    ]
}

print("Creating template that uses {{PROFESSIONAL_EXPERIENCE}} placeholder...")

# Create template
response = requests.post("http://localhost:8000/create-resume-template")
if response.status_code == 200:
    with open("/tmp/single_placeholder_template.docx", "wb") as f:
        f.write(response.content)
    print("Template saved to /tmp/single_placeholder_template.docx")
    
    # Test with the template
    print("\nTesting the template with professional experience data...")
    
    files = {
        'document': ('template.docx', open('/tmp/single_placeholder_template.docx', 'rb'), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    }
    data = {
        'fields': json.dumps(test_data)
    }
    
    response = requests.post("http://localhost:8000/edit-resume", files=files, data=data)
    
    if response.status_code == 200:
        with open("/tmp/generated_resume_single.docx", "wb") as f:
            f.write(response.content)
        print("Generated resume saved to /tmp/generated_resume_single.docx")
        print(f"Replacements made: {response.headers.get('X-Replacements-Made', 'Unknown')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        
    files['document'][1].close()
else:
    print(f"Failed to create template: {response.status_code}")