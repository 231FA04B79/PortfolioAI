from accounts.models import Badge, UserBadge, Profile
from utils.scoring_utils import get_portfolio_score, get_github_score, get_placement_readiness

BADGE_DEFINITIONS = [
    # Verification Badges
    {
        'name': '✓ Verified Email',
        'description': 'Successfully verified your email address.',
        'icon_class': 'bi-patch-check-fill',
        'category': 'Verification',
        'level': 'Bronze'
    },
    {
        'name': 'GitHub Explorer',
        'description': 'Successfully linked your public GitHub username.',
        'icon_class': 'bi-github',
        'category': 'Verification',
        'level': 'Bronze'
    },
    {
        'name': 'Professional Networker',
        'description': 'Successfully linked your LinkedIn profile.',
        'icon_class': 'bi-linkedin',
        'category': 'Verification',
        'level': 'Bronze'
    },
    {
        'name': 'Problem Solver',
        'description': 'Successfully synced your LeetCode competitive coding profile.',
        'icon_class': 'bi-code-square',
        'category': 'Verification',
        'level': 'Bronze'
    },
    {
        'name': 'Competitive Programmer',
        'description': 'Successfully synced your CodeChef competitive coding profile.',
        'icon_class': 'bi-terminal',
        'category': 'Verification',
        'level': 'Bronze'
    },
    {
        'name': 'Skill Certified',
        'description': 'Successfully synced your HackerRank competitive coding profile.',
        'icon_class': 'bi-award',
        'category': 'Verification',
        'level': 'Bronze'
    },
    # GitHub Analyzer Badges
    {
        'name': 'Beginner Developer',
        'description': 'GitHub rank score 30+',
        'icon_class': 'bi-egg',
        'category': 'GitHub',
        'level': 'Bronze'
    },
    {
        'name': 'Intermediate Developer',
        'description': 'GitHub rank score 50+',
        'icon_class': 'bi-egg-fried',
        'category': 'GitHub',
        'level': 'Silver'
    },
    {
        'name': 'Advanced Developer',
        'description': 'GitHub rank score 80+',
        'icon_class': 'bi-rocket-takeoff',
        'category': 'GitHub',
        'level': 'Gold'
    },
    {
        'name': 'Open Source Contributor',
        'description': 'Has 5+ GitHub repositories or links.',
        'icon_class': 'bi-git',
        'category': 'GitHub',
        'level': 'Silver'
    },
    {
        'name': 'GitHub Star',
        'description': 'Earned 10+ stars or high community footprint.',
        'icon_class': 'bi-star-fill',
        'category': 'GitHub',
        'level': 'Gold'
    },
    # Portfolio Badges
    {
        'name': 'Portfolio Creator',
        'description': 'Successfully created a portfolio skeleton.',
        'icon_class': 'bi-palette',
        'category': 'Portfolio',
        'level': 'Bronze'
    },
    {
        'name': 'Profile Completed',
        'description': 'Portfolio completeness reaches 70%+',
        'icon_class': 'bi-person-check',
        'category': 'Portfolio',
        'level': 'Silver'
    },
    {
        'name': 'Portfolio Expert',
        'description': 'Portfolio completeness reaches 90%+',
        'icon_class': 'bi-gem',
        'category': 'Portfolio',
        'level': 'Gold'
    },
    {
        'name': 'Top Portfolio',
        'description': 'Portfolio completeness reaches 100%!',
        'icon_class': 'bi-trophy-fill',
        'category': 'Portfolio',
        'level': 'Gold'
    },
    # Resume Badges
    {
        'name': 'Resume Builder',
        'description': 'Exported or created a resume.',
        'icon_class': 'bi-file-earmark-pdf',
        'category': 'Resume',
        'level': 'Bronze'
    },
    {
        'name': 'ATS Expert',
        'description': 'Resume matches ATS Score of 90%+',
        'icon_class': 'bi-file-earmark-bar-graph',
        'category': 'Resume',
        'level': 'Gold'
    },
    {
        'name': 'Resume Master',
        'description': 'Achieved a perfect ATS Resume score of 100%!',
        'icon_class': 'bi-file-earmark-check-fill',
        'category': 'Resume',
        'level': 'Gold'
    },
    # Placement Readiness Badges
    {
        'name': 'Career Ready',
        'description': 'Placement Readiness index reaches 50%+',
        'icon_class': 'bi-briefcase',
        'category': 'Readiness',
        'level': 'Bronze'
    },
    {
        'name': 'Placement Ready',
        'description': 'Placement Readiness index reaches 75%+',
        'icon_class': 'bi-briefcase-fill',
        'category': 'Readiness',
        'level': 'Silver'
    },
    {
        'name': 'Industry Ready',
        'description': 'Placement Readiness index reaches 90%+',
        'icon_class': 'bi-building',
        'category': 'Readiness',
        'level': 'Gold'
    },
    # Interview Preparation Badges
    {
        'name': 'Interview Beginner',
        'description': 'Successfully generated custom mock interview questions.',
        'icon_class': 'bi-chat-dots',
        'category': 'Interview',
        'level': 'Bronze'
    },
    {
        'name': 'Interview Explorer',
        'description': 'Generated mock interview questions for multiple roles.',
        'icon_class': 'bi-chat-left-quote',
        'category': 'Interview',
        'level': 'Silver'
    },
    {
        'name': 'Interview Master',
        'description': 'Highly prepared for job interviews.',
        'icon_class': 'bi-chat-square-text-fill',
        'category': 'Interview',
        'level': 'Gold'
    },
    # Skill Badges
    {
        'name': 'Python Developer',
        'description': 'Added Python skill at proficiency level 7+.',
        'icon_class': 'bi-filetype-py',
        'category': 'Skill',
        'level': 'Silver'
    },
    {
        'name': 'Java Developer',
        'description': 'Added Java skill at proficiency level 7+.',
        'icon_class': 'bi-cup-hot',
        'category': 'Skill',
        'level': 'Silver'
    },
    {
        'name': 'Django Developer',
        'description': 'Added Django skill at proficiency level 7+.',
        'icon_class': 'bi-file-code',
        'category': 'Skill',
        'level': 'Silver'
    },
    {
        'name': 'Frontend Developer',
        'description': 'Strong HTML/CSS/JS frontend skills.',
        'icon_class': 'bi-laptop',
        'category': 'Skill',
        'level': 'Silver'
    },
    {
        'name': 'Backend Developer',
        'description': 'Strong Python/SQL backend skills.',
        'icon_class': 'bi-database',
        'category': 'Skill',
        'level': 'Silver'
    },
    {
        'name': 'AI Enthusiast',
        'description': 'AI skills listed in inventory.',
        'icon_class': 'bi-cpu-fill',
        'category': 'Skill',
        'level': 'Silver'
    },
    {
        'name': 'Cloud Learner',
        'description': 'Cloud skills listed in inventory.',
        'icon_class': 'bi-cloud',
        'category': 'Skill',
        'level': 'Silver'
    }
]

def initialize_badge_definitions():
    """Seeds or updates Badge definitions in the database."""
    badges_by_name = {}
    for d in BADGE_DEFINITIONS:
        badge_obj, created = Badge.objects.get_or_create(
            name=d['name'],
            defaults={
                'description': d['description'],
                'icon_class': d['icon_class'],
                'category': d['category'],
                'level': d['level']
            }
        )
        if not created:
            # Sync any description/icon updates in definitions
            badge_obj.description = d['description']
            badge_obj.icon_class = d['icon_class']
            badge_obj.category = d['category']
            badge_obj.level = d['level']
            badge_obj.save()
        badges_by_name[d['name']] = badge_obj
    return badges_by_name

def assign_badges(user):
    """
    Evaluates user progress metrics and automatically awards eligible badges.
    This creates UserBadge objects and links them to Profile.badges ManyToMany.
    """
    profile, _ = Profile.objects.get_or_create(user=user)
    badge_objs = initialize_badge_definitions()

    # Fetch relevant metrics
    p_score = get_portfolio_score(user)
    g_score = get_github_score(user)
    readiness = get_placement_readiness(user)

    # 1. Helper to award a badge
    def award(badge_name):
        badge = badge_objs.get(badge_name)
        if badge:
            # Add to the new explicit track
            UserBadge.objects.get_or_create(user=user, badge=badge)
            # Add to the ManyToMany for backward compatibility
            if not profile.badges.filter(id=badge.id).exists():
                profile.badges.add(badge)

    # ==========================================
    # Verification Badges
    # ==========================================
    if profile.email_verified:
        award('✓ Verified Email')
    if profile.github:
        award('GitHub Explorer')
    if profile.linkedin:
        award('Professional Networker')
    if profile.leetcode_username:
        award('Problem Solver')
    if profile.codechef_username:
        award('Competitive Programmer')
    if profile.hackerrank_username:
        award('Skill Certified')

    # ==========================================
    # GitHub Analyzer Badges
    # ==========================================
    if profile.github:
        if g_score >= 30:
            award('Beginner Developer')
        if g_score >= 50:
            award('Intermediate Developer')
        if g_score >= 80:
            award('Advanced Developer')
        
        # Open Source Contributor: Proxy check for repos (we can check if g_score is active)
        if g_score >= 45:
            award('Open Source Contributor')
        # GitHub Star: Proxy check for stars (high score indicator)
        if g_score >= 70:
            award('GitHub Star')

    # ==========================================
    # Portfolio Badges
    # ==========================================
    if user.projects.exists() and user.skills.exists() and user.educations.exists():
        award('Portfolio Creator')
    if p_score >= 70:
        award('Profile Completed')
    if p_score >= 90:
        award('Portfolio Expert')
    if p_score == 100:
        award('Top Portfolio')

    # ==========================================
    # Resume Badges
    # ==========================================
    # If they downloaded or built a resume (check track log count or default presence)
    from portfolio.models import PortfolioViewTracker
    has_downloaded = PortfolioViewTracker.objects.filter(user=user, event_type='resume_download').exists()
    if has_downloaded:
        award('Resume Builder')

    # Calculate ATS Score on-the-fly to award Resume Badges
    ats_score = 0
    profile_fields = [profile.full_name, profile.bio, profile.phone, profile.location, profile.professional_title]
    ats_score += sum(4 for f in profile_fields if f)
    ats_score += min(20, user.skills.count() * 4)
    ats_score += min(20, user.projects.count() * 10)
    ats_score += min(15, user.educations.count() * 5)
    ats_score += min(10, user.certifications.count() * 5)
    ats_score += min(5, int(user.achievements.count() * 2.5))
    if profile.github:
        ats_score += 10
    
    if ats_score >= 90:
        award('ATS Expert')
    if ats_score >= 100:
        award('Resume Master')

    # ==========================================
    # Placement Readiness Badges
    # ==========================================
    if readiness >= 50:
        award('Career Ready')
    if readiness >= 75:
        award('Placement Ready')
    if readiness >= 90:
        award('Industry Ready')

    # ==========================================
    # Interview Preparation Badges
    # ==========================================
    # If they have parsed a JD or interacted with JD analyzer
    has_jds = user.job_descriptions.exists()
    if has_jds:
        award('Interview Beginner')
        if user.job_descriptions.count() >= 2:
            award('Interview Explorer')
        if readiness >= 85:
            award('Interview Master')

    # ==========================================
    # Skill Badges
    # ==========================================
    if user.skills.filter(name__iexact='python', level__gte=7).exists():
        award('Python Developer')
    if user.skills.filter(name__iexact='java', level__gte=7).exists():
        award('Java Developer')
    if user.skills.filter(name__iexact='django', level__gte=7).exists():
        award('Django Developer')
    
    # Frontend Developer: html, css, js/react level >= 7
    frontend_count = user.skills.filter(name__in=['html', 'css', 'javascript', 'react'], level__gte=7).count()
    if frontend_count >= 2:
        award('Frontend Developer')

    # Backend Developer: python/django, sql/postgres level >= 7
    backend_count = user.skills.filter(name__in=['python', 'sql', 'django', 'postgresql'], level__gte=7).count()
    if backend_count >= 2:
        award('Backend Developer')

    # AI Enthusiast
    has_ai = user.skills.filter(name__in=['machine learning', 'tensorflow', 'pytorch', 'ai', 'data science', 'pandas']).exists()
    if has_ai:
        award('AI Enthusiast')

    # Cloud Learner
    has_cloud = user.skills.filter(name__in=['aws', 'docker', 'kubernetes', 'cloud', 'devops']).exists()
    if has_cloud:
        award('Cloud Learner')
