from accounts.models import Profile


def get_portfolio_score(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    
    # 1. Profile = 20% (5 key fields: 4% each)
    profile_fields = [profile.full_name, profile.bio, profile.phone, profile.location, profile.professional_title]
    profile_score = sum(4 for field in profile_fields if field)
    
    # 2. Education = 15% (5% per entry, max 15%)
    edu_count = user.educations.count()
    edu_score = min(15, edu_count * 5)
    
    # 3. Skills = 20% (4% per skill, max 20%)
    skills_count = user.skills.count()
    skills_score = min(20, skills_count * 4)
    
    # 4. Projects = 20% (10% per project, max 20%)
    projects_count = user.projects.count()
    projects_score = min(20, projects_count * 10)
    
    # 5. Certificates = 10% (5% per certificate, max 10%)
    certs_count = user.certifications.count()
    certs_score = min(10, certs_count * 5)
    
    # 6. Achievements = 5% (2.5% per achievement, max 5%)
    ach_count = user.achievements.count()
    ach_score = min(5, int(ach_count * 2.5))
    
    # 7. GitHub = 10% (10% if linked)
    github_score = 10 if profile.github else 0
    
    total = profile_score + edu_score + skills_score + projects_score + certs_score + ach_score + github_score
    return min(100, total)


def get_github_score(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    if not profile.github:
        return 0
    # Base score of 40 for linking github, plus points for repo/project counts
    project_count = user.projects.filter(github_link__isnull=False).exclude(github_link='').count()
    skill_count = user.skills.count()
    score = 40 + (project_count * 15) + (skill_count * 3)
    return min(100, score)


def get_placement_readiness(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    
    # 1. Profile completeness (20%)
    fields = [profile.full_name, profile.bio, profile.phone, profile.github, profile.linkedin, profile.profile_image]
    profile_completion = (sum(bool(field) for field in fields) / len(fields)) * 20
    
    # 2. Skills (20%)
    skills_count = user.skills.count()
    skills_score = min(20, skills_count * 4)
    
    # 3. Projects (20%)
    projects_count = user.projects.count()
    projects_score = min(20, projects_count * 10)
    
    # 4. Certifications (15%)
    certs_count = user.certifications.count()
    certs_score = min(15, certs_count * 7.5)
    
    # 5. Achievements (10%)
    achievements_count = user.achievements.count()
    achievements_score = min(10, achievements_count * 5)
    
    # 6. Coding profile completeness (15%)
    coding_links = [profile.github, profile.leetcode_username, profile.codechef_username, profile.hackerrank_username]
    coding_score = (sum(bool(link) for link in coding_links) / len(coding_links)) * 15
    
    total = int(profile_completion + skills_score + projects_score + certs_score + achievements_score + coding_score)
    return min(100, total)


def update_user_badges(user):
    from utils.badge_service import assign_badges
    assign_badges(user)


