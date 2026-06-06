from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Education(models.Model):
    EDUCATION_TYPES = [
        ('SSC', 'SSC'),
        ('Intermediate', 'Intermediate'),
        ('Diploma', 'Diploma'),
        ('Undergraduate', 'Undergraduate'),
        ('Postgraduate', 'Postgraduate'),
        ('PhD', 'PhD'),
        ('Other', 'Other'),
    ]
    SCORING_TYPES = [
        ('CGPA', 'CGPA'),
        ('Percentage', 'Percentage'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='educations'
    )
    education_type = models.CharField(max_length=50, choices=EDUCATION_TYPES, default='Other')
    degree = models.CharField(max_length=200)
    college_name = models.CharField(max_length=250)
    scoring_type = models.CharField(max_length=20, choices=SCORING_TYPES, default='CGPA')
    score_value = models.CharField(max_length=20, blank=True)
    completion_year = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def cgpa(self):
        return self.score_value

    @cgpa.setter
    def cgpa(self, value):
        self.score_value = value

    class Meta:
        ordering = ['-completion_year', 'college_name']
        verbose_name = 'Education'
        verbose_name_plural = 'Education'

    def __str__(self):
        return f"{self.degree} at {self.college_name}"


class Skill(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='skills'
    )
    name = models.CharField(max_length=100)
    level = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-level', 'name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'

    def __str__(self):
        return self.name


class Project(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tech_stack = models.CharField(max_length=250, blank=True)
    github_link = models.URLField(blank=True)
    project_image = models.ImageField(
        upload_to='project_images/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'

    def __str__(self):
        return self.title


class Certification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='certifications'
    )
    certificate_name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200, blank=True)
    issue_date = models.DateField(blank=True, null=True)
    certificate_file = models.FileField(
        upload_to='certificates/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-issue_date', 'certificate_name']
        verbose_name = 'Certification'
        verbose_name_plural = 'Certifications'

    def __str__(self):
        return self.certificate_name


class Achievement(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Achievement'
        verbose_name_plural = 'Achievements'

    def __str__(self):
        return self.title


class PortfolioViewTracker(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='view_logs'
    )
    event_type = models.CharField(max_length=50) # 'portfolio_view', 'resume_download'
    viewer_ip = models.CharField(max_length=45, blank=True)
    is_recruiter = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Portfolio View Log'
        verbose_name_plural = 'Portfolio View Logs'

    def __str__(self):
        return f"{self.event_type} on {self.user.username} by {self.viewer_ip} ({self.created_at})"
