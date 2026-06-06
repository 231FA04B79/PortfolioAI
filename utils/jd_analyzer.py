import re
from utils.scoring_utils import get_github_score, get_portfolio_score, get_placement_readiness

SKILLS_POOL = [
    'Python', 'Django', 'Flask', 'FastAPI', 'JavaScript', 'HTML', 'CSS', 'React', 'Angular', 
    'Vue', 'Node.js', 'Express', 'TypeScript', 'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 
    'SQLite', 'AWS', 'Azure', 'Docker', 'Kubernetes', 'Git', 'GitHub', 'Java', 'C++', 'C#', 
    'PHP', 'Ruby', 'Rust', 'Linux', 'Pandas', 'NumPy', 'TensorFlow', 'PyTorch', 'REST APIs',
    'Next.js', 'Bootstrap', 'Tailwind', 'Sass', 'Webpack', 'GCP', 'Firebase', 'Oracle',
    'Redis', 'GraphQL', 'JIRA', 'Confluence', 'Agile', 'Scrum', 'CI/CD', 'Jenkins', 'Postman',
    'Selenium', 'Jest', 'Mocha', 'Redux', 'jQuery', 'Nginx', 'Apache', 'Docker Compose'
]

TECH_POOL = [
    'Django', 'Flask', 'FastAPI', 'React', 'Angular', 'Vue', 'Node.js', 'Express', 
    'PostgreSQL', 'MySQL', 'MongoDB', 'SQLite', 'AWS', 'Azure', 'Docker', 'Kubernetes', 
    'TensorFlow', 'PyTorch', 'Next.js', 'Tailwind', 'Redis', 'GraphQL', 'CI/CD', 'Jenkins', 
    'Nginx', 'Docker Compose', 'GitHub Actions', 'Google Cloud', 'Serverless', 'Microservices'
]

CERTS_POOL = [
    'AWS Certified Cloud Practitioner', 'AWS Certified Solutions Architect', 'AWS Certified Developer',
    'Google Cloud Associate Cloud Engineer', 'Google Cloud Professional Cloud Architect',
    'Microsoft Certified: Azure Fundamentals', 'Microsoft Certified: Azure Developer Associate',
    'Certified Kubernetes Administrator', 'CKA', 'Certified Kubernetes Application Developer', 'CKAD',
    'Project Management Professional', 'PMP', 'Certified ScrumMaster', 'CSM', 'CCNA', 'CompTIA Security+',
    'CompTIA Network+', 'Oracle Certified Professional', 'Python Institute Certified Associate'
]

SOFT_SKILLS_POOL = [
    'Communication', 'Leadership', 'Teamwork', 'Collaboration', 'Problem Solving', 
    'Adaptability', 'Time Management', 'Critical Thinking', 'Presentation', 'Creativity',
    'Active Listening', 'Conflict Resolution', 'Emotional Intelligence', 'Decision Making',
    'Work Ethic', 'Interpersonal Skills', 'Attention to Detail', 'Mentoring'
]


def parse_job_description(jd_text):
    """
    Parses a job description to extract skills, technologies, experience, certifications, keywords, and soft skills.
    """
    if not jd_text:
        return {
            'skills': [],
            'technologies': [],
            'experience': 'Not Specified',
            'certifications': [],
            'keywords': [],
            'soft_skills': []
        }

    lower_text = jd_text.lower()
    
    # 1. Extract Skills
    extracted_skills = []
    for skill in SKILLS_POOL:
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if skill in ['C++', 'C#']:
            pattern = re.escape(skill.lower())
        if re.search(pattern, lower_text):
            extracted_skills.append(skill)
            
    # 2. Extract Technologies
    extracted_techs = []
    for tech in TECH_POOL:
        pattern = r'\b' + re.escape(tech.lower()) + r'\b'
        if re.search(pattern, lower_text):
            extracted_techs.append(tech)

    # 3. Extract Experience
    experience_text = 'Not Specified'
    # Match phrases like "3+ years of experience", "2-5 years", "1 year exp", etc.
    exp_matches = re.findall(r'\b(\d+(?:\s*[-+]\s*\d+)?)\s*(?:years?|yrs?)\b.*?(?:experience|exp)\b', lower_text)
    if exp_matches:
        experience_text = f"{exp_matches[0]} Years Required"
    else:
        # Alt check
        exp_matches_alt = re.findall(r'\b(?:experience|exp)\b.*?\b(\d+(?:\s*[-+]\s*\d+)?)\s*(?:years?|yrs?)\b', lower_text)
        if exp_matches_alt:
            experience_text = f"{exp_matches_alt[0]} Years Required"

    # 4. Extract Certifications
    extracted_certs = []
    for cert in CERTS_POOL:
        pattern = r'\b' + re.escape(cert.lower()) + r'\b'
        if re.search(pattern, lower_text):
            extracted_certs.append(cert)
            
    # 5. Extract Soft Skills
    extracted_soft = []
    for ss in SOFT_SKILLS_POOL:
        pattern = r'\b' + re.escape(ss.lower()) + r'\b'
        if re.search(pattern, lower_text):
            extracted_soft.append(ss)

    # 6. Keywords (Common technical context terms found in description)
    keywords_pool = [
        'RESTful', 'Microservices', 'System Design', 'Algorithms', 'Data Structures', 
        'Object-Oriented', 'OOP', 'Agile', 'Scrum', 'CI/CD', 'Unit Testing', 'Deployment', 
        'Scalability', 'Debugging', 'Optimization', 'Cloud Native', 'Responsive Design', 
        'Database Normalization', 'API Integration', 'Version Control', 'Git Flow'
    ]
    extracted_keywords = []
    for kw in keywords_pool:
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, lower_text):
            extracted_keywords.append(kw)

    # Fallbacks if extraction is too empty
    if not extracted_skills:
        extracted_skills = ['Software Engineering', 'Problem Solving']
    if not extracted_techs:
        extracted_techs = ['Git']

    return {
        'skills': extracted_skills,
        'technologies': extracted_techs,
        'experience': experience_text,
        'certifications': extracted_certs,
        'keywords': extracted_keywords,
        'soft_skills': extracted_soft
    }


def compute_ats_match_details(user, jd_data):
    """
    Computes candidate job matching metrics by comparing user profile against parsed JD requirements.
    """
    user_skills_qs = user.skills.all()
    user_skills = [s.name.lower() for s in user_skills_qs]
    
    # Get user project tech list
    user_project_techs = []
    for p in user.projects.all():
        if p.tech_stack:
            user_project_techs.extend([t.strip().lower() for t in p.tech_stack.split(',') if t.strip()])
            
    user_certs = [c.certificate_name.lower() for c in user.certifications.all()]
    
    # Combine skills and project techs for maximum matching capacity
    all_user_keywords = set(user_skills + user_project_techs)

    required_skills = jd_data.get('skills', [])
    required_techs = jd_data.get('technologies', [])
    required_certs = jd_data.get('certifications', [])
    
    # Matched vs Missing Skills
    matched_skills = [s for s in required_skills if s.lower() in all_user_keywords]
    missing_skills = [s for s in required_skills if s.lower() not in all_user_keywords]

    # Matched vs Missing Technologies
    matched_techs = [t for t in required_techs if t.lower() in all_user_keywords]
    missing_techs = [t for t in required_techs if t.lower() not in all_user_keywords]

    # Matched vs Missing Certifications
    matched_certs = []
    missing_certs = []
    if required_certs:
        for c in required_certs:
            # Check substring match
            found = False
            for uc in user_certs:
                if c.lower() in uc or uc in c.lower():
                    found = True
                    break
            if found:
                matched_certs.append(c)
            else:
                missing_certs.append(c)

    # 1. Skills & Tech Match Score (50%)
    total_req_items = len(required_skills) + len(required_techs)
    matched_req_items = len(matched_skills) + len(matched_techs)
    skills_score = (matched_req_items / total_req_items * 50) if total_req_items > 0 else 50

    # 2. Certifications Score (15%)
    if not required_certs:
        certs_score = 15  # Default full score if no certs are required
    else:
        certs_score = (len(matched_certs) / len(required_certs) * 15)

    # 3. Experience & Readiness Score (15%)
    readiness = get_placement_readiness(user)
    experience_score = (readiness / 100 * 15)

    # 4. GitHub Score (10%)
    g_score = get_github_score(user)
    if g_score >= 70:
        github_points = 10
    elif g_score >= 40:
        github_points = 7
    else:
        github_points = (g_score / 10)

    # 5. Portfolio Section Score (10%)
    p_score = get_portfolio_score(user)
    portfolio_points = (p_score / 10)

    # Calculate aggregate match score
    match_score = int(skills_score + certs_score + experience_score + github_points + portfolio_points)
    match_score = min(100, max(0, match_score))

    # Generate Personalized Recommendations
    recommendations = []
    if missing_skills:
        rec_skills_limit = missing_skills[:3]
        recommendations.append(f"Add missing skill keywords: {', '.join(rec_skills_limit)}.")
        for ms in rec_skills_limit:
            recommendations.append(f"Acquire proficiency in {ms} to increase keyword density.")
            
    if missing_techs:
        rec_techs_limit = missing_techs[:2]
        for mt in rec_techs_limit:
            recommendations.append(f"Build a repository or project applying {mt} web integrations.")

    if missing_certs:
        recommendations.append(f"Prepare for certification: {missing_certs[0]} to verify cloud credentials.")

    if g_score < 50:
        recommendations.append("Increase your GitHub ranking by syncing commits and project repositories.")
    if readiness < 80:
        recommendations.append("Enhance placement readiness index by adding achievements and completing profile details.")

    if not recommendations:
        recommendations.append("Your profile is fully optimized for this role! Maintain consistency and keep coding.")

    return {
        'match_score': match_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'matched_technologies': matched_techs,
        'missing_technologies': missing_techs,
        'matched_certifications': matched_certs,
        'missing_certifications': missing_certs,
        'recommendations': recommendations
    }


def generate_learning_roadmap_steps(missing_skills, target_role="Developer"):
    """
    Generates a week-by-week learning roadmap based on missing skills.
    """
    steps = []
    
    # Analyze missing skills
    missing_lower = [s.lower() for s in missing_skills]
    
    # 1. Backend / Cloud roadmap path
    if any(s in missing_lower for s in ['docker', 'aws', 'kubernetes', 'ci/cd', 'nginx', 'docker compose']):
        steps = [
            {'week': 1, 'title': 'Docker Containerization Fundamentals', 'desc': 'Learn Docker architecture, write multi-stage Dockerfiles, build images, and run local containers.'},
            {'week': 2, 'title': 'Docker Compose Orchestration', 'desc': 'Set up docker-compose files to link multi-container backend apps with custom databases and caching layers.'},
            {'week': 3, 'title': 'Cloud Infrastructure Deployments (AWS/GCP)', 'desc': 'Deploy containerized web services, learn AWS EC2, S3 bucket storage, and configure basic cloud firewalls.'},
            {'week': 4, 'title': 'Automated Pipelines & CI/CD workflows', 'desc': 'Configure build automation using GitHub Actions to run linters, unit tests, and trigger container deployments on commits.'}
        ]
    # 2. Frontend roadmap path
    elif any(s in missing_lower for s in ['javascript', 'react', 'typescript', 'next.js', 'tailwind', 'redux', 'angular', 'vue']):
        steps = [
            {'week': 1, 'title': 'Advanced Modern JavaScript & TypeScript', 'desc': 'Master ES6+ concepts, asynchronous handlers, API promises, typing annotations, and interface definitions.'},
            {'week': 2, 'title': 'SPA Framework Architecture (React/Next.js)', 'desc': 'Understand component lifecycle, props rendering, state hooks, and routing setups.'},
            {'week': 3, 'title': 'State Management & API Integrations', 'desc': 'Learn Redux/Context APIs to manage global states, and link responsive forms with JSON endpoints.'},
            {'week': 4, 'title': 'Aesthetics Optimization & Frontend Deployment', 'desc': 'Apply modern styling, set up SEO tags, and deploy the application to Vercel/Netlify hosting services.'}
        ]
    # 3. DB & Django roadmap path
    elif any(s in missing_lower for s in ['django', 'python', 'sql', 'postgresql', 'mysql', 'apis', 'rest apis']):
        steps = [
            {'week': 1, 'title': 'Python OOP & REST API Basics', 'desc': 'Practice Object-Oriented Programming, and build standard CRUD APIs with HTTP request/response payloads.'},
            {'week': 2, 'title': 'Django Framework Architecture', 'desc': 'Understand models, views, URL configurations, forms, and admin interface integrations.'},
            {'week': 3, 'title': 'Database Design & SQL Optimization', 'desc': 'Design normalized schemas in PostgreSQL/MySQL, write raw SQL queries, and manage migrations.'},
            {'week': 4, 'title': 'Django Project Deployment', 'desc': 'Set up production environment variables, configure static files, and deploy to a cloud server.'}
        ]
    # 4. Fallback default 4-week roadmap
    else:
        steps = [
            {'week': 1, 'title': 'Advanced Software Architecture & Refactoring', 'desc': 'Learn OOP design patterns, clean code principles, and refactor existing projects.'},
            {'week': 2, 'title': 'Testing & CI/CD Pipeline Configuration', 'desc': 'Write mock unit tests, calculate test coverage, and automate workflow runs using Git.'},
            {'week': 3, 'title': 'Cloud Infrastructure Basics & Docker', 'desc': 'Write container definitions, manage environment values, and deploy standard web assets.'},
            {'week': 4, 'title': 'Recruiter Portfolio Review & Optimization', 'desc': 'Update professional titles, publish key projects, and prepare summaries for public display.'}
        ]
        
    return steps
