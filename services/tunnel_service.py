"""Use ngrok to make expose an url that can be used for the github Webhook"""

import time
import logging
from pyngrok import ngrok

from config import Config
from services.webhook_service import WebhookService


class TunnelService:
    """Handles tunnel discovery and GitHub Webhook updates."""

    def __init__(self, config: Config):
        self.current_tunnel_urls: dict[str:str] = {}
        self.ngrok_url = config.ngrok_url
        ngrok.set_auth_token(config.ngrok_authtoken)
        self.listener = ngrok.connect(addr=config.server_port, hostname=self.ngrok_url)
        self.webhook_service = WebhookService(config)
        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("TunnelService")

    def start_tunnel_in_repo(self, repo: str):
        """Create or update webhook with the tunnel url."""
        hook_github_api_base_url = f"https://api.github.com/{repo}"
        if self.ngrok_url:
            webhook_id = self.webhook_service.get_github_webhook_id(hook_github_api_base_url)
            if not webhook_id:
                return self.webhook_service.create_webhook(self.ngrok_url, hook_github_api_base_url)
            return
        new_url = self.listener.public_url
        self.logger.info("🔄 tunnel URL changed: %s", new_url)
        if self.webhook_service.update_github_webhook(new_url, hook_github_api_base_url):
            self.current_tunnel_urls[repo] = new_url

    def monitor_tunnel(self, repos: list[str]):
        """For every repo or org start the monitoring."""
        while not self.listener.public_url:  # wait for ngrok to start
            time.sleep(1)
        for repo in repos:
            self.current_tunnel_urls.setdefault(repo, "")
            if self.listener.public_url == self.current_tunnel_urls[repo]:
                continue
            self.start_tunnel_in_repo(repo)
        time.sleep(30)  # Check every 30 seconds
        self.monitor_tunnel(repos)

    def get_current_tunnel_url(self):
        """Exposee current tunnel url"""
        return self.current_tunnel_urls
