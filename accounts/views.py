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
            # Save pending registration details to session
            request.session['pending_registration'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
            }
            request.session.modified = True
            
            # Send verification OTP
            from utils.email_otp_service import generate_otp, send_otp_email
            otp_code = generate_otp()
            send_otp_email(form.cleaned_data['email'], otp_code, purpose='registration')
            
            messages.info(request, f"A verification OTP code has been sent to your email: {form.cleaned_data['email']}.")
            return redirect('verify_registration_email')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def verify_registration_email(request):
    pending = request.session.get('pending_registration')
    if not pending:
        messages.error(request, "No pending registration found. Please register first.")
        return redirect('register')
        
    email = pending['email']
    
    if request.method == 'POST':
        action = request.POST.get('action')
        from utils.email_otp_service import generate_otp, send_otp_email, verify_otp
        
        if action == 'resend':
            otp_code = generate_otp()
            send_otp_email(email, otp_code, purpose='registration')
            messages.success(request, "A new verification OTP code has been sent.")
        else:
            code = request.POST.get('otp', '').strip()
            is_valid, msg = verify_otp(email, code, purpose='registration')
            
            if is_valid:
                from django.contrib.auth.models import User
                # Create user account
                user = User.objects.create_user(
                    username=pending['username'],
                    email=pending['email'],
                    password=pending['password']
                )
                # Create profile and mark email as verified
                profile, _ = Profile.objects.get_or_create(user=user)
                profile.email_verified = True
                profile.full_name = pending['username']
                profile.save()
                
                # Clear pending registration session keys
                del request.session['pending_registration']
                request.session.modified = True
                
                messages.success(request, "Account created successfully. Please login.")
                return redirect('login')
            else:
                messages.error(request, msg)
                
    context = {'email': email, 'purpose': 'registration'}
    return render(request, 'accounts/verify_email_otp.html', context)


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, "Please enter your registered email address.")
            return render(request, 'accounts/forgot_password.html')
            
        from django.contrib.auth.models import User
        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, "This email address is not registered.")
            return render(request, 'accounts/forgot_password.html')
            
        # Send verification OTP
        from utils.email_otp_service import generate_otp, send_otp_email
        otp_code = generate_otp()
        send_otp_email(email, otp_code, purpose='password_reset')
        
        request.session['email_otp_reset_email'] = email
        request.session.modified = True
        
        messages.info(request, f"A verification OTP code has been sent to your registered email: {email}.")
        return redirect('verify_forgot_email')
        
    return render(request, 'accounts/forgot_password.html')


def verify_forgot_email(request):
    email = request.session.get('email_otp_reset_email')
    if not email:
        messages.error(request, "No active password reset session found. Please enter your email again.")
        return redirect('forgot_password')
        
    if request.method == 'POST':
        action = request.POST.get('action')
        from utils.email_otp_service import generate_otp, send_otp_email, verify_otp
        
        if action == 'resend':
            otp_code = generate_otp()
            send_otp_email(email, otp_code, purpose='password_reset')
            messages.success(request, "A new verification OTP code has been sent.")
        else:
            code = request.POST.get('otp', '').strip()
            is_valid, msg = verify_otp(email, code, purpose='password_reset')
            
            if is_valid:
                request.session['email_password_reset_allowed'] = True
                request.session.modified = True
                return redirect('reset_password')
            else:
                messages.error(request, msg)
                
    context = {'email': email, 'purpose': 'reset'}
    return render(request, 'accounts/verify_reset_otp.html', context)


def reset_password(request):
    if not request.session.get('email_password_reset_allowed'):
        messages.error(request, "Unauthorized password reset attempt. Please verify your email first.")
        return redirect('forgot_password')
        
    email = request.session.get('email_otp_reset_email')
    if request.method == 'POST':
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        
        errors = []
        if password != password_confirm:
            errors.append("Passwords do not match.")
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long.")
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
            return render(request, 'accounts/reset_password.html')
            
        # Django validation check
        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        from django.contrib.auth.models import User
        user = User.objects.filter(email=email).first()
        if not user:
            messages.error(request, "User not found.")
            return redirect('forgot_password')
            
        try:
            validate_password(password, user)
        except ValidationError as ve:
            for msg in ve.messages:
                messages.error(request, msg)
            return render(request, 'accounts/reset_password.html')
            
        # Update password
        user.set_password(password)
        user.save()
        
        # Clear session reset keys
        if 'email_otp_reset_email' in request.session: del request.session['email_otp_reset_email']
        if 'email_password_reset_allowed' in request.session: del request.session['email_password_reset_allowed']
        request.session.modified = True
        
        # Set Profile email_verified to True if it wasn't already
        profile, _ = Profile.objects.get_or_create(user=user)
        if not profile.email_verified:
            profile.email_verified = True
            profile.save()
            
        messages.success(request, "Your password has been reset successfully. Please login with your new credentials.")
        return redirect('login')
        
    return render(request, 'accounts/reset_password.html')




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
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from accounts.models import Badge, UserBadge
from utils.email_otp_service import generate_otp, send_otp_email, verify_otp
from django.contrib.auth.models import User

@login_required
def account_settings(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # Store settings in session for display
    notifications_enabled = request.session.get('notifications_enabled', True)
    privacy_mode = request.session.get('privacy_mode', False)
    
    # Handle forms
    profile_form = ProfileForm(instance=profile)
    
    # Track OTP input display state
    show_otp_input = False
    otp_purpose = None
    
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
                profile.email_verified = False
                profile.save()
                update_user_badges(request.user)
                messages.success(request, f"Email address updated to {new_email}. Please verify your new email.")
                return redirect('account_settings')
                
        elif action == 'send_verify_otp':
            otp_code = generate_otp()
            send_otp_email(request.user.email, otp_code, purpose='email_verification')
            show_otp_input = True
            otp_purpose = 'email_verification'
            messages.info(request, f"A verification code has been sent to {request.user.email}.")
            
        elif action == 'verify_email_otp':
            code = request.POST.get('otp', '').strip()
            is_valid, msg = verify_otp(request.user.email, code, purpose='email_verification')
            if is_valid:
                profile.email_verified = True
                profile.save()
                update_user_badges(request.user)
                messages.success(request, "Your email has been verified successfully!")
                return redirect('account_settings')
            else:
                messages.error(request, msg)
                show_otp_input = True
                otp_purpose = 'email_verification'
                
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
        'show_otp_input': show_otp_input,
        'otp_purpose': otp_purpose,
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
        
        # Send OTP
        otp_code = generate_otp()
        send_otp_email(user.email, otp_code, purpose='password_change')
        request.session['password_change_step1_passed'] = True
        request.session.modified = True
        return JsonResponse({'status': 'success', 'message': 'Password verified. OTP code sent.'})
        
    elif step == 2:
        if not request.session.get('password_change_step1_passed'):
            return JsonResponse({'status': 'error', 'message': 'Unauthorized. Please complete Step 1 first.'})
            
        otp_code = data.get('otp', '').strip()
        is_valid, msg = verify_otp(user.email, otp_code, purpose='password_change')
        if is_valid:
            request.session['password_change_otp_verified'] = True
            request.session.modified = True
            return JsonResponse({'status': 'success', 'message': 'OTP verified successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': msg})
            
    elif step == 3:
        if not request.session.get('password_change_otp_verified'):
            return JsonResponse({'status': 'error', 'message': 'Unauthorized. Please complete OTP verification first.'})
            
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
        
        # Send confirmation email
        send_mail(
            subject="Password Changed - PortfolioAI",
            message="Hello,\n\nYour password was successfully changed.\n\nPortfolioAI Team",
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost'),
            recipient_list=[user.email],
            fail_silently=True
        )
        
        # Clear session flags
        if 'password_change_step1_passed' in request.session: del request.session['password_change_step1_passed']
        if 'password_change_otp_verified' in request.session: del request.session['password_change_otp_verified']
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