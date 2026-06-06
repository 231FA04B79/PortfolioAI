from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Q



def is_recruiter(user):
    return user.is_staff or user.groups.filter(name='Recruiter').exists()


@login_required
@user_passes_test(is_recruiter, login_url='dashboard')
def recruiter_dashboard(request):
    students = User.objects.filter(is_active=True).order_by('username')[:50]
    return render(request, 'recruiter/recruiter_dashboard.html', {'students': students})


@login_required
@user_passes_test(is_recruiter, login_url='dashboard')
def student_search(request):
    query = request.GET.get('q', '').strip().lower()
    skills_query = request.GET.get('skills', '').strip().lower()
    sort_by = request.GET.get('sort_by', 'readiness')

    students = User.objects.filter(is_active=True).exclude(is_staff=True)
    if query:
        students = students.filter(
            Q(username__icontains=query) | Q(profile__full_name__icontains=query)
        )

    if skills_query:
        skill_names = [skill.strip() for skill in skills_query.split(',') if skill.strip()]
        if skill_names:
            skill_queries = Q()
            for name in skill_names:
                skill_queries |= Q(skills__name__iexact=name)
            students = students.filter(skill_queries).distinct()

    # Calculate metrics in memory for auto-ranking
    from utils.scoring_utils import get_portfolio_score, get_github_score, get_placement_readiness
    student_list = []
    for student in students:
        student.p_score = get_portfolio_score(student)
        student.g_score = get_github_score(student)
        student.readiness = get_placement_readiness(student)
        student_list.append(student)

    # Auto-rank sort
    if sort_by == 'portfolio':
        student_list.sort(key=lambda s: s.p_score, reverse=True)
    elif sort_by == 'github':
        student_list.sort(key=lambda s: s.g_score, reverse=True)
    else:
        student_list.sort(key=lambda s: s.readiness, reverse=True)

    context = {
        'students': student_list,
        'query': query,
        'skills': skills_query,
        'sort_by': sort_by
    }
    return render(request, 'recruiter/student_search.html', context)


@login_required
@user_passes_test(is_recruiter, login_url='dashboard')
def student_profile(request, username):
    student = get_object_or_404(User, username=username)
    from utils.scoring_utils import get_portfolio_score, get_github_score, get_placement_readiness
    p_score = get_portfolio_score(student)
    g_score = get_github_score(student)
    readiness = get_placement_readiness(student)
    
    # Track recruiter visit
    from portfolio.models import PortfolioViewTracker
    PortfolioViewTracker.objects.create(
        user=student,
        event_type='portfolio_view',
        viewer_ip=request.META.get('REMOTE_ADDR', '127.0.0.1'),
        is_recruiter=True
    )

    context = {
        'student': student,
        'p_score': p_score,
        'g_score': g_score,
        'readiness': readiness,
    }
    return render(request, 'recruiter/student_profile.html', context)


# ====================================================
# FEATURE 6: RECRUITER VIEW MODE
# ====================================================

@login_required
@user_passes_test(is_recruiter, login_url='dashboard')
def student_profile_job_match(request, username, jd_id):
    student = get_object_or_404(User, username=username)
    from analyzer.models import JobDescription
    from utils.jd_analyzer import compute_ats_match_details
    
    jd = get_object_or_404(JobDescription, id=jd_id)
    
    # Compute ATS Job Match details specifically for this candidate and JD
    jd_data = {
        'skills': jd.extracted_skills,
        'technologies': jd.extracted_technologies,
        'certifications': jd.extracted_certifications,
    }
    match_details = compute_ats_match_details(student, jd_data)
    
    from utils.scoring_utils import get_portfolio_score, get_github_score, get_placement_readiness
    p_score = get_portfolio_score(student)
    g_score = get_github_score(student)
    readiness = get_placement_readiness(student)
    
    # Track recruiter visit
    from portfolio.models import PortfolioViewTracker
    PortfolioViewTracker.objects.create(
        user=student,
        event_type='portfolio_view',
        viewer_ip=request.META.get('REMOTE_ADDR', '127.0.0.1'),
        is_recruiter=True
    )
    
    # Restrict context variables to ensure no passwords or internal parameters are sent
    context = {
        'student_username': student.username,
        'profile': student.profile,
        'skills': student.skills.all(),
        'projects': student.projects.all(),
        'certifications': student.certifications.all(),
        'educations': student.educations.all(),
        'p_score': p_score,
        'g_score': g_score,
        'readiness': readiness,
        'job_title': jd.title,
        'match_details': match_details,
    }
    return render(request, 'recruiter/student_profile_job_match.html', context)


# ====================================================
# FEATURE 7: CANDIDATE COMPARISON SYSTEM
# ====================================================

@login_required
@user_passes_test(is_recruiter, login_url='dashboard')
def compare_candidates(request):
    candidate_a_uname = request.GET.get('candidate_a', '').strip()
    candidate_b_uname = request.GET.get('candidate_b', '').strip()
    
    all_students = User.objects.filter(is_active=True).exclude(is_staff=True).order_by('username')
    
    candidate_a = None
    candidate_b = None
    
    if candidate_a_uname and candidate_b_uname:
        candidate_a = get_object_or_404(User, username=candidate_a_uname)
        candidate_b = get_object_or_404(User, username=candidate_b_uname)
        
        from utils.scoring_utils import get_portfolio_score, get_github_score, get_placement_readiness
        
        # Candidate A metrics
        candidate_a.p_score = get_portfolio_score(candidate_a)
        candidate_a.g_score = get_github_score(candidate_a)
        candidate_a.readiness = get_placement_readiness(candidate_a)
        candidate_a.skills_list = [s.name for s in candidate_a.skills.all()]
        candidate_a.projects_list = [p.title for p in candidate_a.projects.all()]
        candidate_a.certs_list = [c.certificate_name for c in candidate_a.certifications.all()]
        
        # Candidate B metrics
        candidate_b.p_score = get_portfolio_score(candidate_b)
        candidate_b.g_score = get_github_score(candidate_b)
        candidate_b.readiness = get_placement_readiness(candidate_b)
        candidate_b.skills_list = [s.name for s in candidate_b.skills.all()]
        candidate_b.projects_list = [p.title for p in candidate_b.projects.all()]
        candidate_b.certs_list = [c.certificate_name for c in candidate_b.certifications.all()]
        
    context = {
        'all_students': all_students,
        'candidate_a': candidate_a,
        'candidate_b': candidate_b,
    }
    return render(request, 'recruiter/candidate_comparison.html', context)
