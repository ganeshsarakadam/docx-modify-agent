# Resume Template Placeholder Guide - SHORT PLACEHOLDERS

## Problem Solved: Clean Templates with Short Placeholders! ✅

Instead of using long placeholders like `{{professional_experience.0.company}}` that take up too much vertical space, you can now use **short, clean placeholders**:

## Short Placeholder Mappings

### Basic Fields
- `{{name}}` → Full name
- `{{professional_summary}}` → Professional summary text
- `{{technical_skills}}` → All technical skills (comma-separated)

### Contact Information  
- `{{phone}}` → Phone number
- `{{email}}` → Email address
- `{{linkedin}}` → LinkedIn URL

### Professional Experience (Clean & Short!)
**First Job:**
- `{{company1}}` → First company name
- `{{location1}}` → First job location
- `{{title1}}` → First job title
- `{{duration1}}` → First job duration
- `{{highlights1}}` → First job highlights (bullet points)

**Second Job:**
- `{{company2}}` → Second company name
- `{{location2}}` → Second job location
- `{{title2}}` → Second job title
- `{{duration2}}` → Second job duration
- `{{highlights2}}` → Second job highlights

**Third Job:**
- `{{company3}}` → Third company name
- `{{location3}}` → Third job location
- `{{title3}}` → Third job title
- `{{duration3}}` → Third job duration
- `{{highlights3}}` → Third job highlights

### Projects
- `{{project1}}` → First project name
- `{{project1_highlights}}` → First project highlights
- `{{project2}}` → Second project name
- `{{project2_highlights}}` → Second project highlights

### Education (Static Content - No Placeholders Needed!)
Since your education won't change, just use static text in your template:

```
EDUCATION

Master of Science in Computer Science
Ohio University | August 2022 – May 2024

Bachelor of Technology in Computer Science
JNTUH | August 2014 – March 2018
```

## Clean Template Example

```
{{name}}
{{phone}} | {{email}} | {{linkedin}}

PROFESSIONAL SUMMARY
{{professional_summary}}

TECHNICAL SKILLS
{{technical_skills}}

PROFESSIONAL EXPERIENCE

{{title1}} at {{company1}}
{{location1}} | {{duration1}}
{{highlights1}}

{{title2}} at {{company2}}
{{location2}} | {{duration2}}
{{highlights2}}

{{title3}} at {{company3}}
{{location3}} | {{duration3}}
{{highlights3}}

PROJECTS

{{project1}}
{{project1_highlights}}

{{project2}}
{{project2_highlights}}

EDUCATION

Master of Science in Computer Science
Ohio University | August 2022 – May 2024

Bachelor of Technology in Computer Science
JNTUH | August 2014 – March 2018
```

## Benefits

✅ **Clean templates** - No more long placeholder text taking up space
✅ **Easy to read** - Short, intuitive placeholder names
✅ **Same functionality** - Maps to your exact JSON structure
✅ **Flexible** - You can still use long placeholders if needed

## Both Formats Work!

You can use either:
- **Short:** `{{company1}}` (recommended for clean templates)
- **Long:** `{{professional_experience.0.company}}` (still supported)

The system automatically maps short placeholders to your JSON structure!