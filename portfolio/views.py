from io import BytesIO

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from accounts.models import Profile
from .models import Education, Skill, Project, Certification, Achievement
from .forms import (
    EducationForm,
    SkillForm,
    ProjectForm,
    CertificationForm,
    AchievementForm,
)


@login_required
def education_list(request):
    items = Education.objects.filter(user=request.user).order_by('-completion_year')
    return render(request, 'portfolio/education_list.html', {'educations': items})


@login_required
def education_create(request):
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.user = request.user
            education.save()
            messages.success(request, 'Education entry added successfully.')
            return redirect('education_list')
    else:
        form = EducationForm()
    return render(request, 'portfolio/education_form.html', {'form': form, 'title': 'Add Education'})


@login_required
def education_edit(request, pk):
    education = get_object_or_404(Education, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, 'Education entry updated successfully.')
            return redirect('education_list')
    else:
        form = EducationForm(instance=education)
    return render(request, 'portfolio/education_form.html', {'form': form, 'title': 'Edit Education'})


@login_required
def education_delete(request, pk):
    education = get_object_or_404(Education, pk=pk, user=request.user)
    if request.method == 'POST':
        education.delete()
        messages.success(request, 'Education entry deleted successfully.')
        return redirect('education_list')
    return render(request, 'portfolio/confirm_delete.html', {'object': education, 'title': 'Delete Education'})


@login_required
def skill_list(request):
    def _skill_meta(level):
        if level >= 9:
            return '#7c3aed', '#a78bfa', '#f5f3ff', 'Expert'
        elif level >= 7:
            return '#2563eb', '#60a5fa', '#eff6ff', 'Advanced'
        elif level >= 5:
            return '#0891b2', '#38bdf8', '#ecfeff', 'Intermediate'
        elif level >= 3:
            return '#d97706', '#fbbf24', '#fffbeb', 'Beginner'
        else:
            return '#64748b', '#94a3b8', '#f8fafc', 'Learning'

    skills = list(Skill.objects.filter(user=request.user).order_by('-level'))
    for s in skills:
        try:
            s.percent = int(s.level) * 10
        except Exception:
            s.percent = 0
        s.accent, s.accent2, s.bg, s.desc = _skill_meta(s.level)
    return render(request, 'portfolio/skill_list.html', {'skills': skills})


@login_required
def skill_create(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            messages.success(request, 'Skill added successfully.')
            return redirect('skill_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SkillForm()
    return render(request, 'portfolio/skill_form.html', {'form': form, 'title': 'Add Skill'})


@login_required
def skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Skill updated successfully.')
            return redirect('skill_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = SkillForm(instance=skill)
    return render(request, 'portfolio/skill_form.html', {'form': form, 'title': 'Edit Skill'})


@login_required
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk, user=request.user)
    if request.method == 'POST':
        skill.delete()
        messages.success(request, 'Skill deleted.')
        return redirect('skill_list')
    return render(request, 'portfolio/confirm_delete.html', {'object': skill, 'title': 'Delete Skill'})


@login_required
def project_list(request):
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'portfolio/project_list.html', {'projects': projects})


@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            messages.success(request, 'Project added successfully.')
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'portfolio/project_form.html', {'form': form, 'title': 'Add Project'})


@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully.')
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'portfolio/project_form.html', {'form': form, 'title': 'Edit Project'})


@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk, user=request.user)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully.')
        return redirect('project_list')
    return render(request, 'portfolio/confirm_delete.html', {'object': project, 'title': 'Delete Project'})


@login_required
def certification_list(request):
    certifications = Certification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'portfolio/certificate_list.html', {'certifications': certifications})


@login_required
def certification_create(request):
    if request.method == 'POST':
        form = CertificationForm(request.POST, request.FILES)
        if form.is_valid():
            certification = form.save(commit=False)
            certification.user = request.user
            certification.save()
            messages.success(request, 'Certification added successfully.')
            return redirect('certificate_list')
    else:
        form = CertificationForm()
    return render(request, 'portfolio/certificate_form.html', {'form': form, 'title': 'Add Certification'})


@login_required
def certification_edit(request, pk):
    certification = get_object_or_404(Certification, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CertificationForm(request.POST, request.FILES, instance=certification)
        if form.is_valid():
            form.save()
            messages.success(request, 'Certification updated successfully.')
            return redirect('certificate_list')
    else:
        form = CertificationForm(instance=certification)
    return render(request, 'portfolio/certificate_form.html', {'form': form, 'title': 'Edit Certification'})


@login_required
def certification_delete(request, pk):
    certification = get_object_or_404(Certification, pk=pk, user=request.user)
    if request.method == 'POST':
        certification.delete()
        messages.success(request, 'Certification deleted successfully.')
        return redirect('certificate_list')
    return render(request, 'portfolio/confirm_delete.html', {'object': certification, 'title': 'Delete Certification'})


@login_required
def achievement_list(request):
    achievements = Achievement.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'portfolio/achievement_list.html', {'achievements': achievements})


@login_required
def achievement_create(request):
    if request.method == 'POST':
        form = AchievementForm(request.POST)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.user = request.user
            achievement.save()
            messages.success(request, 'Achievement added successfully.')
            return redirect('achievement_list')
    else:
        form = AchievementForm()
    return render(request, 'portfolio/achievement_form.html', {'form': form, 'title': 'Add Achievement'})


@login_required
def achievement_edit(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AchievementForm(request.POST, instance=achievement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Achievement updated successfully.')
            return redirect('achievement_list')
    else:
        form = AchievementForm(instance=achievement)
    return render(request, 'portfolio/achievement_form.html', {'form': form, 'title': 'Edit Achievement'})


@login_required
def achievement_delete(request, pk):
    achievement = get_object_or_404(Achievement, pk=pk, user=request.user)
    if request.method == 'POST':
        achievement.delete()
        messages.success(request, 'Achievement deleted successfully.')
        return redirect('achievement_list')
    return render(request, 'portfolio/confirm_delete.html', {'object': achievement, 'title': 'Delete Achievement'})


from utils.ai_helpers import generate_ai_summary, improve_ai_wording, highlight_ai_strengths

@login_required
def generate_resume(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    
    # Track resume download view log
    from portfolio.models import PortfolioViewTracker
    PortfolioViewTracker.objects.create(
        user=request.user,
        event_type='resume_download',
        viewer_ip=request.META.get('REMOTE_ADDR', '127.0.0.1'),
        is_recruiter=False
    )
    educations = Education.objects.filter(user=request.user).order_by('-completion_year')
    skills = Skill.objects.filter(user=request.user).order_by('-level')
    projects = Project.objects.filter(user=request.user).order_by('-created_at')
    certifications = Certification.objects.filter(user=request.user).order_by('-created_at')
    achievements = Achievement.objects.filter(user=request.user).order_by('-created_at')

    # Query parameters
    template = request.GET.get('template', 'ats').lower()
    ai_enhance = request.GET.get('ai_enhance', 'false').lower() == 'true'

    # AI Wording optimizations
    ai_summary = ""
    highlighted_strengths = []
    
    if ai_enhance:
        ai_summary = generate_ai_summary(profile, skills, projects)
        highlighted_strengths = highlight_ai_strengths(skills, certifications)

    # Styling configurations based on template type
    if template == 'modern':
        primary_color = (0.14, 0.38, 0.92) # Royal Blue
        title_font = 'Helvetica-Bold'
        body_font = 'Helvetica'
        section_underline = True
    elif template == 'professional':
        primary_color = (0.36, 0.12, 0.69) # Deep Indigo
        title_font = 'Times-Bold'
        body_font = 'Times-Roman'
        section_underline = True
    elif template == 'fresher':
        primary_color = (0.02, 0.71, 0.83) # Aqua / Cyan
        title_font = 'Helvetica-Bold'
        body_font = 'Helvetica'
        section_underline = False
    else: # 'ats' or default
        primary_color = (0.0, 0.0, 0.0) # Plain Black for ATS compatibility
        title_font = 'Helvetica-Bold'
        body_font = 'Helvetica'
        section_underline = False

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Resume_{request.user.username}_{template}")

    # Draw footer helper
    def draw_footer(canvas_obj):
        canvas_obj.saveState()
        canvas_obj.setFont(body_font, 8)
        canvas_obj.setFillColorRGB(0.5, 0.5, 0.5)
        # Draw divider line
        canvas_obj.setStrokeColorRGB(0.85, 0.85, 0.85)
        canvas_obj.setLineWidth(0.5)
        canvas_obj.line(54, 45, letter[0] - 54, 45)
        # Page info
        page_num = canvas_obj.getPageNumber()
        canvas_obj.drawRightString(letter[0] - 54, 32, f"Page {page_num}")
        canvas_obj.drawString(54, 32, f"Resume ({template.upper()}) | {profile.full_name or request.user.username}")
        canvas_obj.restoreState()

    def new_page():
        draw_footer(pdf)
        pdf.showPage()
        # Set fonts again as showPage resets context
        pdf.setFont(body_font, 10)
        pdf.setFillColorRGB(0.1, 0.1, 0.1)

    # 1. Header Information
    pdf.setFont(title_font, 18)
    pdf.setFillColorRGB(*primary_color)
    pdf.drawString(54, 750, profile.full_name or request.user.get_full_name() or request.user.username)
    
    pdf.setFont(body_font, 10)
    pdf.setFillColorRGB(0.2, 0.2, 0.2)
    pdf.drawString(54, 734, profile.professional_title or "Software Developer")
    
    # Sub-info row (Email, Phone, Location)
    contact_info = []
    contact_info.append(f"Email: {request.user.email}")
    if profile.phone:
        contact_info.append(f"Phone: {profile.phone}")
    if profile.location:
        contact_info.append(f"Location: {profile.location}")
    pdf.drawString(54, 718, " | ".join(contact_info))

    # Links row (GitHub, LinkedIn, Website)
    links_info = []
    if profile.github:
        links_info.append(f"GitHub: {profile.github.replace('https://', '')}")
    if profile.linkedin:
        links_info.append(f"LinkedIn: {profile.linkedin.replace('https://', '')}")
    if profile.portfolio_website:
        links_info.append(f"Portfolio: {profile.portfolio_website.replace('https://', '')}")
    
    if links_info:
        pdf.drawString(54, 702, " | ".join(links_info))
        y = 675
    else:
        y = 690

    # 2. Draw Section Helper
    def draw_section_heading(title_text, curr_y):
        curr_y -= 10
        pdf.setFont(title_font, 12)
        pdf.setFillColorRGB(*primary_color)
        pdf.drawString(54, curr_y, title_text)
        
        if section_underline:
            pdf.setStrokeColorRGB(*primary_color)
            pdf.setLineWidth(0.8)
            pdf.line(54, curr_y - 4, letter[0] - 54, curr_y - 4)
            return curr_y - 20
        else:
            return curr_y - 16

    # Summary Section
    y = draw_section_heading("Professional Summary", y)
    pdf.setFont(body_font, 9.5)
    pdf.setFillColorRGB(0.15, 0.15, 0.15)
    
    summary_text = ai_summary if ai_enhance else profile.bio
    if not summary_text:
        summary_text = "Goal-oriented developer dedicated to engineering reliable systems and writing clean, maintainable code."

    # Simple text wrap
    words = summary_text.split()
    lines_list = []
    current_line = []
    for w in words:
        current_line.append(w)
        # Check size limit
        line_cand = " ".join(current_line)
        if pdf.stringWidth(line_cand, body_font, 9.5) > (letter[0] - 108):
            current_line.pop()
            lines_list.append(" ".join(current_line))
            current_line = [w]
    if current_line:
        lines_list.append(" ".join(current_line))

    for line in lines_list:
        if y < 80:
            new_page()
            y = 740
        pdf.drawString(54, y, line)
        y -= 13
    y -= 10

    # Layout builder helper
    def render_education(curr_y):
        curr_y = draw_section_heading("Education", curr_y)
        pdf.setFont(body_font, 9.5)
        pdf.setFillColorRGB(0.1, 0.1, 0.1)
        for edu in educations:
            if curr_y < 80:
                new_page()
                curr_y = 740
            
            degree_str = f"{edu.degree} - {edu.college_name}"
            year_str = f"Graduation: {edu.completion_year}"
            
            pdf.drawString(64, curr_y, degree_str)
            pdf.drawRightString(letter[0] - 54, curr_y, year_str)
            curr_y -= 13
            
            if edu.score_value:
                if curr_y < 80:
                    new_page()
                    curr_y = 740
                score_suffix = "%" if edu.scoring_type == "Percentage" else ""
                pdf.drawString(74, curr_y, f"{edu.scoring_type}: {edu.score_value}{score_suffix}")
                curr_y -= 14
            curr_y -= 4
        return curr_y

    def render_projects(curr_y):
        curr_y = draw_section_heading("Key Projects", curr_y)
        pdf.setFont(body_font, 9.5)
        for proj in projects:
            if curr_y < 100:
                new_page()
                curr_y = 740
            
            pdf.setFont(title_font, 10.5)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawString(64, curr_y, proj.title)
            
            # Draw Github / link right aligned
            if proj.github_link:
                pdf.setFont(body_font, 9)
                pdf.setFillColorRGB(0.4, 0.4, 0.4)
                pdf.drawRightString(letter[0] - 54, curr_y, proj.github_link.replace('https://', ''))
            
            curr_y -= 13
            
            # Description text (possibly enhanced by AI)
            pdf.setFont(body_font, 9.5)
            pdf.setFillColorRGB(0.18, 0.18, 0.18)
            desc_text = improve_ai_wording(proj.description) if ai_enhance else proj.description
            
            # Simple text wrap
            words_proj = desc_text.split()
            lines_proj = []
            cur_line = []
            for w in words_proj:
                cur_line.append(w)
                if pdf.stringWidth(" ".join(cur_line), body_font, 9.5) > (letter[0] - 128):
                    cur_line.pop()
                    lines_proj.append(" ".join(cur_line))
                    cur_line = [w]
            if cur_line:
                lines_proj.append(" ".join(cur_line))
                
            for lp in lines_proj:
                if curr_y < 80:
                    new_page()
                    curr_y = 740
                pdf.drawString(74, curr_y, f"\u2022 {lp}")
                curr_y -= 13
                
            # Technologies Stack
            if proj.tech_stack:
                if curr_y < 80:
                    new_page()
                    curr_y = 740
                pdf.setFont(body_font, 9)
                pdf.setFillColorRGB(0.3, 0.3, 0.3)
                pdf.drawString(74, curr_y, f"Technologies: {proj.tech_stack}")
                curr_y -= 14
                
            curr_y -= 6
        return curr_y

    def render_skills(curr_y):
        curr_y = draw_section_heading("Technical Expertise", curr_y)
        pdf.setFont(body_font, 9.5)
        pdf.setFillColorRGB(0.1, 0.1, 0.1)
        
        # Display Core Strengths first if AI enabled
        if ai_enhance and highlighted_strengths:
            pdf.setFont(title_font, 9.5)
            pdf.drawString(64, curr_y, "Key Strengths: ")
            pdf.setFont(body_font, 9.5)
            pdf.drawString(140, curr_y, ", ".join(highlighted_strengths))
            curr_y -= 15
            
        skills_str = ", ".join([skill.name for skill in skills])
        if not skills_str:
            skills_str = "No skills listed yet."
            
        words_sk = skills_str.split()
        lines_sk = []
        cur_line = []
        for w in words_sk:
            cur_line.append(w)
            if pdf.stringWidth(" ".join(cur_line), body_font, 9.5) > (letter[0] - 128):
                cur_line.pop()
                lines_sk.append(" ".join(cur_line))
                cur_line = [w]
        if cur_line:
            lines_sk.append(" ".join(cur_line))
            
        pdf.setFont(body_font, 9.5)
        pdf.setFillColorRGB(0.1, 0.1, 0.1)
        for lsk in lines_sk:
            if curr_y < 80:
                new_page()
                curr_y = 740
            pdf.drawString(64, curr_y, lsk)
            curr_y -= 13
        return curr_y - 8

    def render_certifications(curr_y):
        curr_y = draw_section_heading("Professional Credentials", curr_y)
        pdf.setFont(body_font, 9.5)
        pdf.setFillColorRGB(0.1, 0.1, 0.1)
        for cert in certifications:
            if curr_y < 80:
                new_page()
                curr_y = 740
                
            date_str = cert.issue_date.strftime("%B %Y") if cert.issue_date else "Verified"
            cert_str = f"{cert.certificate_name} - {cert.issuing_organization}"
            
            pdf.drawString(64, curr_y, cert_str)
            pdf.drawRightString(letter[0] - 54, curr_y, date_str)
            curr_y -= 15
        return curr_y

    def render_achievements(curr_y):
        curr_y = draw_section_heading("Awards & Achievements", curr_y)
        pdf.setFont(body_font, 9.5)
        pdf.setFillColorRGB(0.1, 0.1, 0.1)
        for ach in achievements:
            if curr_y < 80:
                new_page()
                curr_y = 740
            
            pdf.drawString(64, curr_y, f"\u2022 {ach.title}")
            if ach.description:
                curr_y -= 13
                if curr_y < 80:
                    new_page()
                    curr_y = 740
                pdf.setFillColorRGB(0.3, 0.3, 0.3)
                pdf.drawString(74, curr_y, ach.description)
                pdf.setFillColorRGB(0.1, 0.1, 0.1)
            curr_y -= 15
        return curr_y

    # Arrange sections based on template choices
    if template == 'fresher':
        # Fresher Template places Education first, then Skills, then Projects
        y = render_education(y)
        y = render_skills(y)
        y = render_projects(y)
        y = render_certifications(y)
        y = render_achievements(y)
    else:
        # standard structure for ATS, Modern, Professional
        y = render_skills(y)
        y = render_projects(y)
        y = render_education(y)
        y = render_certifications(y)
        y = render_achievements(y)

    draw_footer(pdf)
    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=Resume_{request.user.username}_{template}.pdf'
    return response


@login_required
def ats_resume_builder(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    skills = request.user.skills.all()
    projects = request.user.projects.all()
    educations = request.user.educations.all()
    certs = request.user.certifications.all()
    achievements = request.user.achievements.all()

    # Dynamic summary generation
    generated_summary = generate_ai_summary(profile, skills, projects)
    highlighted_strengths = highlight_ai_strengths(skills, certs)

    # ATS Scoring Calculation matching updated portfolio weights
    score = 0
    suggestions = []

    # 1. Profile fields (20 points max: 4pt each for Name, Bio, Phone, Location, Title)
    profile_fields = [profile.full_name, profile.bio, profile.phone, profile.location, profile.professional_title]
    profile_score = sum(4 for f in profile_fields if f)
    score += profile_score
    if profile_score < 20:
        suggestions.append("Update location, professional title, and bio in your Profile Settings to secure 20% profile weight.")

    # 2. Skills (20 points max: 4pt per skill, target 5 skills)
    skills_score = min(20, len(skills) * 4)
    score += skills_score
    if len(skills) < 5:
        suggestions.append("Add at least 5 tech skills to your skills inventory to earn full 20% ATS keyword matching weight.")

    # 3. Projects (20 points max: 10pt per project, target 2 projects)
    projects_score = min(20, len(projects) * 10)
    score += projects_score
    if len(projects) < 2:
        suggestions.append("Describe at least 2 key projects with tech stack descriptions to claim full 20% projects weight.")

    # 4. Education (15 points max: 5pt per entry, target 3 entries)
    edu_score = min(15, len(educations) * 5)
    score += edu_score
    if len(educations) < 2:
        suggestions.append("List high school, diploma, or degree background in Education for the 15% educational check.")

    # 5. Certifications (10 points max: 5pt per cert, target 2 certs)
    certs_score = min(10, len(certs) * 5)
    score += certs_score
    if len(certs) < 1:
        suggestions.append("Earn and list technical certifications to claim full 10% credentials weight.")

    # 6. Achievements (5 points max: 2.5pt per entry, target 2 entries)
    ach_score = min(5, int(len(achievements) * 2.5))
    score += ach_score
    if len(achievements) < 1:
        suggestions.append("Add scholarships, hackathon rankings, or Dean's list to earn 5% achievements weight.")

    # 7. GitHub link check (10 points max)
    github_score = 10 if profile.github else 0
    score += github_score
    if not profile.github:
        suggestions.append("Link your public GitHub profile link for an instant 10% placement score boost.")

    # Suggest missing popular tech keywords
    keyword_pool = ['REST APIs', 'Docker', 'CI/CD', 'AWS', 'Kubernetes', 'Git', 'Agile', 'Unit Testing', 'SQL', 'Django']
    user_skills_lower = [s.name.lower() for s in skills]
    recommended_keywords = [kw for kw in keyword_pool if kw.lower() not in user_skills_lower]

    context = {
        'ats_score': min(100, score),
        'suggestions': suggestions,
        'recommended_keywords': recommended_keywords,
        'generated_summary': generated_summary,
        'highlighted_strengths': highlighted_strengths,
        'profile': profile,
        'skills': skills,
        'projects': projects,
        'educations': educations,
        'certifications': certs,
        'achievements': achievements,
    }
    return render(request, 'portfolio/ats_resume_builder.html', context)


def portfolio_view(request, username):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, username=username)
    profile, _ = Profile.objects.get_or_create(user=user)
    
    # Track view log (excluding self-views to keep stats accurate)
    is_recruiter = False
    if request.user.is_authenticated:
        from recruiter.views import is_recruiter as check_recruiter
        is_recruiter = check_recruiter(request.user)
        
    if request.user != user:
        from portfolio.models import PortfolioViewTracker
        PortfolioViewTracker.objects.create(
            user=user,
            event_type='portfolio_view',
            viewer_ip=request.META.get('REMOTE_ADDR', '127.0.0.1'),
            is_recruiter=is_recruiter
        )

    projects = list(user.projects.all())
    for project in projects:
        if project.tech_stack:
            project.tech_list = [t.strip() for t in project.tech_stack.split(',') if t.strip()]
        else:
            project.tech_list = []

    # Get absolute URL for QR code generation
    absolute_url = request.build_absolute_uri()
    qr_code_url = f"https://api.qrserver.com/v1/create-qr-code/?size=150x150&data={absolute_url}"

    context = {
        'owner': user,
        'profile': profile,
        'educations': user.educations.all(),
        'skills': user.skills.all(),
        'projects': projects,
        'certifications': user.certifications.all(),
        'achievements': user.achievements.all(),
        'qr_code_url': qr_code_url,
    }
    return render(request, 'portfolio/portfolio_view.html', context)


@login_required
def portfolio_search(request):
    from django.contrib.auth.models import User
    from django.db.models import Q
    from django.http import JsonResponse
    from utils.scoring_utils import get_portfolio_score

    query = request.GET.get('q', '').strip()
    is_json = request.GET.get('json', '') == '1' or request.headers.get('x-requested-with') == 'XMLHttpRequest'

    results = []
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(profile__full_name__icontains=query) |
            Q(profile__professional_title__icontains=query)
        ).distinct()[:15]

        for u in users:
            profile, _ = Profile.objects.get_or_create(user=u)
            p_score = get_portfolio_score(u)
            
            image_url = ""
            if profile.profile_image:
                image_url = profile.profile_image.url
            
            results.append({
                'username': u.username,
                'full_name': profile.full_name or u.username,
                'professional_title': profile.professional_title or "Developer",
                'image_url': image_url,
                'portfolio_score': p_score,
                'url': f"/portfolio/{u.username}/",
            })

    if is_json:
        return JsonResponse({'results': results})

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'portfolio/search_results.html', context)
