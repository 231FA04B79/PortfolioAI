from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('register/verify/', views.verify_registration_email, name='verify_registration_email'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('resume/import/', views.resume_import_view, name='resume_import'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('forgot-password/verify/', views.verify_forgot_email, name='verify_forgot_email'),


    path('forgot-password/reset/', views.reset_password, name='reset_password'),
    path('settings/', views.account_settings, name='account_settings'),
    path('settings/change-password/ajax/', views.change_password_ajax, name='change_password_ajax'),
    path('achievements/', views.achievements_dashboard, name='achievements_dashboard'),
]
