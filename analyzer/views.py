import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import datetime

from PyPDF2 import PdfReader
from django.db.models import Count

from .interview_generator import generate_interview_questions
from accounts.models import Profile
from portfolio.models import Skill, Project, Certification, PortfolioViewTracker
from utils.scoring_utils import get_portfolio_score, get_github_score, get_placement_readiness
from .models import JobDescription, LearningRoadmap, RoadmapStep
from utils.jd_analyzer import parse_job_description, compute_ats_match_details, generate_learning_roadmap_steps
import json

ROLE_REQUIREMENTS = {
    'backend developer': ['Python', 'Django', 'SQL', 'APIs', 'Git'],
    'full stack developer': ['Python', 'Django', 'JavaScript', 'HTML', 'CSS', 'SQL'],
    'frontend developer': ['HTML', 'CSS', 'JavaScript', 'React', 'Git'],
    'data analyst': ['Python', 'SQL', 'Pandas', 'Excel', 'Data Visualization'],
    'ai engineer': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch', 'Data Analysis'],
    'cloud engineer': ['AWS', 'Docker', 'Kubernetes', 'Linux', 'CI/CD'],
    'cybersecurity analyst': ['Linux', 'Networking', 'Security', 'Cryptography', 'Python'],
}

CAREER_PATHS = [
    {
        'role': 'Backend Developer',
        'skills': ['Python', 'Django', 'SQL', 'REST APIs', 'Git'],
        'summary': 'Build server-side applications, APIs, and database-driven systems.',
        'salary': '$85,000 - $130,000',
    },
    {
        'role': 'Full Stack Developer',
        'skills': ['Python', 'Django', 'JavaScript', 'HTML', 'CSS'],
        'summary': 'Design both frontend and backend components for modern web applications.',
        'salary': '$90,000 - $140,000',
    },
    {
        'role': 'Frontend Developer',
        'skills': ['HTML', 'CSS', 'JavaScript', 'React', 'Git'],
        'summary': 'Build responsive, interactive, and beautiful user interfaces for web apps.',
        'salary': '$80,000 - $120,000',
    },
    {
        'role': 'AI Engineer',
        'skills': ['Python', 'Machine Learning', 'Data Analysis', 'TensorFlow', 'PyTorch'],
        'summary': 'Develop AI models and production-ready machine learning solutions.',
        'salary': '$110,000 - $180,000',
    },
    {
        'role': 'Data Analyst',
        'skills': ['Python', 'SQL', 'Pandas', 'Data Visualization', 'Excel'],
        'summary': 'Extract insights from data and support business decisions.',
        'salary': '$65,000 - $95,000',
    },
    {
        'role': 'Cloud Engineer',
        'skills': ['AWS', 'Docker', 'Kubernetes', 'Linux', 'CI/CD'],
        'summary': 'Manage cloud infrastructure and deploy scalable applications.',
        'salary': '$95,000 - $150,000',
    },
    {
        'role': 'Cybersecurity Analyst',
        'skills': ['Linux', 'Networking', 'Security', 'Cryptography', 'Python'],
        'summary': 'Secure corporate networks, data, and software systems from intrusion.',
        'salary': '$90,000 - $140,000',
    },
]


@login_required
def github_analyzer(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('github_username', '').strip()
        if username:
            user_response = requests.get(f'https://api.github.com/users/{username}')
            if user_response.status_code == 200:
                profile_data = user_response.json()
                repos_response = requests.get(profile_data.get('repos_url', ''))
                if repos_response.status_code == 200:
                    repos = repos_response.json()
                    total_stars = sum(repo.get('stargazers_count', 0) for repo in repos)
                    total_forks = sum(repo.get('forks_count', 0) for repo in repos)
                    language_counts = {}
                    for repo in repos:
                        language = repo.get('language') or 'Unknown'
                        language_counts[language] = language_counts.get(language, 0) + 1
                    score = min(100, len(repos) * 4 + total_stars * 2 + total_forks)
                    
                    lang_labels = list(language_counts.keys())
                    lang_data = list(language_counts.values())
                    sorted_repos = sorted(repos, key=lambda r: r.get('stargazers_count', 0), reverse=True)[:5]
                    repo_labels = [r.get('name') for r in sorted_repos]
                    repo_stars = [r.get('stargazers_count', 0) for r in sorted_repos]
                    
                    profile, _ = Profile.objects.get_or_create(user=request.user)
                    profile.consistency_score = score
                    profile.save()

                    context.update({
                        'profile_data': profile_data,
                        'total_repos': len(repos),
                        'total_stars': total_stars,
                        'total_forks': total_forks,
                        'language_counts': language_counts,
                        'github_score': score,
                        'username': username,
                        'lang_labels_json': json.dumps(lang_labels),
                        'lang_data_json': json.dumps(lang_data),
                        'repo_labels_json': json.dumps(repo_labels),
                        'repo_stars_json': json.dumps(repo_stars),
                    })
                else:
                    context['error'] = 'Could not fetch repositories from GitHub.'
            else:
                # Rate limit fallback to mock data
                profile_data = {
                    'login': username,
                    'bio': 'Developer | Active GitHub user (Simulated Profile)',
                    'avatar_url': 'https://github.com/identicons/git.png',
                    'public_repos': 14,
                    'followers': 28
                }
                total_repos = 14
                total_stars = 32
                total_forks = 9
                language_counts = {'Python': 6, 'JavaScript': 5, 'HTML/CSS': 3}
                score = 75
                
                lang_labels = list(language_counts.keys())
                lang_data = list(language_counts.values())
                repo_labels = ['PortfolioAI', 'DjangoApp', 'MachineLearning', 'WebScraper', 'Utilities']
                repo_stars = [12, 10, 6, 4, 0]
                
                profile, _ = Profile.objects.get_or_create(user=request.user)
                profile.consistency_score = score
                profile.save()

                context.update({
                    'profile_data': profile_data,
                    'total_repos': total_repos,
                    'total_stars': total_stars,
                    'total_forks': total_forks,
                    'language_counts': language_counts,
                    'github_score': score,
                    'username': username,
                    'lang_labels_json': json.dumps(lang_labels),
                    'lang_data_json': json.dumps(lang_data),
                    'repo_labels_json': json.dumps(repo_labels),
                    'repo_stars_json': json.dumps(repo_stars),
                    'simulated': True
                })
        else:
            context['error'] = 'Please enter a GitHub username.'
    return render(request, 'analyzer/github_analyzer.html', context)


@login_required
def resume_analyzer(request):
    context = {}
    if request.method == 'POST' and request.FILES.get('resume'):
        resume_file = request.FILES['resume']
        try:
            reader = PdfReader(resume_file)
            text = ' '.join(page.extract_text() or '' for page in reader.pages)
            text_lower = text.lower()
            sections = {
                'education': 'education' in text_lower,
                'skills': 'skills' in text_lower or 'technical skills' in text_lower,
                'projects': 'project' in text_lower,
                'certifications': 'certification' in text_lower or 'certificate' in text_lower,
                'experience': 'experience' in text_lower,
            }
            found = sum(sections.values())
            score = int(found / len(sections) * 100)
            missing = [name for name, present in sections.items() if not present]
            suggestions = []
            if 'education' in missing:
                suggestions.append('Add clear education details if missing or incomplete.')
            if 'skills' in missing:
                suggestions.append('Include a dedicated skill section with relevant keywords.')
            if 'experience' in missing:
                suggestions.append('Provide impact-oriented project and internship details.')
            if 'certifications' in missing:
                suggestions.append('List certifications with dates and issuing organizations.')
            if 'projects' in missing:
                suggestions.append('Describe projects and technical tools used.')
            context.update({
                'resume_score': score,
                'missing_sections': missing,
                'suggestions': suggestions,
            })
        except Exception as exc:
            context['error'] = f'Could not read the uploaded resume PDF: {exc}'
    return render(request, 'analyzer/resume_analyzer.html', context)


@login_required
def skill_gap(request):
    context = {}
    if request.method == 'POST':
        target_role = request.POST.get('target_role', '').strip().lower()
        required = ROLE_REQUIREMENTS.get(target_role)
        current_skills = [skill.name.lower() for skill in Skill.objects.filter(user=request.user)]
        if required:
            missing = [skill for skill in required if skill.lower() not in current_skills]
            match = int((len(required) - len(missing)) / len(required) * 100)
            context.update({
                'target_role': target_role.title(),
                'required_skills': required,
                'current_skills': current_skills,
                'missing_skills': missing,
                'match_percentage': match,
            })
        else:
            context['error'] = 'Please select a valid target role.'
    return render(request, 'analyzer/skill_gap.html', context)


@login_required
def career_recommendation(request):
    # Aggregate user skills, project technologies and certifications to improve matching
    skill_qs = Skill.objects.filter(user=request.user)
    project_qs = Project.objects.filter(user=request.user)
    cert_qs = Certification.objects.filter(user=request.user)

    user_skills = set()
    for s in skill_qs:
        user_skills.add(s.name.lower())
    for p in project_qs:
        if p.tech_stack:
            for tok in [t.strip().lower() for t in p.tech_stack.split(',') if t.strip()]:
                user_skills.add(tok)
    for c in cert_qs:
        if c.certificate_name:
            for tok in [t.strip().lower() for t in c.certificate_name.split() if t.strip()]:
                user_skills.add(tok)

    recommendations = []
    learning_map = {
        'python': 'Complete a Python fundamentals course and practice projects.',
        'django': 'Build a CRUD web app with Django and deploy it.',
        'sql': 'Practice SQL queries and design normalized schemas.',
        'javascript': 'Learn modern JavaScript (ES6+) and DOM manipulation.',
        'html': 'Master semantic HTML and accessibility practices.',
        'css': 'Learn responsive layouts and modern CSS (Flexbox/Grid).',
        'react': 'Build a React SPA and learn component patterns.',
        'machine learning': 'Study ML fundamentals and experiment with scikit-learn.',
        'tensorflow': 'Follow TensorFlow tutorials and train simple models.',
        'pytorch': 'Build neural network pipelines and train simple models in PyTorch.',
        'pandas': 'Practice data cleaning with pandas and exploratory analysis.',
        'aws': 'Get hands-on with AWS free tier and core services like EC2/S3.',
        'docker': 'Containerize apps using Docker and compose for multi-service apps.',
        'kubernetes': 'Learn basics of Kubernetes and deploy a sample app.',
        'linux': 'Practice shell commands, permissions, and basic bash scripting.',
        'networking': 'Study TCP/IP protocols, DNS, subnetting, and network analysis.',
        'security': 'Understand threat models, firewalls, and secure programming practices.',
        'cryptography': 'Learn about symmetric/asymmetric encryption, hashing, and PKI.',
        'git': 'Master basic Git commands, branching, and collaborative PR workflows.',
        'apis': 'Design and build clean RESTful API endpoints with Django.',
        'rest apis': 'Understand API endpoints, methods, and standard API responses.',
        'excel': 'Build data workbooks and practice pivot tables and formatting.',
        'data visualization': 'Learn Matplotlib, Seaborn, or Tableau for plotting reports.',
        'ci/cd': 'Set up automated test and deploy workflows using GitHub Actions.'
    }

    for path in CAREER_PATHS:
        required = [r.lower() for r in path['skills']]
        match_count = sum(1 for req in required if req in user_skills)
        score = int(match_count / max(1, len(required)) * 100)
        missing = [r for r in path['skills'] if r.lower() not in user_skills]
        roadmap = []
        for m in missing:
            key = m.lower()
            if key in learning_map:
                roadmap.append(learning_map[key])
            else:
                roadmap.append(f'Gain experience with {m} through tutorials and small projects.')

        recommendations.append({
            'role': path['role'],
            'summary': path.get('summary', ''),
            'required_skills': path['skills'],
            'match_score': score,
            'missing_skills': missing,
            'learning_roadmap': roadmap,
            'salary': path.get('salary', ''),
        })

    recommendations.sort(key=lambda item: item['match_score'], reverse=True)
    return render(request, 'analyzer/career_recommendation.html', {'recommendations': recommendations})


@login_required
def interview_questions(request):
    context = {}
    if request.method == 'POST':
        target_role = request.POST.get('target_role', '').strip().lower()
        skills = [skill.name.lower() for skill in Skill.objects.filter(user=request.user)]
        projects = list(request.user.projects.all())
        certs = list(request.user.certifications.all())
        
        questions_dict = generate_interview_questions(
            skills,
            target_role,
            projects,
            certs
        )
        context = {
            'target_role': target_role.title(),
            'questions': questions_dict,
        }
    return render(request, 'analyzer/interview_questions.html', context)


@login_required
def portfolio_score(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    score = get_portfolio_score(request.user)
    profile_fields = [profile.full_name, profile.bio, profile.phone, profile.location, profile.professional_title]
    p_comp = sum(4 for field in profile_fields if field)
    
    breakdown = {
        'Profile': p_comp,
        'Education': min(15, request.user.educations.count() * 5),
        'Skills': min(20, request.user.skills.count() * 4),
        'Projects': min(20, request.user.projects.count() * 10),
        'Certifications': min(10, request.user.certifications.count() * 5),
        'Achievements': min(5, int(request.user.achievements.count() * 2.5)),
        'GitHub': 10 if profile.github else 0,
    }
    suggestions = []
    if score < 100:
        suggestions.append('Complete your profile, add more portfolio assets, and share your projects.')
    if request.user.skills.count() < 5:
        suggestions.append('Add at least 5 tech skills to your skills inventory.')
    if request.user.projects.count() < 2:
        suggestions.append('Add two or more key projects with tech stack and outcomes.')
    if request.user.certifications.count() < 2:
        suggestions.append('List certifications or training to demonstrate credentials.')
    # JSON-encode chart data for safe embedding in JS
    chart_labels_json = json.dumps(list(breakdown.keys()))
    chart_values_json = json.dumps(list(breakdown.values()))
    return render(request, 'analyzer/portfolio_score.html', {
        'score': score,
        'profile_completion': p_comp * 5,  # scaling to percentage format
        'breakdown': breakdown,
        'chart_labels_json': chart_labels_json,
        'chart_values_json': chart_values_json,
        'suggestions': suggestions,
    })


@login_required
def coding_analyzer(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile.leetcode_username = request.POST.get('leetcode_username', '').strip()
        profile.codechef_username = request.POST.get('codechef_username', '').strip()
        profile.hackerrank_username = request.POST.get('hackerrank_username', '').strip()
        
        # Heuristic calculations for mock platform ranks
        coding_score = 0
        problem_solving = 0
        consistency = 40 # base
        
        if profile.leetcode_username:
            coding_score += 40
            problem_solving += 45
            consistency += 20
        if profile.codechef_username:
            coding_score += 30
            problem_solving += 25
            consistency += 20
        if profile.hackerrank_username:
            coding_score += 30
            problem_solving += 30
            consistency += 20
            
        profile.coding_score = min(100, coding_score)
        profile.problem_solving_score = min(100, problem_solving)
        profile.consistency_score = min(100, consistency)
        profile.save()
        
        messages.success(request, "Coding profiles successfully analyzed and metrics updated!")
        return redirect('coding_analyzer')
        
    context = {
        'profile': profile,
        'leetcode_username': profile.leetcode_username,
        'codechef_username': profile.codechef_username,
        'hackerrank_username': profile.hackerrank_username,
        'coding_score': profile.coding_score,
        'consistency_score': profile.consistency_score,
        'problem_solving_score': profile.problem_solving_score,
    }
    return render(request, 'analyzer/coding_analyzer.html', context)


@login_required
def placement_readiness_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    readiness_score = get_placement_readiness(request.user)
    
    recommendations = []
    if readiness_score < 85:
        if request.user.projects.count() < 2:
            recommendations.append("Build and publish at least 2 technical projects with complete documentation.")
        if request.user.skills.count() < 6:
            recommendations.append("Add at least 6 technical skills to your skill list to raise candidate ranking.")
        if not profile.github:
            recommendations.append("Sync your GitHub account to showcase open-source contributions.")
        if not (profile.leetcode_username or profile.codechef_username or profile.hackerrank_username):
            recommendations.append("Configure competitive coding profile handles (LeetCode, HackerRank) to verify algorithmic skills.")
        if request.user.certifications.count() < 1:
            recommendations.append("Earn and list technical certifications to demonstrate credentials.")
    else:
        recommendations.append("Congratulations! Your portfolio matches placement readiness criteria. Keep maintaining consistency.")

    context = {
        'score': readiness_score,
        'recommendations': recommendations
    }
    return render(request, 'analyzer/placement_readiness.html', context)


@login_required
def project_recommender(request):
    skills = [s.name.lower() for s in request.user.skills.all()]
    
    # Capture requested career goal
    career_goal = request.GET.get('career_goal', '').strip().lower()
    if not career_goal:
        # Fallback to user professional title or backend developer
        profile = Profile.objects.filter(user=request.user).first()
        career_goal = (profile.professional_title or '').lower() if profile else 'backend developer'
        if 'front' in career_goal:
            career_goal = 'frontend developer'
        elif 'full' in career_goal:
            career_goal = 'full stack developer'
        elif 'ai' in career_goal or 'machine' in career_goal or 'ml' in career_goal:
            career_goal = 'ai engineer'
        elif 'data' in career_goal:
            career_goal = 'data analyst'
        elif 'cloud' in career_goal or 'devops' in career_goal:
            career_goal = 'cloud engineer'
        else:
            career_goal = 'backend developer'
            
    # Compile candidates lists
    all_recommendations = {
        'backend developer': [
            {
                'title': 'E-Commerce Platform API',
                'difficulty': 'Medium',
                'tech': 'Django, Python, SQLite, Redis',
                'outcome': 'Learn database relationships, session-based shopping carts, custom payment gateway integration, and caching flow.'
            },
            {
                'title': 'Hospital Management System',
                'difficulty': 'Medium',
                'tech': 'Django, Python, PostgreSQL, HTML5',
                'outcome': 'Master user role-based access control (doctor, patient, admin), database normalization, scheduling engines, and reports compilation.'
            },
            {
                'title': 'Real-Time Notification Engine',
                'difficulty': 'Hard',
                'tech': 'Python, FastAPI, WebSockets, Redis Pub/Sub',
                'outcome': 'Build asynchronous messaging networks, WebSocket handlers, local pub-sub configurations, and client listeners.'
            }
        ],
        'frontend developer': [
            {
                'title': 'Task Management Dashboard',
                'difficulty': 'Medium',
                'tech': 'React.js, Javascript, LocalStorage, CSS3',
                'outcome': 'Gain expertise in React state management, drag-and-drop components, asynchronous API data loading, and local caching.'
            },
            {
                'title': 'Interactive Analytics Portal',
                'difficulty': 'Medium',
                'tech': 'React, Chart.js, TailwindCSS, HTML5',
                'outcome': 'Master data plotting, dashboard design patterns, grid layouts, and custom chart themes.'
            },
            {
                'title': 'Developer Resume builder SPA',
                'difficulty': 'Hard',
                'tech': 'React, TypeScript, Redux, Sass',
                'outcome': 'Handle sophisticated global state trees, dynamic HTML-to-PDF compilation pipelines, and rich UI forms.'
            }
        ],
        'full stack developer': [
            {
                'title': 'Interactive Chat Application',
                'difficulty': 'Hard',
                'tech': 'React, Node.js, Express, Socket.io, MongoDB',
                'outcome': 'Master WebSockets, real-time message broadcasting, JWT-based user authentication, and persistent database storage for chats.'
            },
            {
                'title': 'SaaS Project Hub',
                'difficulty': 'Hard',
                'tech': 'Next.js, Tailwind, Django REST, PostgreSQL',
                'outcome': 'Design decoupled front-back architectures, integrate Stripe billing subscription plans, and secure JWT-based communications.'
            },
            {
                'title': 'Community Blog Platform',
                'difficulty': 'Medium',
                'tech': 'HTML, CSS, JavaScript, Django, MySQL',
                'outcome': 'Create full posting lifecycles, user profile settings, comments section, and search parameters.'
            }
        ],
        'ai engineer': [
            {
                'title': 'AI Document Parser & Analyzer',
                'difficulty': 'Hard',
                'tech': 'Python, PyPDF2, Natural Language Processing, FastAPI',
                'outcome': 'Understand NLP tokenization, custom regex heuristics parsing, pdf extraction pipelines, and high-performance FastAPI routing.'
            },
            {
                'title': 'Image Classification Engine',
                'difficulty': 'Medium',
                'tech': 'Python, TensorFlow, Keras, Matplotlib',
                'outcome': 'Learn Convolutional Neural Networks (CNNs), data augmentation techniques, model checkpointing, and evaluation metrics.'
            },
            {
                'title': 'Sentiment Analysis API',
                'difficulty': 'Medium',
                'tech': 'Python, Scikit-learn, Flask, Pandas',
                'outcome': 'Clean raw text bodies, train Naive Bayes or Logistic Regression classifiers, and deploy a REST prediction endpoint.'
            }
        ],
        'data analyst': [
            {
                'title': 'Sales Intelligence Workbook',
                'difficulty': 'Easy',
                'tech': 'Python, Pandas, Jupyter, Excel',
                'outcome': 'Automate report sheets aggregation, handle missing values data cleaning, and generate pivot calculations.'
            },
            {
                'title': 'Web Scraping Analytics Dashboard',
                'difficulty': 'Medium',
                'tech': 'Python, BeautifulSoup, SQLite, Matplotlib',
                'outcome': 'Extract public catalog datasets, build relational persistence schemas, and generate PDF visual trends.'
            },
            {
                'title': 'Financial Market Trends Plotter',
                'difficulty': 'Medium',
                'tech': 'Python, Pandas, Seaborn, APIs',
                'outcome': 'Fetch real-time stock ticks, compile moving averages calculations, and render technical analysis diagrams.'
            }
        ],
        'cloud engineer': [
            {
                'title': 'CI/CD Cloud Deploy Pipeline',
                'difficulty': 'Hard',
                'tech': 'Docker, Kubernetes, AWS EKS, GitHub Actions',
                'outcome': 'Deploy containerized web services, write multi-stage Dockerfiles, manage Kubernetes deployments, and construct automated build triggers.'
            },
            {
                'title': 'Serverless Image Processor',
                'difficulty': 'Hard',
                'tech': 'AWS Lambda, AWS S3, Python, Terraform',
                'outcome': 'Write infrastructure as code, trigger lambda handlers on file uploads, and auto-scale cloud microservices.'
            },
            {
                'title': 'Secure Multi-Tier Network VPC',
                'difficulty': 'Medium',
                'tech': 'AWS VPC, Linux, Ansible, Nginx',
                'outcome': 'Build secure private subnets, configure network address translations (NAT), and automate server setups.'
            }
        ]
    }

    # Fetch recommendations for career goal
    goal_recs = all_recommendations.get(career_goal, all_recommendations['backend developer'])
    
    recommendations = []
    for rec in goal_recs:
        tech_list = [t.strip() for t in rec['tech'].split(',') if t.strip()]
        matched_techs = [t for t in tech_list if t.lower() in skills]
        missing_techs = [t for t in tech_list if t.lower() not in skills]
        
        recommendations.append({
            'title': rec['title'],
            'difficulty': rec['difficulty'],
            'tech': rec['tech'],
            'tech_list': tech_list,
            'matched_techs': matched_techs,
            'missing_techs': missing_techs,
            'outcome': rec['outcome']
        })

    context = {
        'recommendations': recommendations,
        'career_goal': career_goal.title(),
        'goals_list': [g.title() for g in all_recommendations.keys()],
        'user_skills': skills
    }
    return render(request, 'analyzer/project_recommender.html', context)


@login_required
def analytics_dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # 1. Skill Distribution
    skills = request.user.skills.all()
    skill_labels = [s.name for s in skills]
    skill_levels = [s.level * 10 for s in skills] # normalized to 0-100
    
    # 2. Portfolio Completion Breakdown
    profile_fields = [profile.full_name, profile.bio, profile.phone, profile.location, profile.professional_title]
    p_comp = sum(4 for field in profile_fields if field)
    
    breakdown = {
        'Profile': p_comp,
        'Education': min(15, request.user.educations.count() * 5),
        'Skills': min(20, request.user.skills.count() * 4),
        'Projects': min(20, request.user.projects.count() * 10),
        'Certifications': min(10, request.user.certifications.count() * 5),
        'Achievements': min(5, int(request.user.achievements.count() * 2.5)),
        'GitHub': 10 if profile.github else 0,
    }
    portfolio_labels = list(breakdown.keys())
    portfolio_data = list(breakdown.values())
    
    # 3. Placement Readiness
    readiness = get_placement_readiness(request.user)
    
    # 4. Career Match Scores
    user_skills = set(s.name.lower() for s in skills)
    for p in request.user.projects.all():
        if p.tech_stack:
            for tok in [t.strip().lower() for t in p.tech_stack.split(',') if t.strip()]:
                user_skills.add(tok)
    
    career_labels = []
    career_scores = []
    for path in CAREER_PATHS:
        required = [r.lower() for r in path['skills']]
        match_count = sum(1 for req in required if req in user_skills)
        score = int(match_count / max(1, len(required)) * 100)
        career_labels.append(path['role'])
        career_scores.append(score)

    # ====================================================
    # FEATURE 8 & 10: PORTFOLIO TRAFFIC ANALYTICS
    # ====================================================
    today = timezone.now().date()
    logs = PortfolioViewTracker.objects.filter(user=request.user)
    
    total_views = logs.filter(event_type='portfolio_view').count()
    unique_visitors = logs.filter(event_type='portfolio_view').values('viewer_ip').distinct().count()
    recruiter_visits = logs.filter(is_recruiter=True).count()
    resume_downloads = logs.filter(event_type='resume_download').count()

    # Daily views (last 7 days)
    seven_days_ago = today - datetime.timedelta(days=6)
    daily_logs = logs.filter(
        event_type='portfolio_view',
        created_at__date__gte=seven_days_ago
    ).values('created_at__date').annotate(count=Count('id')).order_by('created_at__date')
    
    daily_views_dict = {log['created_at__date']: log['count'] for log in daily_logs}
    daily_labels = []
    daily_data = []
    for i in range(7):
        d = seven_days_ago + datetime.timedelta(days=i)
        daily_labels.append(d.strftime('%b %d'))
        daily_data.append(daily_views_dict.get(d, 0))

    # Weekly views (last 4 weeks)
    weekly_labels = []
    weekly_data = []
    for i in range(4):
        w_start = today - datetime.timedelta(weeks=i+1)
        w_end = today - datetime.timedelta(weeks=i)
        w_count = logs.filter(
            event_type='portfolio_view',
            created_at__date__gt=w_start,
            created_at__date__lte=w_end
        ).count()
        weekly_labels.insert(0, f"Week -{i}")
        weekly_data.insert(0, w_count)

    # Monthly views (last 6 months)
    monthly_labels = []
    monthly_data = []
    for i in range(6):
        m_start = today - datetime.timedelta(days=(i+1)*30)
        m_end = today - datetime.timedelta(days=i*30)
        m_count = logs.filter(
            event_type='portfolio_view',
            created_at__date__gt=m_start,
            created_at__date__lte=m_end
        ).count()
        monthly_labels.insert(0, m_end.strftime('%B'))
        monthly_data.insert(0, m_count)

    # Combined stats breakdown
    visitor_metrics = {
        'total_views': total_views,
        'unique_visitors': unique_visitors,
        'recruiter_visits': recruiter_visits,
        'resume_downloads': resume_downloads
    }

    context = {
        'readiness': readiness,
        'skill_labels_json': json.dumps(skill_labels),
        'skill_levels_json': json.dumps(skill_levels),
        'portfolio_labels_json': json.dumps(portfolio_labels),
        'portfolio_data_json': json.dumps(portfolio_data),
        'career_labels_json': json.dumps(career_labels),
        'career_scores_json': json.dumps(career_scores),
        # Traffic chart data
        'daily_labels_json': json.dumps(daily_labels),
        'daily_data_json': json.dumps(daily_data),
        'weekly_labels_json': json.dumps(weekly_labels),
        'weekly_data_json': json.dumps(weekly_data),
        'monthly_labels_json': json.dumps(monthly_labels),
        'monthly_data_json': json.dumps(monthly_data),
        'visitor_metrics': visitor_metrics
    }
    return render(request, 'analyzer/analytics_dashboard.html', context)


# ====================================================
# FEATURE 1: AI JOB DESCRIPTION ANALYZER
# FEATURE 2: ATS MATCH ENGINE
# FEATURE 3: AI IMPROVEMENT RECOMMENDATIONS
# FEATURE 4: LEARNING ROADMAP GENERATOR
# ====================================================

@login_required
def job_description_analyzer(request):
    context = {}
    
    # Fetch user's previous parsed JDs
    previous_jds = JobDescription.objects.filter(user=request.user).order_by('-created_at')
    active_roadmap = LearningRoadmap.objects.filter(user=request.user, is_active=True).first()
    
    if request.method == 'POST':
        jd_title = request.POST.get('job_title', '').strip() or 'Job Posting'
        jd_text = request.POST.get('job_description', '').strip()
        
        # Handle file upload if PDF
        if 'jd_file' in request.FILES:
            jd_file = request.FILES['jd_file']
            if jd_file.name.endswith('.pdf'):
                try:
                    reader = PdfReader(jd_file)
                    jd_text = ' '.join(page.extract_text() or '' for page in reader.pages)
                except Exception as e:
                    messages.error(request, f"Error parsing uploaded PDF: {e}")
                    return redirect('job_description_analyzer')
            else:
                messages.error(request, "Only PDF files are supported.")
                return redirect('job_description_analyzer')
                
        if not jd_text:
            messages.error(request, "Please enter a job description text or upload a PDF.")
            return redirect('job_description_analyzer')
            
        # Parse job description using jd_analyzer utility
        parsed_jd = parse_job_description(jd_text)
        
        # Save JD record
        jd_obj = JobDescription.objects.create(
            user=request.user,
            title=jd_title,
            raw_text=jd_text,
            extracted_skills=parsed_jd['skills'],
            extracted_technologies=parsed_jd['technologies'],
            extracted_experience=parsed_jd['experience'],
            extracted_certifications=parsed_jd['certifications'],
            extracted_keywords=parsed_jd['keywords'],
            extracted_soft_skills=parsed_jd['soft_skills']
        )
        
        # Run Match Engine
        match_details = compute_ats_match_details(request.user, parsed_jd)
        
        # Deactivate old roadmaps
        LearningRoadmap.objects.filter(user=request.user).update(is_active=False)
        
        # Create Learning Roadmap
        roadmap_obj = LearningRoadmap.objects.create(
            user=request.user,
            target_role=jd_title,
            job_description=jd_obj,
            is_active=True
        )
        
        # Generate and save week-by-week timeline steps
        roadmap_steps = generate_learning_roadmap_steps(match_details['missing_skills'], target_role=jd_title)
        for step in roadmap_steps:
            RoadmapStep.objects.create(
                roadmap=roadmap_obj,
                week_number=step['week'],
                title=step['title'],
                description=step['desc']
            )
            
        messages.success(request, "Job Description analyzed and custom roadmap generated!")
        return redirect('job_description_analyzer')

    # If viewing an analyzed JD details
    view_jd_id = request.GET.get('jd_id')
    selected_jd = None
    match_details = None
    selected_roadmap = None
    
    if view_jd_id:
        selected_jd = get_object_or_404(JobDescription, id=view_jd_id, user=request.user)
        # Compute match details
        jd_data = {
            'skills': selected_jd.extracted_skills,
            'technologies': selected_jd.extracted_technologies,
            'certifications': selected_jd.extracted_certifications,
        }
        match_details = compute_ats_match_details(request.user, jd_data)
        selected_roadmap = LearningRoadmap.objects.filter(job_description=selected_jd).first()
    elif previous_jds.exists():
        # Default to latest JD if none specified
        selected_jd = previous_jds.first()
        jd_data = {
            'skills': selected_jd.extracted_skills,
            'technologies': selected_jd.extracted_technologies,
            'certifications': selected_jd.extracted_certifications,
        }
        match_details = compute_ats_match_details(request.user, jd_data)
        selected_roadmap = LearningRoadmap.objects.filter(job_description=selected_jd).first()

    context.update({
        'previous_jds': previous_jds,
        'selected_jd': selected_jd,
        'match_details': match_details,
        'selected_roadmap': selected_roadmap,
        'active_roadmap': active_roadmap,
    })
    return render(request, 'analyzer/job_description_analyzer.html', context)


@login_required
@require_POST
def toggle_roadmap_step(request, step_id):
    """
    Ajax endpoint to toggle roadmap step completion.
    """
    step = get_object_or_404(RoadmapStep, id=step_id, roadmap__user=request.user)
    step.completed = not step.completed
    step.save()
    return JsonResponse({'status': 'success', 'completed': step.completed})


# ====================================================
# FEATURE 5: AI PORTFOLIO REVIEW SYSTEM
# ====================================================

@login_required
def portfolio_review(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    skills = list(request.user.skills.all())
    projects = list(request.user.projects.all())
    certs = list(request.user.certifications.all())
    
    p_score = get_portfolio_score(request.user)
    g_score = get_github_score(request.user)
    readiness = get_placement_readiness(request.user)

    strengths = []
    weaknesses = []
    recommendations = []

    # Calculate Strengths
    if p_score >= 80:
        strengths.append("High Completeness Index: Your portfolio contains highly populated profile details, education history, and metrics.")
    if len(skills) >= 6:
        strengths.append(f"Diverse Skillset: You have registered {len(skills)} distinct core skills demonstrating solid technical versatility.")
    if len(projects) >= 3:
        strengths.append(f"Strong Project Repository: Documenting {len(projects)} technical projects shows a great practical implementation footprint.")
    if profile.github and g_score >= 60:
        strengths.append("Active GitHub Footprint: Linked repository details represent consistency and standard coding activity.")
    if len(certs) >= 2:
        strengths.append(f"Industry Credentialing: Holding {len(certs)} certified tags builds immediate screening trust.")

    # Fallback strength
    if not strengths:
        strengths.append("Foundational Setup: Basic profiles and authentication verified.")

    # Calculate Weaknesses
    if p_score < 70:
        weaknesses.append("Low Portfolio Completeness: Several sections are empty or have minimal data, lowering recruiter interest.")
    if len(skills) < 5:
        weaknesses.append("Sparse Technical Inventory: Under 5 registered technical skills reduces keyword density for ATS filters.")
    if len(projects) < 2:
        weaknesses.append("Limited Project Portfolio: Having fewer than 2 showcase projects makes it difficult to verify execution capability.")
    if not profile.github:
        weaknesses.append("Missing GitHub Sync: Not linking your public GitHub repository hides contribution weight.")
    if len(certs) == 0:
        weaknesses.append("No Industry Certifications: Absence of certified tags reduces verified domain authority.")

    # Calculate Recommendations
    if not profile.github:
        recommendations.append("Link your public GitHub profile and run the sync analyzer to build consistency indicators.")
    if len(skills) < 6:
        recommendations.append("Register additional skills (e.g. Docker, SQL, Git) to expand match percentages.")
    if len(projects) < 3:
        recommendations.append("Add a cloud deployment or full-stack project using tools from the Smart Project Recommender.")
    if len(certs) < 2:
        recommendations.append("Obtain entry-level technical certifications (like AWS Cloud Practitioner or Oracle Java Associate) to reinforce credibility.")
    if p_score < 85:
        recommendations.append("Upload phone contacts, complete profile locations, and customize cover settings to raise score ratings.")

    context = {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'recommendations': recommendations,
        'portfolio_score': p_score,
        'github_score': g_score,
        'placement_readiness': readiness
    }
    return render(request, 'analyzer/portfolio_review.html', context)


# ====================================================
# FEATURE 12: AI PROFESSIONAL SUMMARY GENERATOR
# FEATURE 13: AI LINKEDIN HEADLINE GENERATOR
# ====================================================

@login_required
def ai_profile_generator(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    skills = [s.name for s in request.user.skills.all()[:5]]
    projects = [p.title for p in request.user.projects.all()[:3]]
    certs = [c.certificate_name for c in request.user.certifications.all()[:2]]

    # 1. Professional Summary
    title = profile.professional_title or "Software Engineer"
    skills_str = ", ".join(skills) if skills else "modern web architectures"
    proj_str = f" key showcase projects such as {', '.join(projects)}" if projects else "industry-standard code solutions"
    
    summary = (
        f"Detail-oriented {title} offering practical execution expertise in {skills_str}. "
        f"Proven competency in design patterns, data architecture, and deploying high-performance applications. "
        f"Demonstrated project delivery with{proj_str}. Adept at integrating with cross-functional engineering "
        f"teams, solving complex backend/frontend issues, and maintaining continuous delivery integration workflows."
    )

    # 2. Career Objective
    objective = (
        f"To secure a challenging {title} position in a growth-driven organization to leverage my skills "
        f"in {skills_str} and contribute to engineering robust, scalable software products while continuously "
        f"refining my technical and collaborative capabilities."
    )

    # 3. LinkedIn About Section
    linkedin_about = (
        f"💻 I am a passionate {title} dedicated to building high-performance systems and writing clean, scalable code.\n\n"
        f"🚀 Over the course of my engineering journey, I have focused on mastering technical frameworks including "
        f"{skills_str}. I believe in applying structured coding practices, database normalization, and automated deployments "
        f"to translate product requirements into user-friendly digital experiences.\n\n"
        f"🔧 Technical Toolbelt:\n"
        f"• Core Technologies: {skills_str}\n"
        f"• Project Footprint: {', '.join(projects) if projects else 'Full-Stack Web Architectures'}\n"
        f"• Certifications: {', '.join(certs) if certs else 'Continuous Learning'}\n\n"
        f"Let's connect or collaborate on open-source projects!"
    )

    # 4. LinkedIn Headlines
    headlines = [
        f"{title} | Specializing in {skills[0] if len(skills) > 0 else 'Software Engineering'} & {' / '.join(skills[1:3]) if len(skills) > 2 else 'API Architectures'} | Building Scalable Web Systems",
        f"Aspiring {title} | {skills_str} | Developer Candidate | Open to Opportunities",
        f"{title} | {', '.join(skills[:3]) if skills else 'Full Stack Developer'} | Passionate about Algorithms and System Design"
    ]

    context = {
        'summary': summary,
        'objective': objective,
        'linkedin_about': linkedin_about,
        'headlines': headlines
    }
    return render(request, 'analyzer/ai_profile_generator.html', context)


# ====================================================
# FEATURE 14: PORTFOLIO QUALITY SCORE
# ====================================================

@login_required
def portfolio_quality_score(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # Quality score components:
    # 1. Profile Completeness (25 points):
    p_fields = [profile.full_name, profile.bio, profile.phone, profile.location, profile.professional_title, profile.profile_image]
    profile_completion = sum(4.2 for f in p_fields if f) # max ~25
    profile_completion = min(25, int(profile_completion))

    # 2. Skills Count & Level (20 points):
    skills_count = request.user.skills.count()
    skills_score = min(20, skills_count * 4) # 5 skills to get 20

    # 3. Projects Quality (20 points):
    projects = request.user.projects.all()
    projects_score = min(20, len(projects) * 10) # 2 projects to get 20
    # Additional points for github link
    project_links_score = sum(2 for p in projects if p.github_link)
    projects_score = min(20, projects_score + project_links_score)

    # 4. Certifications & Credentials (15 points):
    certs_count = request.user.certifications.count()
    certs_score = min(15, certs_count * 7.5) # 2 certs to get 15

    # 5. GitHub Activity Score (10 points):
    g_score = get_github_score(request.user)
    github_score = min(10, int(g_score / 10))

    # 6. Education background (10 points):
    edu_count = request.user.educations.count()
    edu_score = min(10, edu_count * 5) # 2 entries to get 10

    total_score = profile_completion + skills_score + projects_score + certs_score + github_score + edu_score
    total_score = min(100, max(0, int(total_score)))

    # Determine Rating
    if total_score >= 85:
        rating = 'Excellent'
        badge_class = 'bg-success'
        summary_text = "Outstanding portfolio setup! Your records are highly comprehensive, keyword-dense, and optimized to capture recruiter attention."
    elif total_score >= 70:
        rating = 'Good'
        badge_class = 'bg-primary'
        summary_text = "Good setup. A few minor adjustments like adding another key project or industry certification will elevate your profile further."
    elif total_score >= 50:
        rating = 'Average'
        badge_class = 'bg-warning text-dark'
        summary_text = "Average score. Recommend syncing your GitHub activity, listing more technologies in your skill pool, and expanding project write-ups."
    else:
        rating = 'Needs Improvement'
        badge_class = 'bg-danger'
        summary_text = "Your portfolio needs details. Recruiter search filters require more keywords, certificates, and repositories to rank your application higher."

    # Checklist
    checklist = [
        {'item': 'Full Name & Title added', 'done': bool(profile.full_name and profile.professional_title)},
        {'item': 'Bio & Location populated', 'done': bool(profile.bio and profile.location)},
        {'item': 'At least 5 skills listed', 'done': skills_count >= 5},
        {'item': 'At least 2 showcase projects added', 'done': len(projects) >= 2},
        {'item': 'Public GitHub profile linked', 'done': bool(profile.github)},
        {'item': 'At least 1 industry certification listed', 'done': certs_count >= 1},
        {'item': 'Education background added', 'done': edu_count >= 1},
    ]

    context = {
        'quality_score': total_score,
        'rating': rating,
        'badge_class': badge_class,
        'summary_text': summary_text,
        'checklist': checklist
    }
    return render(request, 'analyzer/portfolio_quality_score.html', context)
