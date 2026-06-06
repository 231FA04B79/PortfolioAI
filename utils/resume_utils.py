import re
from PyPDF2 import PdfReader


def analyze_resume_pdf(resume_file):
    reader = PdfReader(resume_file)
    text = ' '.join(page.extract_text() or '' for page in reader.pages)
    lower_text = text.lower()

    sections = {
        'education': 'education' in lower_text,
        'skills': 'skills' in lower_text or 'technical skills' in lower_text,
        'projects': 'project' in lower_text,
        'certifications': 'certification' in lower_text or 'certificate' in lower_text,
        'experience': 'experience' in lower_text,
    }
    found = sum(sections.values())
    score = int(found / len(sections) * 100)
    missing = [name for name, present in sections.items() if not present]

    suggestions = []
    if 'education' in missing:
        suggestions.append('Add a clear education section with school, field, and dates.')
    if 'skills' in missing:
        suggestions.append('Include a dedicated skills section with relevant keywords.')
    if 'experience' in missing:
        suggestions.append('Add project or internship experience with measurable results.')
    if 'certifications' in missing:
        suggestions.append('List certifications with issuing organizations and dates.')
    if 'projects' in missing:
        suggestions.append('Describe projects and the technologies you used.')

    return {
        'resume_score': score,
        'missing_sections': missing,
        'suggestions': suggestions,
    }


def detect_education_details_helper(degree_text, score_text):
    deg_lower = degree_text.lower()
    edu_type = 'Other'
    if any(k in deg_lower for k in ['ssc', '10th', 'matriculation', 'high school', 'secondary school']):
        edu_type = 'SSC'
    elif any(k in deg_lower for k in ['intermediate', '12th', 'hsc', 'senior secondary', '10+2']):
        edu_type = 'Intermediate'
    elif 'diploma' in deg_lower:
        edu_type = 'Diploma'
    elif any(k in deg_lower for k in ['b.tech', 'b.e.', 'bachelor', 'b.s', 'b.sc', 'bba', 'undergraduate', 'bca', 'cse', 'it']):
        edu_type = 'Undergraduate'
    elif any(k in deg_lower for k in ['m.tech', 'm.e.', 'master', 'm.s', 'm.sc', 'mba', 'postgraduate', 'mca']):
        edu_type = 'Postgraduate'
    elif any(k in deg_lower for k in ['ph.d', 'phd', 'doctorate']):
        edu_type = 'PhD'
        
    scoring_type = 'CGPA'
    score_val = ""
    
    if score_text:
        score_val = score_text.strip()
        if '%' in score_val or any(k in score_val.lower() for k in ['percent', 'percentage']):
            scoring_type = 'Percentage'
        elif any(k in score_val.lower() for k in ['cgpa', 'gpa']):
            scoring_type = 'CGPA'
        else:
            # Check numeric range
            num_match = re.search(r'[\d\.]+', score_val)
            if num_match:
                try:
                    val = float(num_match.group(0))
                    if val > 10.0:
                        scoring_type = 'Percentage'
                    else:
                        scoring_type = 'CGPA'
                except ValueError:
                    pass
                    
        # Extract only numeric value or decimal
        num_only_match = re.search(r'([\d\.]+)', score_val)
        if num_only_match:
            score_val = num_only_match.group(1).strip()
            
    return edu_type, scoring_type, score_val


def parse_resume_pdf_content(resume_file):
    reader = PdfReader(resume_file)
    text = '\n'.join(page.extract_text() or '' for page in reader.pages)
    
    # Normalize line endings and split
    text = text.replace('\r', '\n')
    lines = [line.strip() for line in text.split('\n')]
    
    # Section markers map
    headings_map = {
        'education': ['education', 'academic background', 'academic details', 'educational qualifications', 'qualifications', 'qualification', 'academics', 'academic profile'],
        'skills': ['skills', 'technical skills', 'key skills', 'core competencies', 'skills & technologies', 'skills & tools', 'technologies', 'tools', 'languages & technologies', 'technical expertise'],
        'projects': ['projects', 'key projects', 'personal projects', 'academic projects', 'recent projects', 'technical projects'],
        'certifications': ['certifications', 'certificates', 'courses', 'licenses & certifications', 'licenses'],
        'achievements': ['achievements', 'accomplishments', 'awards', 'honors & awards', 'honors', 'extra-curricular activities'],
        'experience': ['experience', 'work experience', 'professional experience', 'employment history', 'internships', 'employment']
    }
    
    section_lines = {
        'header': [],
        'education': [],
        'skills': [],
        'projects': [],
        'certifications': [],
        'achievements': [],
        'experience': []
    }
    
    current_sec = 'header'
    
    # Segment text into sections
    for line in lines:
        if not line:
            continue
        
        # Clean line for matching
        clean_line = re.sub(r'^[\d\.\-\•\*\s\u2022\u25cf]+', '', line).strip().lower()
        
        # Check if line is a section heading
        found_heading = False
        for sec_name, headings in headings_map.items():
            if clean_line in headings or (len(clean_line) < 30 and any(clean_line == h for h in headings)):
                current_sec = sec_name
                found_heading = True
                break
                
        if found_heading:
            # Skip the heading line itself so it doesn't get saved as data
            continue
            
        section_lines[current_sec].append(line)
        
    def is_noise_line(l):
        lower_l = l.strip().lower()
        for headings in headings_map.values():
            if lower_l in headings:
                return True
        return False

    # Extract Profile Header
    header_text = '\n'.join(section_lines['header'])
    
    # Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    email = email_match.group(0) if email_match else ""
    
    # Phone
    phone_match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{4}', text)
    phone = phone_match.group(0) if phone_match else ""
    
    # Location
    location = ""
    location_match = re.search(r'\b([a-zA-Z\s]{3,30}),\s*([a-zA-Z\s]{2,20})\b', header_text)
    if location_match:
        loc_candidate = location_match.group(0)
        if not any(w in loc_candidate.lower() for w in ['email', 'phone', 'mobile', 'github', 'linkedin', 'cv', 'resume']):
            location = loc_candidate
            
    # URLs
    github_match = re.search(r'(https?://)?(www\.)?github\.com/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
    github_url = github_match.group(0) if github_match else ""
    
    linkedin_match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+', text, re.IGNORECASE)
    linkedin_url = linkedin_match.group(0) if linkedin_match else ""
    
    portfolio_url = ""
    urls = re.findall(r'https?://[^\s/$.?#].[^\s]*', text)
    for url in urls:
        if 'github.com' not in url.lower() and 'linkedin.com' not in url.lower():
            portfolio_url = url
            break

    # Name: First non-empty, non-contact line of header that is 2-4 words
    name = ""
    for line in section_lines['header']:
        line_s = line.strip()
        if not line_s or is_noise_line(line_s):
            continue
        if '@' in line_s or any(kw in line_s.lower() for kw in ['github.com', 'linkedin.com', 'http', 'phone', 'mobile']):
            continue
        words = line_s.split()
        if 2 <= len(words) <= 4 and re.match(r'^[a-zA-Z\s\.]+$', line_s):
            name = line_s
            break
    if not name:
        name = "Candidate Name"
        
    # Extract Education
    edu_list = []
    degree_keywords = [
        r'\bB\.?Tech\b', r'\bM\.?Tech\b', r'\bB\.?E\.?\b', r'\bM\.?E\.?\b', 
        r'\bB\.?S\b', r'\bM\.?S\b', r'\bB\.?Sc\b', r'\bM\.?Sc\b', 
        r'\bBBA\b', r'\bMBA\b', r'\bPh\.?D\b', r'\bBachelor\b', r'\bMaster\b', 
        r'\bDiploma\b', r'\bSSC\b', r'\bHSC\b', r'\bIntermediate\b', r'\bHigh School\b'
    ]
    
    current_edu = None
    for line in section_lines['education']:
        line_s = line.strip()
        if not line_s or is_noise_line(line_s):
            continue
            
        is_new_degree = False
        degree_found = ""
        for deg_pat in degree_keywords:
            match = re.search(deg_pat, line_s, re.IGNORECASE)
            if match:
                is_new_degree = True
                degree_found = match.group(0)
                break
                
        if is_new_degree or not current_edu:
            if current_edu:
                # Resolve details for the previous one before saving
                edu_type, scoring_type, score_val = detect_education_details_helper(current_edu['degree'], current_edu['raw_score'])
                current_edu['education_type'] = edu_type
                current_edu['scoring_type'] = scoring_type
                current_edu['score_value'] = score_val
                current_edu['cgpa'] = score_val
                edu_list.append(current_edu)
            
            # CGPA / percentage
            cgpa_match = re.search(r'\b(cgpa|gpa|marks|percentage|percent):?\s*([\d\.]+(?:\s*%)?|\d+\/\d+)\b', line_s, re.IGNORECASE)
            cgpa = cgpa_match.group(2) if cgpa_match else ""
            if not cgpa:
                pct_match = re.search(r'\b(\d{2}(?:\.\d+)?\s*%)\b', line_s)
                if pct_match:
                    cgpa = pct_match.group(1)
                else:
                    gpa_val_match = re.search(r'\b([5-9]\.\d{1,2}|10\.0)\b', line_s)
                    if gpa_val_match:
                        cgpa = gpa_val_match.group(1)
            
            # Graduation Year
            year_match = re.search(r'\b(20|19)\d{2}\b', line_s)
            year = year_match.group(0) if year_match else ""
            
            # College
            college_name = ""
            college_keywords = ['college', 'university', 'school', 'institute', 'academy', 'iit', 'nit', 'bits', 'institution']
            for keyword in college_keywords:
                if keyword in line_s.lower():
                    college_name = line_s
                    break
            
            current_edu = {
                'degree': degree_found or line_s[:100],
                'college_name': college_name or "University/College",
                'completion_year': year or "2026",
                'raw_score': cgpa,
                'cgpa': cgpa,
                'education_type': 'Other',
                'scoring_type': 'CGPA',
                'score_value': ''
            }
        else:
            if current_edu['college_name'] == "University/College":
                college_keywords = ['college', 'university', 'school', 'institute', 'academy', 'iit', 'nit', 'bits', 'institution']
                if any(kw in line_s.lower() for kw in college_keywords):
                    current_edu['college_name'] = line_s[:250]
            
            if not current_edu['raw_score']:
                cgpa_match = re.search(r'\b(cgpa|gpa|marks|percentage|percent):?\s*([\d\.]+(?:\s*%)?|\d+\/\d+)\b', line_s, re.IGNORECASE)
                if cgpa_match:
                    current_edu['raw_score'] = cgpa_match.group(2)
                else:
                    pct_match = re.search(r'\b(\d{2}(?:\.\d+)?\s*%)\b', line_s)
                    if pct_match:
                        current_edu['raw_score'] = pct_match.group(1)
                    else:
                        gpa_val_match = re.search(r'\b([5-9]\.\d{1,2}|10\.0)\b', line_s)
                        if gpa_val_match:
                            current_edu['raw_score'] = gpa_val_match.group(1)
                            
            if current_edu['completion_year'] == "2026":
                year_match = re.search(r'\b(20|19)\d{2}\b', line_s)
                if year_match:
                    current_edu['completion_year'] = year_match.group(0)
                    
    if current_edu:
        edu_type, scoring_type, score_val = detect_education_details_helper(current_edu['degree'], current_edu['raw_score'])
        current_edu['education_type'] = edu_type
        current_edu['scoring_type'] = scoring_type
        current_edu['score_value'] = score_val
        current_edu['cgpa'] = score_val
        edu_list.append(current_edu)
        
    clean_edu_list = []
    for edu in edu_list:
        if edu['degree'].lower() in ['education', 'academics', 'academic details', 'educational qualifications']:
            continue
        clean_edu_list.append(edu)

    # Extract Skills
    extracted_skills = []
    skills_pool = [
        'Python', 'Django', 'Flask', 'FastAPI', 'JavaScript', 'HTML', 'CSS', 'React', 'Angular', 
        'Vue', 'Node.js', 'Express', 'TypeScript', 'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 
        'SQLite', 'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'GitHub', 'Java', 'C++', 'C#', 
        'PHP', 'Ruby', 'Rust', 'Linux', 'Pandas', 'NumPy', 'TensorFlow', 'PyTorch', 'REST APIs',
        'C', 'Next.js', 'Bootstrap', 'Tailwind', 'Sass', 'Webpack', 'GCP', 'Firebase', 'Oracle',
        'Redis', 'GraphQL', 'JIRA', 'Confluence', 'Agile', 'Scrum', 'CI/CD', 'Jenkins', 'Postman',
        'Selenium', 'Jest', 'Mocha', 'Redux', 'jQuery', 'Nginx', 'Apache', 'Docker Compose'
    ]
    
    skills_text = '\n'.join(section_lines['skills']).lower()
    for skill in skills_pool:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if skill in ['C++', 'C#']:
            pattern = re.escape(skill.lower())
        if re.search(pattern, skills_text):
            extracted_skills.append(skill)
            
    for line in section_lines['skills']:
        if ',' in line:
            parts = line.split(',')
            for p in parts:
                p_clean = p.strip()
                if len(p_clean) < 30 and p_clean and p_clean.lower() not in ['skills', 'technical skills', 'key skills']:
                    p_clean = p_clean.title()
                    if p_clean not in extracted_skills:
                        extracted_skills.append(p_clean)

    # Extract Projects
    proj_list = []
    current_proj = None
    project_title_keywords = ['project', 'system', 'app', 'application', 'website', 'platform', 'tool', 'engine']
    
    for line in section_lines['projects']:
        line_s = line.strip()
        if not line_s or is_noise_line(line_s):
            continue
            
        is_title = False
        clean_text_only = re.sub(r'^[\d\.\-\•\*\s\u2022\u25cf]+', '', line_s).strip()
        words = clean_text_only.split()
        
        if 1 <= len(words) <= 6 and (any(kw in clean_text_only.lower() for kw in project_title_keywords) or clean_text_only[0].isupper()):
            if not any(s.lower() in clean_text_only.lower() for s in ['technologies', 'tech stack', 'skills', 'tools']):
                is_title = True
                
        if is_title or not current_proj:
            if current_proj:
                proj_list.append(current_proj)
                
            git_match = re.search(r'(https?://)?(www\.)?github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+', line_s, re.IGNORECASE)
            git_link = git_match.group(0) if git_match else ""
            
            techs = ""
            bracket_match = re.search(r'\(([^)]+)\)', clean_text_only)
            if bracket_match:
                techs = bracket_match.group(1)
                
            duration_match = re.search(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?\s*\d{4}\s*-\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?\s*\d{4}\b', line_s, re.IGNORECASE)
            duration = duration_match.group(0) if duration_match else ""
            
            title_val = clean_text_only
            if bracket_match:
                title_val = title_val.replace(bracket_match.group(0), "").strip()
            if duration_match:
                title_val = title_val.replace(duration_match.group(0), "").strip()
            title_val = re.sub(r'^[^a-zA-Z0-9]+', '', title_val).strip()
            
            current_proj = {
                'title': title_val or "Project Title",
                'description': "",
                'tech_stack': techs or "",
                'github_link': git_link,
                'duration': duration or ""
            }
        else:
            clean_line = re.sub(r'^[\d\.\-\•\*\s\u2022\u25cf]+', '', line_s).strip()
            if any(label in line_s.lower() for label in ['technologies:', 'tech stack:', 'skills used:', 'built with:']):
                tech_val = re.sub(r'^(?:technologies|tech stack|skills used|built with):', '', line_s, flags=re.IGNORECASE).strip()
                current_proj['tech_stack'] = tech_val
            else:
                if current_proj['description']:
                    current_proj['description'] += " " + clean_line
                else:
                    current_proj['description'] = clean_line
                    
            git_match = re.search(r'(https?://)?(www\.)?github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+', line_s, re.IGNORECASE)
            if git_match and not current_proj['github_link']:
                current_proj['github_link'] = git_match.group(0)
                
            duration_match = re.search(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?\s*\d{4}\s*-\s*(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?\s*\d{4}\b', line_s, re.IGNORECASE)
            if duration_match and not current_proj['duration']:
                current_proj['duration'] = duration_match.group(0)
                
    if current_proj:
        proj_list.append(current_proj)
        
    clean_proj_list = []
    for proj in proj_list:
        if proj['title'].lower() in ['projects', 'key projects', 'personal projects', 'academic projects']:
            continue
        if proj['tech_stack']:
            matched_techs = []
            for skill in skills_pool:
                if skill.lower() in proj['tech_stack'].lower():
                    matched_techs.append(skill)
            if matched_techs:
                proj['tech_stack'] = ', '.join(matched_techs)
        clean_proj_list.append(proj)

    # Extract Certifications
    cert_list = []
    current_cert = None
    
    for line in section_lines['certifications']:
        line_s = line.strip()
        if not line_s or is_noise_line(line_s):
            continue
            
        clean_line = re.sub(r'^[\d\.\-\•\*\s\u2022\u25cf]+', '', line_s).strip()
        cred_match = re.search(r'\b(?:credential id|id|verification):?\s*([a-zA-Z0-9_-]+)\b', line_s, re.IGNORECASE)
        date_match = re.search(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)?\s*(20|19)\d{2}\b', line_s, re.IGNORECASE)
        
        issuer = ""
        issuers_pool = ['Google', 'AWS', 'Amazon', 'Microsoft', 'IBM', 'Coursera', 'Udemy', 'Oracle', 'Cisco', 'Stanford', 'Meta']
        for iss in issuers_pool:
            if iss.lower() in line_s.lower():
                issuer = iss
                break
                
        if not cred_match and len(clean_line) > 5 and not current_cert:
            current_cert = {
                'certificate_name': clean_line,
                'issuing_organization': issuer or "Coursera / Udemy",
                'issue_date': date_match.group(0) if date_match else "2025",
                'credential_id': cred_match.group(1) if cred_match else ""
            }
        elif current_cert:
            if issuer and current_cert['issuing_organization'] == "Coursera / Udemy":
                current_cert['issuing_organization'] = issuer
            if date_match and current_cert['issue_date'] == "2025":
                current_cert['issue_date'] = date_match.group(0)
            if cred_match:
                current_cert['credential_id'] = cred_match.group(1)
            
            if not cred_match and not date_match and current_cert['issuing_organization'] == "Coursera / Udemy":
                current_cert['issuing_organization'] = clean_line[:100]
                
            cert_list.append(current_cert)
            current_cert = None
            
    if current_cert:
        cert_list.append(current_cert)
        
    clean_cert_list = []
    for c in cert_list:
        if c['certificate_name'].lower() in ['certifications', 'certificates', 'courses']:
            continue
        clean_cert_list.append(c)

    # Extract Achievements
    ach_list = []
    for line in section_lines['achievements']:
        line_s = line.strip()
        if not line_s or is_noise_line(line_s):
            continue
            
        clean_line = re.sub(r'^[\d\.\-\•\*\s\u2022\u25cf]+', '', line_s).strip()
        if clean_line.lower() in ['achievements', 'accomplishments', 'awards', 'honors']:
            continue
            
        title = clean_line
        desc = "Awarded for exceptional performance."
        if ':' in clean_line:
            parts = clean_line.split(':', 1)
            title = parts[0].strip()
            desc = parts[1].strip()
            
        ach_list.append({
            'title': title,
            'description': desc,
            'award_name': title,
            'competition_name': "Competition"
        })

    return {
        'name': name,
        'email': email,
        'phone': phone,
        'location': location or "City, Country",
        'github': github_url,
        'linkedin': linkedin_url,
        'portfolio_website': portfolio_url,
        'skills': extracted_skills,
        'education': clean_edu_list[:5],
        'projects': clean_proj_list[:5],
        'certifications': clean_cert_list[:5],
        'achievements': ach_list[:5]
    }
