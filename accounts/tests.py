import time
from datetime import timedelta
from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User
from accounts.models import Profile
from utils.recovery_service import (
    generate_recovery_code,
    hash_recovery_code,
    verify_recovery_code
)

# ──────────────────────────────────────────────
# Unit Tests for utils/recovery_service.py
# ──────────────────────────────────────────────

class RecoveryServiceTests(TestCase):
    """Tests for the recovery_service utilities."""

    def test_generate_recovery_code_format(self):
        """Code should start with PAI- and follow the group format PAI-XXXX-XXXX-XXXX."""
        code = generate_recovery_code()
        self.assertTrue(code.startswith("PAI-"))
        parts = code.split("-")
        self.assertEqual(len(parts), 4)
        self.assertEqual(parts[0], "PAI")
        for part in parts[1:]:
            self.assertEqual(len(part), 4)
            self.assertTrue(part.isalnum())
            self.assertEqual(part, part.upper())

    def test_unique_codes(self):
        """Consecutive calls should generate unique codes."""
        codes = {generate_recovery_code() for _ in range(50)}
        self.assertEqual(len(codes), 50)

    def test_hashing_and_verification(self):
        """Hashed code should verify successfully against plain code, and reject incorrect ones."""
        code = generate_recovery_code()
        hashed = hash_recovery_code(code)
        
        self.assertNotEqual(code, hashed)
        self.assertTrue(verify_recovery_code(code, hashed))
        self.assertFalse(verify_recovery_code("PAI-INVALID-CODE-HERE", hashed))
        self.assertFalse(verify_recovery_code("", hashed))
        self.assertFalse(verify_recovery_code(None, hashed))


# ──────────────────────────────────────────────
# Integration Tests for Registration Flow
# ──────────────────────────────────────────────

class RegistrationFlowTests(TestCase):
    """Integration tests for the registration and recovery code setup flow."""

    def setUp(self):
        self.client = Client()

    def test_successful_registration_generates_code(self):
        """Registration should create User/Profile, generate a recovery code, and redirect to success page."""
        response = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'X9k$qLm2wP!z',
            'password_confirm': 'X9k$qLm2wP!z',
        })
        self.assertEqual(response.status_code, 302)  # redirect to success page

        # User and profile should be created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        profile = user.profile
        self.assertTrue(profile.email_verified)
        self.assertIsNotNone(profile.recovery_code_hash)
        
        # Plain recovery code should be stored in session as 'plain_recovery_code'
        self.assertIn('plain_recovery_code', self.client.session)
        plain_code = self.client.session['plain_recovery_code']
        self.assertTrue(verify_recovery_code(plain_code, profile.recovery_code_hash))

        # Check redirect after verifying session
        self.assertRedirects(response, '/register/success/')

    def test_success_page_displays_code_once(self):
        """Accessing the success page pops the code from session so it is only shown once."""
        # Set up a session with a recovery code
        session = self.client.session
        session['plain_recovery_code'] = 'PAI-TEST-CODE-1234'
        session.save()

        # First load should show the code
        response = self.client.get('/register/success/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'PAI-TEST-CODE-1234')

        # Code should be popped from session
        self.assertNotIn('plain_recovery_code', self.client.session)

        # Second load should redirect back (prevent double exposure)
        second_response = self.client.get('/register/success/')
        self.assertEqual(second_response.status_code, 302)


# ──────────────────────────────────────────────
# Integration Tests for Forgot Password Reset Flow
# ──────────────────────────────────────────────

class ForgotPasswordFlowTests(TestCase):
    """Integration tests for the single-page password recovery flow."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='OldPassword123!',
        )
        self.profile = self.user.profile
        self.plain_code = generate_recovery_code()
        self.profile.recovery_code_hash = hash_recovery_code(self.plain_code)
        self.profile.email_verified = True
        self.profile.save()

    def test_successful_password_reset(self):
        """Resetting password with valid code should update password and generate a new recovery code."""
        response = self.client.post('/forgot-password/', {
            'email': 'existing@example.com',
            'recovery_code': self.plain_code,
            'password': 'NewSecurePassword123!',
            'password_confirm': 'NewSecurePassword123!',
        })
        self.assertEqual(response.status_code, 302)

        # New code should be in session before the redirect is followed and pops it
        self.assertIn('new_recovery_code', self.client.session)
        new_code = self.client.session['new_recovery_code']

        # Assert redirection
        self.assertRedirects(response, '/forgot-password/reset-success/')

        # User's password should be updated
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecurePassword123!'))

        # Old recovery code should be invalidated, and a new one generated
        self.profile.refresh_from_db()
        self.assertFalse(verify_recovery_code(self.plain_code, self.profile.recovery_code_hash))
        self.assertTrue(verify_recovery_code(new_code, self.profile.recovery_code_hash))

    def test_failed_reset_on_incorrect_recovery_code(self):
        """An incorrect recovery code should return a professional validation error without disclosing what failed."""
        response = self.client.post('/forgot-password/', {
            'email': 'existing@example.com',
            'recovery_code': 'PAI-WRONG-CODE-0000',
            'password': 'NewSecurePassword123!',
            'password_confirm': 'NewSecurePassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email address or recovery code.')
        
        # Password should not be changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('OldPassword123!'))

    def test_failed_reset_on_nonexistent_email(self):
        """A nonexistent email should return the same error (preventing email enumeration)."""
        response = self.client.post('/forgot-password/', {
            'email': 'nonexistent@example.com',
            'recovery_code': self.plain_code,
            'password': 'NewSecurePassword123!',
            'password_confirm': 'NewSecurePassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid email address or recovery code.')


# ──────────────────────────────────────────────
# Unit Tests for Recovery Code Regeneration (Settings)
# ──────────────────────────────────────────────

class SettingsRegenerationTests(TestCase):
    """Tests for regenerating recovery codes inside account settings."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='settingsuser',
            email='settings@example.com',
            password='MyPassword123!',
        )
        self.profile = self.user.profile
        self.plain_code = generate_recovery_code()
        self.profile.recovery_code_hash = hash_recovery_code(self.plain_code)
        self.profile.save()
        self.client.force_login(self.user)

    def test_successful_regeneration_on_valid_password(self):
        """Regenerating recovery code with password confirmation should update the code and show it once."""
        response = self.client.post('/settings/', {
            'action': 'regenerate_recovery_code',
            'confirm_password': 'MyPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        
        # New code should be stored in session to display once
        self.assertIn('new_recovery_code_settings', self.client.session)
        new_code = self.client.session['new_recovery_code_settings']

        # New code should be generated
        self.profile.refresh_from_db()
        self.assertFalse(verify_recovery_code(self.plain_code, self.profile.recovery_code_hash))
        self.assertTrue(verify_recovery_code(new_code, self.profile.recovery_code_hash))

    def test_failed_regeneration_on_incorrect_password(self):
        """Regenerating recovery code with incorrect password should fail and keep the old code."""
        response = self.client.post('/settings/', {
            'action': 'regenerate_recovery_code',
            'confirm_password': 'WrongPassword123!',
        })
        self.assertEqual(response.status_code, 302)
        
        # Code should remain unchanged
        self.profile.refresh_from_db()
        self.assertTrue(verify_recovery_code(self.plain_code, self.profile.recovery_code_hash))
        self.assertNotIn('new_recovery_code_settings', self.client.session)
