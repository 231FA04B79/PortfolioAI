from django.urls import path

from . import views

urlpatterns = [
    path('education/', views.education_list, name='education_list'),
    path('education/add/', views.education_create, name='education_create'),
    path('education/<int:pk>/edit/', views.education_edit, name='education_edit'),
    path('education/<int:pk>/delete/', views.education_delete, name='education_delete'),

    path('skills/', views.skill_list, name='skill_list'),
    path('skills/add/', views.skill_create, name='skill_create'),
    path('skills/<int:pk>/edit/', views.skill_edit, name='skill_edit'),
    path('skills/<int:pk>/delete/', views.skill_delete, name='skill_delete'),

    path('projects/', views.project_list, name='project_list'),
    path('projects/add/', views.project_create, name='project_create'),
    path('projects/<int:pk>/edit/', views.project_edit, name='project_edit'),
    path('projects/<int:pk>/delete/', views.project_delete, name='project_delete'),

    path('certifications/', views.certification_list, name='certificate_list'),
    path('certifications/add/', views.certification_create, name='certificate_create'),
    path('certifications/<int:pk>/edit/', views.certification_edit, name='certificate_edit'),
    path('certifications/<int:pk>/delete/', views.certification_delete, name='certificate_delete'),

    path('achievements/', views.achievement_list, name='achievement_list'),
    path('achievements/add/', views.achievement_create, name='achievement_create'),
    path('achievements/<int:pk>/edit/', views.achievement_edit, name='achievement_edit'),
    path('achievements/<int:pk>/delete/', views.achievement_delete, name='achievement_delete'),

    path('resume/download/', views.generate_resume, name='generate_resume'),
    path('resume/ats/', views.ats_resume_builder, name='ats_resume_builder'),
    path('search/', views.portfolio_search, name='portfolio_search'),
    path('<str:username>/', views.portfolio_view, name='portfolio_view'),
]
