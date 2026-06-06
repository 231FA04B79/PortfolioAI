from django import forms
from django.forms import TextInput, NumberInput

from .models import Education, Skill, Project, Certification, Achievement


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['education_type', 'degree', 'college_name', 'scoring_type', 'score_value', 'completion_year']
        widgets = {
            'education_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_education_type'}),
            'degree': forms.TextInput(attrs={'class': 'form-control'}),
            'college_name': forms.TextInput(attrs={'class': 'form-control'}),
            'scoring_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_scoring_type'}),
            'score_value': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_score_value'}),
            'completion_year': forms.TextInput(attrs={'class': 'form-control'}),
        }


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'level']
        labels = {'name': 'Skill Name', 'level': 'Proficiency (0-10)'}
        widgets = {
            'name': TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python'}),
            'level': NumberInput(attrs={'class': 'form-range', 'type': 'range', 'min': '0', 'max': '10', 'step': '1'}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'tech_stack', 'github_link', 'project_image']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
            'tech_stack': TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma separated technologies'}),
        }


class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['certificate_name', 'issuing_organization', 'issue_date', 'certificate_file']
        widgets = {
            'certificate_name': TextInput(attrs={'class': 'form-control'}),
            'issuing_organization': TextInput(attrs={'class': 'form-control'}),
        }


class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['title', 'description']
        widgets = {
            'title': TextInput(attrs={'class': 'form-control'}),
        }
