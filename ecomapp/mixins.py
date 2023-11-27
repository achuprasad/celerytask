from django.core.mail import send_mail
from django.conf import settings

class EmailSendingMixin:
    def send_custom_mail(self, subject, message, sender, recipient):
        try:
            send_mail(
                subject,
                message,
                sender,
                [recipient],
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Log the exception or handle the error according to your needs
            return False
