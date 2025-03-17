import smtplib
import logging
from email.message import EmailMessage

class EmailService:
    """Handles sending email alerts."""

    def __init__(self, smtp_server, smtp_port, smtp_username, smtp_password, alert_emails):
        self.smtp_server = smtp_server
        self.smtp_port = int(smtp_port or "10")
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.alert_emails = alert_emails
        self.logger = logging.getLogger("EmailService")
        self.start_server()
    
    def start_server(self):
        """Start the email server."""
        if not self.smtp_username or not self.smtp_password or not self.alert_emails:
            self.logger.warning("❌ Email service not configured. Skipping alert.")
            return

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as self.server:
            self.server.starttls()
            self.server.login(self.smtp_username, self.smtp_password)
            
        self.logger.info("📧 Email server started")

    def send_email(self, subject, message):
        """Send an email alert."""
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = self.smtp_username
            msg["To"] = self.alert_emails
            msg.set_content(message)
            self.server.send_message(msg)

            self.logger.info(f"📧 Email alert sent to {', '.join(self.alert_emails)}: {message}")
        except Exception as e:
            self.logger.error(f"⚠️ Failed to send email: {e}")