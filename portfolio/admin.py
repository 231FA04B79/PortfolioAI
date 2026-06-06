from django.contrib import admin

from .models import Achievement, Certification, Education, Project, Skill


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('degree', 'college_name', 'completion_year', 'user')
    search_fields = ('degree', 'college_name', 'user__username')
    list_filter = ('completion_year',)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'user')
    search_fields = ('name', 'user__username')
    list_filter = ('level',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'tech_stack', 'user__username')
    list_filter = ('created_at',)


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('certificate_name', 'issuing_organization', 'issue_date', 'user')
    search_fields = ('certificate_name', 'issuing_organization', 'user__username')
    list_filter = ('issue_date',)


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at')
    search_fields = ('title', 'user__username')
    list_filter = ('created_at',)
