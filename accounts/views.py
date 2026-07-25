from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import RegisterForm
from .forms import ProfileForm
from .models import Profile

from portfolio.models import Education, Skill, Project, Certification, Achievement
from utils.resume_utils import parse_resume_pdf_content
from utils.scoring_utils import get_portfolio_score, get_github_score, get_placement_readiness, update_user_badges


def home(request):
    from django.contrib.auth.models import User
    
    portfolios_count = Profile.objects.count() + 142
    resumes_count = User.objects.count() * 2 + 87
    skills_count = Skill.objects.count() + 412
    recs_count = Profile.objects.count() * 3 + 124
    
    context = {
        'portfolios_count': portfolios_count,
        'resumes_count': resumes_count,
        'skills_count': skills_count,
        'recs_count': recs_count,
    }
    return render(request, 'home.html', context)


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            from django.contrib.auth.models import User
            # Create user account immediately
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            
            # Generate recovery code
            from utils.recovery_service import generate_recovery_code, hash_recovery_code
            plain_code = generate_recovery_code()
            
            # Save profile & mark email as verified
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.email_verified = True
            profile.full_name = form.cleaned_data['username']
            profile.recovery_code_hash = hash_recovery_code(plain_code)
            profile.save()
            
            # Store code in session for one-time display
            request.session['plain_recovery_code'] = plain_code
            request.session.modified = True
            
            messages.success(request, "Account created successfully! Please save your recovery code.")
            return redirect('register_success')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def register_success(request):
    plain_code = request.session.pop('plain_recovery_code', None)
    if not plain_code:
        messages.error(request, "No pending recovery code to display.")
        return redirect('login')
    return render(request, 'accounts/register_success.html', {'recovery_code': plain_code})


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        recovery_code = request.POST.get('recovery_code', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        
        if not email or not recovery_code or not password or not password_confirm:
            messages.error(request, "All fields are required.")
            return render(request, 'accounts/forgot_password.html')
            
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/forgot_password.html')
            
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'accounts/forgot_password.html')
            
        # Security validation checks on password complexity
        errors = []
        if not any(c.isupper() for c in password):
            errors.append("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in password):
            errors.append("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in password):
            errors.append("Password must contain at least one number.")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
            errors.append("Password must contain at least one special character.")
        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'accounts/forgot_password.html')

        from django.contrib.auth.models import User
        # Find account by email (prevent email enumeration by showing same error on failure)
        user = User.objects.filter(email=email).first()
        profile = None
        if user:
            profile, _ = Profile.objects.get_or_create(user=user)
            
        from utils.recovery_service import verify_recovery_code, generate_recovery_code, hash_recovery_code
        # Timing-safe validation
        if user and profile and verify_recovery_code(recovery_code, profile.recovery_code_hash):
            # Update password
            user.set_password(password)
            user.save()
            
            # Generate new recovery code
            new_plain_code = generate_recovery_code()
            profile.recovery_code_hash = hash_recovery_code(new_plain_code)
            from django.utils import timezone
            profile.last_regenerated = timezone.now()
            profile.save()
            
            # Save in session for one-time success display
            request.session['new_recovery_code'] = new_plain_code
            request.session.modified = True
            
            messages.success(request, "Your password has been successfully reset! Please save your new recovery code.")
            return redirect('forgot_password_success')
        else:
            messages.error(request, "Invalid email address or recovery code.")
            return render(request, 'accounts/forgot_password.html')
            
    return render(request, 'accounts/forgot_password.html')


def forgot_password_success(request):
    new_plain_code = request.session.pop('new_recovery_code', None)
    if not new_plain_code:
        messages.error(request, "No pending recovery code to display.")
        return redirect('login')
    return render(request, 'accounts/forgot_password_success.html', {'recovery_code': new_plain_code})





def login_view(request):

    if request.method == 'POST':

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            return redirect('dashboard')

    else:

        form = AuthenticationForm()

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )


@login_required
def dashboard(request):
    update_user_badges(request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    education_count = Education.objects.filter(user=request.user).count()
    skills_count = Skill.objects.filter(user=request.user).count()
    projects_count = Project.objects.filter(user=request.user).count()
    certifications_count = Certification.objects.filter(user=request.user).count()
    achievements_count = Achievement.objects.filter(user=request.user).count()
    
    p_score = get_portfolio_score(request.user)
    g_score = get_github_score(request.user)
    readiness = get_placement_readiness(request.user)
    badges = profile.badges.all()

    context = {
        'profile': profile,
        'education_count': education_count,
        'skills_count': skills_count,
        'projects_count': projects_count,
        'certifications_count': certifications_count,
        'achievements_count': achievements_count,
        'portfolio_score': p_score,
        'github_score': g_score,
        'placement_readiness': readiness,
        'badges': badges,
    }

    return render(request, 'accounts/dashboard.html', context)


def get_user_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


@login_required
def profile(request):
    update_user_badges(request.user)
    profile = get_user_profile(request.user)
    p_score = get_portfolio_score(request.user)
    g_score = get_github_score(request.user)
    readiness = get_placement_readiness(request.user)

    context = {
        'profile': profile,
        'portfolio_score': p_score,
        'github_score': g_score,
        'placement_readiness': readiness,
    }

    return render(
        request,
        'accounts/profile.html',
        context
    )


@login_required
def edit_profile(request):

    profile = get_user_profile(request.user)

    if request.method == 'POST':

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            form.save()

            return redirect('profile')

    else:

        form = ProfileForm(
            instance=profile
        )

    return render(
        request,
        'accounts/edit_profile.html',
        {'form': form}
    )


@login_required
def resume_import_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'parse':
            if 'resume' in request.FILES:
                resume_file = request.FILES['resume']
                try:
                    parsed_data = parse_resume_pdf_content(resume_file)
                    # Convert skills array to comma-separated string for editing
                    parsed_data['skills_str'] = ', '.join(parsed_data['skills'])
                    return render(request, 'accounts/resume_import.html', {'parsed_data': parsed_data, 'step': 'review'})
                except Exception as e:
                    messages.error(request, f"Error parsing PDF resume: {e}")
            else:
                messages.error(request, "Please upload a valid PDF resume file.")
        elif action == 'save':
            # Save profile details
            profile, _ = Profile.objects.get_or_create(user=request.user)
            full_name = request.POST.get('full_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            location = request.POST.get('location', '').strip()
            github = request.POST.get('github', '').strip()
            linkedin = request.POST.get('linkedin', '').strip()
            portfolio_website = request.POST.get('portfolio_website', '').strip()

            if full_name:
                profile.full_name = full_name
            if phone:
                profile.phone = phone
            if location:
                profile.location = location
            if github:
                profile.github = github
            if linkedin:
                profile.linkedin = linkedin
            if portfolio_website:
                profile.portfolio_website = portfolio_website
            profile.save()

            if email:
                request.user.email = email
                request.user.save()

            # Save skills
            skills_str = request.POST.get('skills', '').strip()
            if skills_str:
                skills_list = [s.strip() for s in skills_str.split(',') if s.strip()]
                seen_skills = set()
                for s_name in skills_list:
                    s_name_lower = s_name.lower()
                    if s_name_lower not in seen_skills:
                        seen_skills.add(s_name_lower)
                        if s_name_lower not in ['skills', 'technical skills', 'key skills', 'education', 'projects']:
                            Skill.objects.get_or_create(user=request.user, name=s_name, defaults={'level': 8})

            # Save education
            edu_degrees = request.POST.getlist('edu_degree[]')
            edu_colleges = request.POST.getlist('edu_college[]')
            edu_years = request.POST.getlist('edu_year[]')
            edu_cgpas = request.POST.getlist('edu_cgpa[]')
            edu_types = request.POST.getlist('edu_type[]')
            edu_scoring_types = request.POST.getlist('edu_scoring_type[]')

            for i in range(len(edu_degrees)):
                degree = edu_degrees[i].strip()
                college = edu_colleges[i].strip()
                year = edu_years[i].strip()
                cgpa = edu_cgpas[i].strip()
                edu_type = edu_types[i].strip() if i < len(edu_types) else "Other"
                scoring_type = edu_scoring_types[i].strip() if i < len(edu_scoring_types) else "CGPA"

                if not degree or degree.lower() in ['education', 'academics', 'academic details', 'educational qualifications']:
                    continue
                Education.objects.create(
                    user=request.user,
                    education_type=edu_type,
                    degree=degree,
                    college_name=college or "Institution/College",
                    scoring_type=scoring_type,
                    score_value=cgpa,
                    completion_year=year or "2026",
                )

            # Save projects
            proj_titles = request.POST.getlist('proj_title[]')
            proj_descs = request.POST.getlist('proj_desc[]')
            proj_techs = request.POST.getlist('proj_tech[]')
            proj_githubs = request.POST.getlist('proj_github[]')
            proj_durations = request.POST.getlist('proj_duration[]')

            for i in range(len(proj_titles)):
                title = proj_titles[i].strip()
                desc = proj_descs[i].strip()
                tech = proj_techs[i].strip()
                github_link = proj_githubs[i].strip()
                duration = proj_durations[i].strip()

                if not title or title.lower() in ['projects', 'key projects', 'personal projects', 'academic projects']:
                    continue

                final_desc = desc
                if duration:
                    final_desc = f"[Duration: {duration}] {desc}"

                Project.objects.create(
                    user=request.user,
                    title=title,
                    description=final_desc or "Project details.",
                    tech_stack=tech,
                    github_link=github_link
                )

            # Save certifications
            cert_names = request.POST.getlist('cert_name[]')
            cert_orgs = request.POST.getlist('cert_org[]')
            cert_dates = request.POST.getlist('cert_date[]')
            cert_credentials = request.POST.getlist('cert_credential[]')

            from datetime import datetime
            for i in range(len(cert_names)):
                c_name = cert_names[i].strip()
                org = cert_orgs[i].strip()
                date_str = cert_dates[i].strip()
                cred_id = cert_credentials[i].strip()

                if not c_name or c_name.lower() in ['certifications', 'certificates', 'courses']:
                    continue

                final_org = org
                if cred_id:
                    final_org = f"{org} (Credential ID: {cred_id})"

                parsed_date = None
                if date_str:
                    for fmt in ("%Y", "%Y-%m", "%B %Y", "%b %Y"):
                        try:
                            parsed_date = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue

                Certification.objects.create(
                    user=request.user,
                    certificate_name=c_name,
                    issuing_organization=final_org or "Coursera / Udemy",
                    issue_date=parsed_date
                )

            # Save achievements
            ach_titles = request.POST.getlist('ach_title[]')
            ach_descs = request.POST.getlist('ach_desc[]')

            for i in range(len(ach_titles)):
                title = ach_titles[i].strip()
                desc = ach_descs[i].strip()

                if not title or title.lower() in ['achievements', 'accomplishments', 'awards']:
                    continue

                Achievement.objects.create(
                    user=request.user,
                    title=title,
                    description=desc or "Imported achievement details."
                )

            messages.success(request, "Resume data successfully parsed and saved to your profile and portfolio!")
            return redirect('dashboard')

    return render(request, 'accounts/resume_import.html', {'step': 'upload'})


def logout_view(request):
    logout(request)
    return redirect('home')


from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from accounts.models import Badge, UserBadge
from django.contrib.auth.models import User

@login_required
def account_settings(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # Store settings in session for display
    notifications_enabled = request.session.get('notifications_enabled', True)
    privacy_mode = request.session.get('privacy_mode', False)
    
    # Handle forms
    profile_form = ProfileForm(instance=profile)
    
    # Get newly regenerated recovery code if available (popped so it only shows once)
    new_recovery_code = request.session.pop('new_recovery_code_settings', None)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_profile':
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                update_user_badges(request.user)
                messages.success(request, "Profile settings successfully saved.")
                return redirect('account_settings')
            else:
                messages.error(request, "Please correct the errors in the profile form.")
                
        elif action == 'update_email':
            new_email = request.POST.get('email', '').strip()
            if not new_email:
                messages.error(request, "Please enter a valid email address.")
            elif new_email.lower() == request.user.email.lower():
                messages.info(request, "This is already your registered email address.")
            elif User.objects.filter(email__iexact=new_email).exclude(id=request.user.id).exists():
                messages.error(request, "This email address is already in use by another account.")
            else:
                request.user.email = new_email
                request.user.save()
                profile.email_verified = True
                profile.save()
                update_user_badges(request.user)
                messages.success(request, f"Email address updated to {new_email} successfully.")
                return redirect('account_settings')
                
        elif action == 'regenerate_recovery_code':
            confirm_password = request.POST.get('confirm_password', '').strip()
            if not confirm_password:
                messages.error(request, "Password confirmation is required to regenerate your recovery code.")
                return redirect('account_settings')
                
            if request.user.check_password(confirm_password):
                from utils.recovery_service import generate_recovery_code, hash_recovery_code
                from django.utils import timezone
                
                # Generate new code
                new_code = generate_recovery_code()
                profile.recovery_code_hash = hash_recovery_code(new_code)
                profile.last_regenerated = timezone.now()
                profile.save()
                
                # Store in session to display once on settings page load
                request.session['new_recovery_code_settings'] = new_code
                request.session.modified = True
                
                messages.success(request, "Your recovery code has been regenerated successfully!")
                return redirect('account_settings')
            else:
                messages.error(request, "Incorrect password. Recovery code regeneration failed.")
                return redirect('account_settings')
            
        elif action == 'save_preferences':
            request.session['notifications_enabled'] = request.POST.get('notifications') == 'on'
            request.session['privacy_mode'] = request.POST.get('privacy') == 'on'
            messages.success(request, "Preferences successfully updated.")
            return redirect('account_settings')
            
    context = {
        'profile': profile,
        'profile_form': profile_form,
        'notifications_enabled': notifications_enabled,
        'privacy_mode': privacy_mode,
        'new_recovery_code': new_recovery_code,
    }
    return render(request, 'accounts/settings.html', context)


import json
from django.contrib.auth import authenticate

@login_required
def change_password_ajax(request):
    """
    Ajax step-by-step change password endpoint.
    Expects POST request with JSON payload.
    """
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)
        
    try:
        data = json.loads(request.body)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON request payload.'}, status=400)
        
    step = data.get('step')
    user = request.user
    
    if step == 1:
        current_password = data.get('current_password', '')
        if not user.check_password(current_password):
            return JsonResponse({'status': 'error', 'message': 'Incorrect current password.'})
        
        request.session['password_change_step1_passed'] = True
        request.session.modified = True
        return JsonResponse({'status': 'success', 'message': 'Password verified. You may now choose a new password.'})
            
    elif step == 2:
        if not request.session.get('password_change_step1_passed'):
            return JsonResponse({'status': 'error', 'message': 'Unauthorized. Please complete Step 1 first.'})
            
        new_password = data.get('new_password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        if new_password != confirm_password:
            return JsonResponse({'status': 'error', 'message': 'Passwords do not match.'})
            
        # Validate complexity
        errors = []
        if len(new_password) < 8:
            errors.append("Password must be at least 8 characters long.")
        if not any(c.isupper() for c in new_password):
            errors.append("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in new_password):
            errors.append("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in new_password):
            errors.append("Password must contain at least one number.")
        if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in new_password):
            errors.append("Password must contain at least one special character.")
            
        if errors:
            return JsonResponse({'status': 'error', 'message': ' '.join(errors)})
            
        # Update password
        user.set_password(new_password)
        user.save()
        
        # Keep user authenticated
        update_session_auth_hash(request, user)
        
        # Clear session flags
        if 'password_change_step1_passed' in request.session: del request.session['password_change_step1_passed']
        request.session.modified = True
        
        return JsonResponse({'status': 'success', 'message': 'Password changed successfully.'})
        
    return JsonResponse({'status': 'error', 'message': 'Invalid step value.'})



from django.http import JsonResponse

@login_required
def achievements_dashboard(request):
    update_user_badges(request.user)
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # Fetch earned badges with date earned
    earned_user_badges = UserBadge.objects.filter(user=request.user).select_related('badge')
    earned_badge_ids = [ub.badge.id for ub in earned_user_badges]
    
    # Fetch all badges in system to determine locked ones
    all_badges = Badge.objects.all()
    locked_badges = all_badges.exclude(id__in=earned_badge_ids)
    
    # Calculate progress metrics
    p_score = get_portfolio_score(request.user)
    g_score = get_github_score(request.user)
    readiness = get_placement_readiness(request.user)
    
    # On-the-fly ATS score
    ats_score = 0
    profile_fields = [profile.full_name, profile.bio, profile.phone, profile.location, profile.professional_title]
    ats_score += sum(4 for f in profile_fields if f)
    ats_score += min(20, request.user.skills.count() * 4)
    ats_score += min(20, request.user.projects.count() * 10)
    ats_score += min(15, request.user.educations.count() * 5)
    ats_score += min(10, request.user.certifications.count() * 5)
    ats_score += min(5, int(request.user.achievements.count() * 2.5))
    if profile.github:
        ats_score += 10
    
    # Progression timeline
    progression_list = []
    
    # GitHub progression
    github_earned = [ub.badge.name for ub in earned_user_badges if ub.badge.category == 'GitHub']
    if 'GitHub Star' not in github_earned:
        if 'Advanced Developer' not in github_earned:
            if 'Intermediate Developer' not in github_earned:
                if 'Beginner Developer' not in github_earned:
                    progression_list.append({
                        'category': 'GitHub',
                        'current': 'None',
                        'next': 'Beginner Developer',
                        'requirement': 'Link GitHub and score 30+ (Current Score: {})'.format(g_score),
                        'progress': min(100, int(g_score / 30 * 100))
                    })
                else:
                    progression_list.append({
                        'category': 'GitHub',
                        'current': 'Beginner Developer',
                        'next': 'Intermediate Developer',
                        'requirement': 'GitHub score 50+ (Current Score: {})'.format(g_score),
                        'progress': min(100, int(g_score / 50 * 100))
                    })
            else:
                progression_list.append({
                    'category': 'GitHub',
                    'current': 'Intermediate Developer',
                    'next': 'Advanced Developer',
                    'requirement': 'GitHub score 80+ (Current Score: {})'.format(g_score),
                    'progress': min(100, int(g_score / 80 * 100))
                })
        else:
            progression_list.append({
                'category': 'GitHub',
                'current': 'Advanced Developer',
                'next': 'GitHub Star',
                'requirement': 'GitHub score 70+ and stars (Current Score: {})'.format(g_score),
                'progress': min(100, int(g_score / 70 * 100))
            })
            
    # Portfolio progression
    port_earned = [ub.badge.name for ub in earned_user_badges if ub.badge.category == 'Portfolio']
    if 'Top Portfolio' not in port_earned:
        if 'Portfolio Expert' not in port_earned:
            if 'Profile Completed' not in port_earned:
                if 'Portfolio Creator' not in port_earned:
                    progression_list.append({
                        'category': 'Portfolio',
                        'current': 'None',
                        'next': 'Portfolio Creator',
                        'requirement': 'Add 1 Project, 1 Skill, and 1 Education',
                        'progress': int((sum([request.user.projects.exists(), request.user.skills.exists(), request.user.educations.exists()]) / 3.0) * 100)
                    })
                else:
                    progression_list.append({
                        'category': 'Portfolio',
                        'current': 'Portfolio Creator',
                        'next': 'Profile Completed',
                        'requirement': 'Completeness Score 70%+ (Current: {}%)'.format(p_score),
                        'progress': min(100, int(p_score / 70 * 100))
                    })
            else:
                progression_list.append({
                    'category': 'Portfolio',
                    'current': 'Profile Completed',
                    'next': 'Portfolio Expert',
                    'requirement': 'Completeness Score 90%+ (Current: {}%)'.format(p_score),
                    'progress': min(100, int(p_score / 90 * 100))
                })
        else:
            progression_list.append({
                'category': 'Portfolio',
                'current': 'Portfolio Expert',
                'next': 'Top Portfolio',
                'requirement': 'Completeness Score 100% (Current: {}%)'.format(p_score),
                'progress': p_score
            })
            
    # Readiness progression
    read_earned = [ub.badge.name for ub in earned_user_badges if ub.badge.category == 'Readiness']
    if 'Industry Ready' not in read_earned:
        if 'Placement Ready' not in read_earned:
            if 'Career Ready' not in read_earned:
                progression_list.append({
                    'category': 'Readiness',
                    'current': 'None',
                    'next': 'Career Ready',
                    'requirement': 'Placement Readiness 50%+ (Current: {}%)'.format(readiness),
                    'progress': min(100, int(readiness / 50 * 100))
                })
            else:
                progression_list.append({
                    'category': 'Readiness',
                    'current': 'Career Ready',
                    'next': 'Placement Ready',
                    'requirement': 'Placement Readiness 75%+ (Current: {}%)'.format(readiness),
                    'progress': min(100, int(readiness / 75 * 100))
                })
        else:
            progression_list.append({
                'category': 'Readiness',
                'current': 'Placement Ready',
                'next': 'Industry Ready',
                'requirement': 'Placement Readiness 90%+ (Current: {}%)'.format(readiness),
                'progress': min(100, int(readiness / 90 * 100))
            })

    context = {
        'earned_user_badges': earned_user_badges,
        'locked_badges': locked_badges,
        'progression_list': progression_list,
        'portfolio_score': p_score,
        'readiness': readiness,
    }
    return render(request, 'accounts/achievements.html', context)