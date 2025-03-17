import logging
import requests

from services.email_service import EmailService

class WebhookService:
    def __init__(self, email_service: EmailService, github_token, github_repo, github_org):
        if not github_org and not github_repo:
            print("Please provide either GITHUB_REPO or GITHUB_ORG env variable")
            
        self.github_api_url= f"https://api.github.com/repo/{self.github_repo}" if github_repo else f"https://api.github.com/orgs/{github_org}"
        self.github_token = github_token
        
        self.email_service = email_service
        self.logger = logging.getLogger("WebhookService")


    def get_github_webhook_id(self, tunnel_server="ngrok"):
        """Find the GitHub webhook ID."""
        headers = {"Authorization": f"token {self.github_token}", "Accept": "application/vnd.github.v3+json"}
        try:
            response = requests.get(f'{self.github_api_url}/hooks', headers=headers).json()
            for hook in response:
                if tunnel_server in hook["config"]["url"]:
                    return hook["id"]
        except Exception as e:
            self.logger.error(f"Error fetching GitHub webhook: {e}")
        return None

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
                    return True
                else:
                    self.logger.error(f"❌ Failed to update webhook: {response.text}")
            except Exception as e:
                self.logger.error(f"Error updating webhook: {e}")
        return False
    
    def github_api_url(self):
        return self.github_api_url
