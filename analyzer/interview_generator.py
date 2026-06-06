def generate_interview_questions(current_skills, target_role, user_projects=None, user_certs=None):
    if not target_role:
        target_role = "Backend Developer"
        
    normalized = target_role.strip().lower()
    user_projects = user_projects or []
    user_certs = user_certs or []
    
    # 1. Technical Questions
    tech_pool = {
        'backend developer': [
            'How do you design RESTful API routing and structure JSON responses?',
            'Explain Django model relations (ForeignKey, ManyToManyField) and query optimization.',
            'What is connection pooling and how do you handle database lock issues in SQL?'
        ],
        'frontend developer': [
            'Explain React hooks (useState, useEffect, useMemo) and performance optimization.',
            'How do you design custom CSS layouts using Flexbox and Grid dynamically?',
            'What is client-side state management and how do you handle routing?'
        ],
        'full stack developer': [
            'How do you integrate React UI with a Django back-end service securely?',
            'Explain how session authentication differs from JWT tokens.',
            'Describe how you optimize asset bundling and page rendering times.'
        ],
        'ai engineer': [
            'Explain the difference between bagging and boosting algorithms.',
            'How do you handle gradient explosion or vanishing gradient during backpropagation?',
            'Describe how you prepare and split large datasets for model training.'
        ],
        'data analyst': [
            'What SQL aggregates and window functions do you use for data analysis?',
            'Explain how you deal with null values and outliers in Pandas dataframes.',
            'How do you decide between a bar chart, line chart, or scatter plot for presentation?'
        ],
        'cloud engineer': [
            'Explain Docker containerization and how you manage shared volumes.',
            'How do you design high-availability load balancing in AWS?',
            'Describe CI/CD pipeline stages for automated testing and deployment.'
        ],
        'cybersecurity analyst': [
            'Explain symmetric vs asymmetric encryption (RSA, AES) and key exchange.',
            'How do you identify and mitigate SQL injection and Cross-Site Scripting (XSS)?',
            'What steps do you take to secure a Linux production web server?'
        ]
    }
    
    tech_questions = list(tech_pool.get(normalized, [
        'Explain the core programming concepts of your preferred language.',
        'How do you optimize code complexity and memory usage?'
    ]))
    
    # Customize based on specific skills the user has added
    for skill in current_skills:
        skill_clean = skill.lower()
        if skill_clean == 'django':
            tech_questions.append("How do you manage database migrations in Django and resolve migration conflicts?")
        elif skill_clean == 'react':
            tech_questions.append("What is React Virtual DOM and how does reconciliation work?")
        elif skill_clean == 'docker':
            tech_questions.append("How do you write a multi-stage Dockerfile to minimize image sizes?")
        elif skill_clean == 'aws':
            tech_questions.append("Explain the use case for AWS S3 vs EC2 vs RDS.")
        elif skill_clean == 'python':
            tech_questions.append("Explain decorators and generator functions in Python.")

    # 2. HR Questions
    hr_questions = [
        'Walk me through a difficult technical challenge you solved recently.',
        'How do you manage deadlines and prioritize competing tasks under stress?',
        'Describe a situation where you had a disagreement with a team member. How did you resolve it?'
    ]

    # 3. Scenario Questions
    scenario_questions = [
        f'Scenario: Your company web application experiences a sudden 10x traffic spike. As a {target_role.title()}, what immediate and long-term mitigation steps do you recommend?',
        'Scenario: A critical production server goes offline, and the logs show database connection timeout error. What is your troubleshooting protocol?',
        'Scenario: You discover that a third-party package used in your codebase has a severe security vulnerability. How do you patch it safely?'
    ]

    # 4. Project & Certification Questions (Dynamic based on user portfolio)
    project_questions = []
    if user_projects:
        for p in user_projects[:2]:
            project_questions.append(f"In your project '{p.title}', what was the main architectural challenge you faced when using {p.tech_stack or 'the tech stack'}?")
            project_questions.append(f"How did you test the reliability and scale of '{p.title}'?")
    else:
        project_questions.append("Tell me about a personal project you built. What were the technical hurdles, and what would you change if you rewrote it?")

    if user_certs:
        for c in user_certs[:2]:
            project_questions.append(f"How has the training or knowledge you acquired from your '{c.certificate_name}' certification directly influenced your coding practices?")
    
    return {
        'technical': tech_questions[:4],
        'hr': hr_questions,
        'scenario': scenario_questions,
        'project': project_questions
    }
