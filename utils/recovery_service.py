import secrets
import string
from django.contrib.auth.hashers import make_password, check_password

def generate_recovery_code():
    """
    Generates a cryptographically secure, random, unique recovery code.
    Format: PAI-XXXX-XXXX-XXXX
    Uses alphanumeric characters (excluding confusing ones like I, O, 0, 1).
    """
    # Clean character pool to avoid readability mistakes for users
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    
    group1 = "".join(secrets.choice(alphabet) for _ in range(4))
    group2 = "".join(secrets.choice(alphabet) for _ in range(4))
    group3 = "".join(secrets.choice(alphabet) for _ in range(4))
    
    return f"PAI-{group1}-{group2}-{group3}"

def hash_recovery_code(plain_code):
    """
    Hashes a plain recovery code using Django's default secure password hashing.
    """
    return make_password(plain_code.strip().upper())

def verify_recovery_code(entered_code, hashed_code):
    """
    Verifies an entered recovery code against a stored hash using timing-safe comparison.
    """
    if not entered_code or not hashed_code:
        return False
    return check_password(entered_code.strip().upper(), hashed_code)
