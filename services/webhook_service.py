import logging
import requests

from config import Config
from services.email_service import EmailService

class WebhookService:
    def __init__(self, config: Config):
        github_repo = config.github_repo
        self.github_token = config.github_token
        # if using a persistent url for the tunnel server, set it here instead of "ngrok"
        self.tunnel_server = "ngrok"

        self.github_api_url= f"https://api.github.com/{github_repo}"
        self.email_service = EmailService(config)
        self.logger = logging.getLogger("WebhookService")


    def get_github_webhook_id(self):
        """Find the GitHub webhook ID."""
        headers = {"Authorization": f"token {self.github_token}", "Accept": "application/vnd.github.v3+json"}
        try:
            response = requests.get(f'{self.github_api_url}/hooks', headers=headers).json()
            for hook in response:
                if self.tunnel_server in hook["config"]["url"]:
                    return hook["id"]
        except Exception as e:
            self.logger.error(f"Error fetching GitHub webhook: {e}")
        return None
    
    ## this is needed with because we are using ngrok free tier, and the url changes every time we restart the server
    def update_github_webhook(self, new_url):
        """Update GitHub Webhook to use the latest server URL."""
        webhook_id = self.get_github_webhook_id()
        if webhook_id:
            headers = {"Authorization": f"token {self.github_token}", "Accept": "application/vnd.github.v3+json"}
            payload = {"config": {"url": f"{new_url}/webhook", "content_type": "json"}}
            try:
                response = requests.patch(f"{self.github_api_url}/hooks/{webhook_id}", headers=headers, json=payload)
                if response.status_code == 200:
                    self.logger.info(f"✅ Webhook updated: {new_url}")
                    self.send_email_alert(f"✅ GitHub Webhook updated successfully: {new_url}")
                    return True
                else:
                    self.logger.error(f"❌ Failed to update webhook: {response.text}")
                    self.send_email_alert(f"❌ Failed to update GitHub Webhook: {response.text}")
            except Exception as e:
                self.logger.error(f"Error updating webhook: {e}")
                self.send_email_alert(f"❌ Error updating GitHub Webhook: {e}")
        return False
    
    def github_api_url(self):
        return self.github_api_url
