import time
from unittest.mock import patch
from datetime import timedelta

from django.test import TestCase, Client
from django.utils import timezone
from django.contrib.auth.models import User

from accounts.models import Profile, EmailOTP
from utils.email_otp_service import generate_otp, send_otp_email, verify_otp, delete_expired_otps


# ──────────────────────────────────────────────
# Unit Tests for utils/email_otp_service.py
# ──────────────────────────────────────────────

class GenerateOTPTests(TestCase):
    """Tests for the generate_otp() utility function."""

    def test_returns_six_digit_string(self):
        code = generate_otp()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_unique_codes(self):
        """Two consecutive calls should (almost certainly) produce different codes."""
        codes = {generate_otp() for _ in range(20)}
        self.assertGreater(len(codes), 1)


class SendOTPEmailTests(TestCase):
    """Tests for send_otp_email() – DB record creation + email dispatch."""

    @patch('utils.email_otp_service.send_mail')
    def test_creates_db_record_and_sends_email(self, mock_send_mail):
        email = "user@example.com"
        code = "123456"
        result = send_otp_email(email, code, purpose='registration')

        self.assertTrue(result)
        mock_send_mail.assert_called_once()

        # Verify DB record
        otp = EmailOTP.objects.get(email=email, purpose='registration')
        self.assertEqual(otp.otp_code, code)
        self.assertEqual(otp.attempts, 0)
        self.assertGreater(otp.expires_at, timezone.now())

    @patch('utils.email_otp_service.send_mail')
    def test_replaces_previous_otp_for_same_email_and_purpose(self, mock_send_mail):
        email = "user@example.com"
        send_otp_email(email, "111111", purpose='registration')
        send_otp_email(email, "222222", purpose='registration')

        self.assertEqual(EmailOTP.objects.filter(email=email, purpose='registration').count(), 1)
        otp = EmailOTP.objects.get(email=email, purpose='registration')
        self.assertEqual(otp.otp_code, "222222")

    @patch('utils.email_otp_service.send_mail')
    def test_different_purposes_kept_separate(self, mock_send_mail):
        email = "user@example.com"
        send_otp_email(email, "111111", purpose='registration')
        send_otp_email(email, "222222", purpose='password_reset')

        self.assertEqual(EmailOTP.objects.filter(email=email).count(), 2)

    @patch('utils.email_otp_service.send_mail', side_effect=Exception("SMTP down"))
    def test_returns_false_on_send_failure(self, mock_send_mail):
        result = send_otp_email("user@example.com", "123456")
        self.assertFalse(result)
        # DB record should still exist even if send fails
        self.assertEqual(EmailOTP.objects.filter(email="user@example.com").count(), 1)


class VerifyOTPTests(TestCase):
    """Tests for verify_otp() – success, wrong code, expiry, rate limiting."""

    def _create_otp(self, email="user@example.com", code="123456",
                    purpose='registration', minutes=5, attempts=0):
        return EmailOTP.objects.create(
            email=email,
            otp_code=code,
            expires_at=timezone.now() + timedelta(minutes=minutes),
            attempts=attempts,
            purpose=purpose,
        )

    def test_success(self):
        self._create_otp()
        is_valid, msg = verify_otp("user@example.com", "123456", purpose='registration')
        self.assertTrue(is_valid)
        self.assertIn("successfully", msg.lower())
        # OTP record must be deleted after successful verification
        self.assertFalse(EmailOTP.objects.filter(email="user@example.com", purpose='registration').exists())

    def test_incorrect_code(self):
        self._create_otp()
        is_valid, msg = verify_otp("user@example.com", "000000", purpose='registration')
        self.assertFalse(is_valid)
        self.assertIn("Incorrect", msg)
        # Record still exists with incremented attempts
        otp = EmailOTP.objects.get(email="user@example.com", purpose='registration')
        self.assertEqual(otp.attempts, 1)

    def test_expired_otp(self):
        self._create_otp(minutes=-1)  # Already expired
        is_valid, msg = verify_otp("user@example.com", "123456", purpose='registration')
        self.assertFalse(is_valid)
        # Expired OTPs are cleaned up, so either "expired" or "no active" message
        self.assertTrue("expired" in msg.lower() or "no active" in msg.lower())

    def test_rate_limit_after_five_attempts(self):
        self._create_otp(attempts=4)
        # 5th attempt with wrong code
        is_valid, msg = verify_otp("user@example.com", "000000", purpose='registration')
        self.assertFalse(is_valid)
        self.assertIn("Too many", msg)
        # OTP record should be deleted
        self.assertFalse(EmailOTP.objects.filter(email="user@example.com", purpose='registration').exists())

    def test_no_otp_found(self):
        is_valid, msg = verify_otp("nobody@example.com", "123456")
        self.assertFalse(is_valid)
        self.assertIn("No active", msg)

    def test_wrong_purpose(self):
        self._create_otp(purpose='registration')
        is_valid, msg = verify_otp("user@example.com", "123456", purpose='password_reset')
        self.assertFalse(is_valid)
        self.assertIn("No active", msg)


class DeleteExpiredOTPsTests(TestCase):
    """Tests for delete_expired_otps() cleanup utility."""

    def test_deletes_only_expired(self):
        # Active OTP
        EmailOTP.objects.create(
            email="active@example.com", otp_code="111111",
            expires_at=timezone.now() + timedelta(minutes=5), purpose='registration',
        )
        # Expired OTP
        EmailOTP.objects.create(
            email="expired@example.com", otp_code="222222",
            expires_at=timezone.now() - timedelta(minutes=1), purpose='registration',
        )
        delete_expired_otps()
        self.assertTrue(EmailOTP.objects.filter(email="active@example.com").exists())
        self.assertFalse(EmailOTP.objects.filter(email="expired@example.com").exists())


# ──────────────────────────────────────────────
# Integration Tests for Registration + Verify Flow
# ──────────────────────────────────────────────

class RegistrationFlowTests(TestCase):
    """End-to-end test: register → send OTP → verify → user created."""

    def setUp(self):
        self.client = Client()

    @patch('utils.email_otp_service.send_mail')
    def test_full_registration_flow(self, mock_send_mail):
        # Step 1 – POST the registration form
        resp = self.client.post('/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'X9k$qLm2wP!z',
            'password_confirm': 'X9k$qLm2wP!z',
        })
        self.assertEqual(resp.status_code, 302)  # redirect to verify page
        mock_send_mail.assert_called_once()

        # OTP should be in the DB
        otp = EmailOTP.objects.get(email='newuser@example.com', purpose='registration')
        code = otp.otp_code

        # Step 2 – Verify OTP
        resp = self.client.post('/register/verify/', {
            'otp': code,
        })
        self.assertEqual(resp.status_code, 302)  # redirect to login

        # User should now exist
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')

        # Profile should be email_verified
        profile = Profile.objects.get(user=user)
        self.assertTrue(profile.email_verified)

    @patch('utils.email_otp_service.send_mail')
    def test_registration_resend_otp(self, mock_send_mail):
        # Register first
        self.client.post('/register/', {
            'username': 'resenduser',
            'email': 'resend@example.com',
            'password': 'R7m!nPq3xZ$v',
            'password_confirm': 'R7m!nPq3xZ$v',
        })
        self.assertEqual(mock_send_mail.call_count, 1)

        # Hit resend
        resp = self.client.post('/register/verify/', {
            'action': 'resend',
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(mock_send_mail.call_count, 2)

    @patch('utils.email_otp_service.send_mail')
    def test_wrong_otp_shows_error(self, mock_send_mail):
        self.client.post('/register/', {
            'username': 'wrongotp',
            'email': 'wrong@example.com',
            'password': 'J4w@hKe9sM#b',
            'password_confirm': 'J4w@hKe9sM#b',
        })
        resp = self.client.post('/register/verify/', {
            'otp': '000000',
        })
        self.assertEqual(resp.status_code, 200)  # stays on the page
        self.assertFalse(User.objects.filter(username='wrongotp').exists())


# ──────────────────────────────────────────────
# Integration Tests for Forgot Password + Reset Flow
# ──────────────────────────────────────────────

class ForgotPasswordFlowTests(TestCase):
    """End-to-end test: forgot password → OTP verify → reset password."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='OldP@ss1k3x!',
        )
        profile, _ = Profile.objects.get_or_create(user=self.user)
        profile.email_verified = True
        profile.save()

    @patch('utils.email_otp_service.send_mail')
    def test_full_reset_flow(self, mock_send_mail):
        # Step 1 – Submit email on forgot-password
        resp = self.client.post('/forgot-password/', {
            'email': 'existing@example.com',
        })
        self.assertEqual(resp.status_code, 302)
        mock_send_mail.assert_called_once()

        otp = EmailOTP.objects.get(email='existing@example.com', purpose='password_reset')
        code = otp.otp_code

        # Step 2 – Verify OTP
        resp = self.client.post('/forgot-password/verify/', {
            'otp': code,
        })
        self.assertEqual(resp.status_code, 302)  # redirect to reset page

        # Step 3 – Set new password
        resp = self.client.post('/forgot-password/reset/', {
            'password': 'N3w$tR0ng!zXq',
            'password_confirm': 'N3w$tR0ng!zXq',
        })
        self.assertEqual(resp.status_code, 302)  # redirect to login

        # Verify user can login with new password
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('N3w$tR0ng!zXq'))

    @patch('utils.email_otp_service.send_mail')
    def test_unregistered_email_shows_error(self, mock_send_mail):
        resp = self.client.post('/forgot-password/', {
            'email': 'nonexistent@example.com',
        })
        self.assertEqual(resp.status_code, 200)  # stays on page
        mock_send_mail.assert_not_called()

    def test_reset_password_without_otp_verification_redirects(self):
        """Directly hitting reset-password without OTP should be blocked."""
        resp = self.client.get('/forgot-password/reset/')
        self.assertEqual(resp.status_code, 302)  # redirect to forgot_password


# ──────────────────────────────────────────────
# Unit Tests for Badge System & Settings Views
# ──────────────────────────────────────────────

from accounts.models import Badge, UserBadge
from utils.badge_service import assign_badges, initialize_badge_definitions

class BadgeAndSettingsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='teststudent',
            email='teststudent@example.com',
            password='Password123!',
        )
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        
    def test_initialize_badge_definitions(self):
        badges_map = initialize_badge_definitions()
        self.assertIn('✓ Verified Email', badges_map)
        self.assertIn('GitHub Explorer', badges_map)
        self.assertEqual(Badge.objects.count(), 31)

    def test_assign_badges_verified_email(self):
        initialize_badge_definitions()
        self.profile.email_verified = True
        self.profile.save()
        
        assign_badges(self.user)
        
        # Should have received verified email badge
        self.assertTrue(UserBadge.objects.filter(user=self.user, badge__name='✓ Verified Email').exists())
        self.assertTrue(self.profile.badges.filter(name='✓ Verified Email').exists())

    def test_settings_view_requires_login(self):
        resp = self.client.get('/settings/')
        self.assertEqual(resp.status_code, 302)

    def test_achievements_view_requires_login(self):
        resp = self.client.get('/achievements/')
        self.assertEqual(resp.status_code, 302)

    def test_settings_view_authenticated(self):
        self.client.force_login(self.user)
        resp = self.client.get('/settings/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'accounts/settings.html')

    def test_achievements_view_authenticated(self):
        self.client.force_login(self.user)
        resp = self.client.get('/achievements/')
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'accounts/achievements.html')
