from django.db import models
from django.contrib.auth.models import User

class JobDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_descriptions')
    title = models.CharField(max_length=200, default='Unnamed Job')
    raw_text = models.TextField()
    extracted_skills = models.JSONField(default=list, blank=True)
    extracted_technologies = models.JSONField(default=list, blank=True)
    extracted_experience = models.CharField(max_length=150, blank=True)
    extracted_certifications = models.JSONField(default=list, blank=True)
    extracted_keywords = models.JSONField(default=list, blank=True)
    extracted_soft_skills = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.created_at.strftime('%Y-%m-%d')})"

class LearningRoadmap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roadmaps')
    target_role = models.CharField(max_length=200)
    job_description = models.ForeignKey(JobDescription, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Roadmap for {self.target_role} ({self.user.username})"

class RoadmapStep(models.Model):
    roadmap = models.ForeignKey(LearningRoadmap, on_delete=models.CASCADE, related_name='steps')
    week_number = models.PositiveIntegerField()
    title = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ['week_number']

    def __str__(self):
        return f"Week {self.week_number}: {self.title}"
