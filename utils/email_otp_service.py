import random
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from accounts.models import EmailOTP

import os
import requests
import json

def generate_otp():
    """Generates a cryptographically-random-like 6-digit OTP code."""
    return f"{random.randint(100000, 999999)}"

def send_otp_email(email, otp_code, purpose='registration'):
    """
    Sends the 6-digit OTP code to the entered email with a professional template.
    """
    subject = "PortfolioAI Verification Code"
    
    # Matching the requested example formatting exactly:
    message = (
        f"Hello User,\n\n"
        f"Your verification code is:\n"
        f"{otp_code}\n\n"
        f"This code expires in 5 minutes.\n\n"
        f"PortfolioAI Team"
    )
    
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost')
    
    # Store OTP in the database
    # Delete any previous active OTPs for this email and purpose to prevent duplicate/multiple active codes
    EmailOTP.objects.filter(email=email, purpose=purpose).delete()
    
    # Create new database OTP entry
    expires_at = timezone.now() + timedelta(minutes=5)
    EmailOTP.objects.create(
        email=email,
        otp_code=otp_code,
        expires_at=expires_at,
        purpose=purpose
    )
    
    resend_api_key = os.environ.get('RESEND_API_KEY')
    brevo_api_key = os.environ.get('BREVO_API_KEY')
    
    # 1. Send via Brevo if API key is provided
    if brevo_api_key:
        url = "https://api.brevo.com/v3/smtp/email"
        headers = {
            "api-key": brevo_api_key,
            "Content-Type": "application/json"
        }
        sender_email = from_email if '@' in from_email and not from_email.endswith('localhost') else 'hemanthkurapati097@gmail.com'
        payload = {
            "sender": {"name": "PortfolioAI", "email": sender_email},
            "to": [{"email": email}],
            "subject": subject,
            "textContent": message
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code in [200, 201]:
                return True
            else:
                print(f" [BREVO API EXCEPTION] Failed to send email: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f" [BREVO API EXCEPTION] Failed to send email to {email}: {e}")
            return False
            
    # 2. Send via Resend if API key is provided
    elif resend_api_key:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json"
        }
        from_email_resend = from_email if '@' in from_email and not from_email.endswith('localhost') else 'onboarding@resend.dev'
        if 'onboarding@resend.dev' in from_email_resend:
            from_email_resend = "PortfolioAI <onboarding@resend.dev>"
            
        payload = {
            "from": from_email_resend,
            "to": [email],
            "subject": subject,
            "text": message
        }
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            if response.status_code in [200, 201]:
                return True
            else:
                print(f" [RESEND API EXCEPTION] Failed to send email: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f" [RESEND API EXCEPTION] Failed to send email to {email}: {e}")
            return False
            
    # 3. Fallback to standard Django send_mail (SMTP)
    else:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[email],
                fail_silently=False
            )
            return True
        except Exception as e:
            print(f" [EMAIL SERVICE EXCEPTION] Failed to send email to {email}: {e}")
            return False

def delete_expired_otps():
    """Deletes all expired OTPs from the database."""
    EmailOTP.objects.filter(expires_at__lt=timezone.now()).delete()

def verify_otp(email, entered_code, purpose='registration'):
    """
    Verifies the user entered OTP code from the database.
    Rate limiting: max 5 attempts.
    One-Time Use: deletes OTP from database upon success.
    """
    delete_expired_otps()
    
    # Fetch the latest active OTP for this email and purpose
    otp = EmailOTP.objects.filter(email=email, purpose=purpose).order_by('-created_at').first()
    
    if not otp:
        return False, "No active verification code found. Please request a new one."
        
    if timezone.now() > otp.expires_at:
        otp.delete()
        return False, "The OTP code has expired. Please request a new one."
        
    if otp.attempts >= 5:
        otp.delete()
        return False, "Too many incorrect attempts. This OTP code has been invalidated. Please request a new one."
        
    # Increment attempts
    otp.attempts += 1
    otp.save()
    
    if otp.otp_code != entered_code:
        remaining = 5 - otp.attempts
        if remaining <= 0:
            otp.delete()
            return False, "Too many incorrect attempts. This OTP code has been invalidated. Please request a new one."
        return False, f"Incorrect verification code. Attempts remaining: {remaining}"
        
    # Success - Delete OTP immediately to enforce One-Time Use
    otp.delete()
    return True, "OTP verified successfully."
