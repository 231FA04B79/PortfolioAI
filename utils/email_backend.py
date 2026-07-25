import ssl
from django.core.mail.backends.smtp import EmailBackend

class SSLCertBypassEmailBackend(EmailBackend):
    """
    Custom SMTP email backend that bypasses SSL certificate verification.
    This is useful in local/development environments where system certificates
    are not trusted, or when the connection is routed through an SSL-intercepting proxy.
    """
    @property
    def ssl_context(self):
        context = ssl._create_unverified_context()
        return context
