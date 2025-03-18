import time
import logging
import ngrok

from config import Config
from services.webhook_service import WebhookService

class TunnelService:
    """Handles tunnel discovery and GitHub Webhook updates."""
    def __init__(self, config: Config):
        self.current_tunnel_url = None
        self.listener = ngrok.forward(config.server_port, authtoken_from_env=True)
        self.webhookService = WebhookService(config)
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("TunnelService")

    def monitor_tunnel(self):
        """Continuously check for tunnel URL changes and update the GitHub Webhook."""
        time.sleep(10)  # wait for ngrok to start
        while True:
            new_url = self.listener.url()
            if new_url and new_url != self.current_tunnel_url:
                self.logger.info(f"🔄 tunnel URL changed: {new_url}")
                if self.webhookService.update_github_webhook(new_url):
                    self.current_tunnel_url = new_url
            time.sleep(30)  # Check every 30 seconds
    
    def get_current_tunnel_url(self):
        return self.current_tunnel_url