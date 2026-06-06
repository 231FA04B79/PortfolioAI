from django.urls import path
from . import views

urlpatterns = [
    path('github/', views.github_analyzer, name='github_analyzer'),
    path('resume/', views.resume_analyzer, name='resume_analyzer'),
    path('skill-gap/', views.skill_gap, name='skill_gap'),
    path('career-recommendation/', views.career_recommendation, name='career_recommendation'),
    path('interview-questions/', views.interview_questions, name='interview_questions'),
    path('portfolio-score/', views.portfolio_score, name='portfolio_score'),
    path('coding/', views.coding_analyzer, name='coding_analyzer'),
    path('readiness/', views.placement_readiness_view, name='placement_readiness'),
    path('projects/', views.project_recommender, name='project_recommender'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('jd-analyzer/', views.job_description_analyzer, name='job_description_analyzer'),
    path('roadmap/step/<int:step_id>/toggle/', views.toggle_roadmap_step, name='toggle_roadmap_step'),
    path('portfolio-review/', views.portfolio_review, name='portfolio_review'),
    path('profile-generator/', views.ai_profile_generator, name='ai_profile_generator'),
    path('quality-score/', views.portfolio_quality_score, name='portfolio_quality_score'),
]
