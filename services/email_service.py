import smtplib
import logging

from config import Config
from email.message import EmailMessage

class EmailService:
    """Handles sending email alerts."""

    def __init__(self, config: Config):
        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port
        self.smtp_username = config.smtp_username
        self.smtp_password = config.smtp_password
        self.alert_emails = config.alert_emails
        self.server: smtplib.SMTP | None = None
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

    def send_email_alert(self, message):
        """Send an email alert."""
        if not self.server:
            return
        try:
            msg = EmailMessage()
            msg["Subject"] = "GitHub Webhook & Runner Alert"
            msg["From"] = self.smtp_username
            msg["To"] = self.alert_emails
            msg.set_content(message)
            self.server.send_message(msg)

            self.logger.info(f"📧 Email alert sent to {', '.join(self.alert_emails)}: {message}")
        except Exception as e:
            self.logger.error(f"⚠️ Failed to send email: {e}")