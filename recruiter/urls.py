from django.urls import path

from . import views

urlpatterns = [
    path('', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('search/', views.student_search, name='student_search'),
    path('student/<slug:username>/', views.student_profile, name='student_profile'),
    path('student/<slug:username>/match/<int:jd_id>/', views.student_profile_job_match, name='student_profile_job_match'),
    path('compare/', views.compare_candidates, name='compare_candidates'),
]
