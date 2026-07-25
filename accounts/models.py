from django.db import models
from django.contrib.auth.models import User


class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon_class = models.CharField(max_length=50, default='bi-award')
    category = models.CharField(max_length=50, default='General')
    level = models.CharField(max_length=20, default='Bronze')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'level', 'name']

    def __str__(self):
        return f"{self.name} ({self.category} - {self.level})"


class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='user_badges')
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-date_earned']

    def __str__(self):
        return f"{self.user.username} earned {self.badge.name}"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=100,
        blank=True
    )

    email_verified = models.BooleanField(
        default=False
    )

    professional_title = models.CharField(
        max_length=100,
        blank=True
    )

    phone = models.CharField(
        max_length=15,
        blank=True
    )

    location = models.CharField(
        max_length=100,
        blank=True
    )

    bio = models.TextField(
        blank=True
    )

    github = models.URLField(
        blank=True
    )

    linkedin = models.URLField(
        blank=True
    )

    portfolio_website = models.URLField(
        blank=True
    )

    profile_image = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True
    )

    cover_image = models.ImageField(
        upload_to='covers/',
        blank=True,
        null=True
    )

    # Coding Profiles
    leetcode_username = models.CharField(
        max_length=100,
        blank=True
    )

    codechef_username = models.CharField(
        max_length=100,
        blank=True
    )

    hackerrank_username = models.CharField(
        max_length=100,
        blank=True
    )

    # Generated Scores
    coding_score = models.IntegerField(
        default=0
    )

    consistency_score = models.IntegerField(
        default=0
    )

    problem_solving_score = models.IntegerField(
        default=0
    )

    # Gamification
    badges = models.ManyToManyField(
        Badge,
        blank=True,
        related_name='profiles'
    )

    # Recovery Code authentication
    recovery_code_hash = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    last_regenerated = models.DateTimeField(blank=True, null=True)

    @property
    def initials(self):
        if self.full_name:
            parts = self.full_name.split()
            if len(parts) >= 2:
                return (parts[0][0] + parts[-1][0]).upper()
            elif len(parts) == 1:
                return parts[0][:2].upper()
        return self.user.username[:2].upper()

    def __str__(self):
        return self.user.username
