ROLE_REQUIREMENTS = {
    'backend developer': ['Python', 'Django', 'SQL', 'APIs', 'Git'],
    'full stack developer': ['Python', 'Django', 'JavaScript', 'HTML', 'CSS', 'SQL'],
    'data analyst': ['Python', 'SQL', 'Pandas', 'Excel', 'Data Visualization'],
    'ai engineer': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Data Analysis'],
    'cloud engineer': ['AWS', 'Docker', 'Kubernetes', 'Linux', 'CI/CD'],
}

CAREER_PATHS = [
    {
        'role': 'Backend Developer',
        'skills': ['Python', 'Django', 'SQL', 'REST APIs', 'Git'],
        'summary': 'Build server-side applications, APIs, and database-driven systems.',
    },
    {
        'role': 'Full Stack Developer',
        'skills': ['Python', 'Django', 'JavaScript', 'HTML', 'CSS'],
        'summary': 'Design both frontend and backend components for modern web applications.',
    },
    {
        'role': 'AI Engineer',
        'skills': ['Python', 'Machine Learning', 'Data Analysis', 'TensorFlow', 'PyTorch'],
        'summary': 'Develop AI models and production-ready machine learning solutions.',
    },
    {
        'role': 'Data Analyst',
        'skills': ['Python', 'SQL', 'Pandas', 'Data Visualization', 'Excel'],
        'summary': 'Extract insights from data and support business decisions.',
    },
    {
        'role': 'Cloud Engineer',
        'skills': ['AWS', 'Docker', 'Kubernetes', 'Linux', 'CI/CD'],
        'summary': 'Manage cloud infrastructure and deploy scalable applications.',
    },
]


def analyze_skill_gap(current_skills, target_role):
    if not target_role:
        return None, 'Please select a valid target role.'

    required = ROLE_REQUIREMENTS.get(target_role)
    if not required:
        return None, 'Please select a valid target role.'

    missing = [skill for skill in required if skill.lower() not in current_skills]
    match = int((len(required) - len(missing)) / len(required) * 100)
    return {
        'target_role': target_role.title(),
        'required_skills': required,
        'current_skills': current_skills,
        'missing_skills': missing,
        'match_percentage': match,
    }, None


def get_career_recommendations(current_skills):
    recommendations = []
    for path in CAREER_PATHS:
        match_count = sum(1 for skill in path['skills'] if skill.lower() in current_skills)
        score = int(match_count / len(path['skills']) * 100)
        if score >= 20:
            recommendations.append({
                'role': path['role'],
                'summary': path['summary'],
                'required_skills': path['skills'],
                'match_score': score,
            })
    return sorted(recommendations, key=lambda item: item['match_score'], reverse=True)
