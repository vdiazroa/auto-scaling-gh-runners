"""Use ngrok to make expose an url that can be used for the github Webhook"""
import time
import logging
from pyngrok import ngrok

from config import Config
from services.webhook_service import WebhookService

class TunnelService:
    """Handles tunnel discovery and GitHub Webhook updates."""
    def __init__(self, config: Config):
        self.current_tunnel_url = None
        ngrok.set_auth_token(config.ngrok_authtoken)
        self.listener = ngrok.connect(addr=config.server_port)
        self.webhook_service = WebhookService(config)

        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("TunnelService")

    def monitor_tunnel(self):
        """Continuously check for tunnel URL changes and update the GitHub Webhook."""
        time.sleep(10)  # wait for ngrok to start
        while True:
            new_url = self.listener.public_url
            if new_url and new_url != self.current_tunnel_url:
                self.logger.info("🔄 tunnel URL changed: %s", new_url)
                if self.webhook_service.update_github_webhook(new_url):
                    self.current_tunnel_url = new_url
            time.sleep(30)  # Check every 30 seconds

    def get_current_tunnel_url(self):
        """Exposee current tunnel url"""
        return self.current_tunnel_url
