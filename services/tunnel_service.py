import time
import requests
import logging

from config import Config
from services.webhook_service import WebhookService

class TunnelService:
    """Handles tunnel discovery and GitHub Webhook updates."""
    def __init__(self, config: Config):
        self.tunnel_service_url = f'http://{config.tunnel_service_name or "localhost"}:4040'
        self.current_tunnel_url = None
        
        self.webhookService = WebhookService(config)
        
        # Configure logging
        logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
        self.logger = logging.getLogger("TunnelService")

    def get_tunnel_url(self):
        """Fetch the current tunnle public URL."""
        try:
            response = requests.get(f'{self.tunnel_service_url}/api/tunnels').json()
            return response["tunnels"][0]["public_url"]
        except Exception as e:
            self.logger.error(f"Error fetching tunnel URL: {e}")
            return None

    def monitor_tunnel(self):
        """Continuously check for tunnel URL changes and update the GitHub Webhook."""
        time.sleep(10)  # wait for ngrok to start
        while True:
            new_url = self.get_tunnel_url()
            if new_url and new_url != self.current_tunnel_url:
                self.logger.info(f"🔄 tunnel URL changed: {new_url}")
                if self.webhookService.update_github_webhook(new_url):
                    self.current_tunnel_url = new_url
            time.sleep(30)  # Check every 30 seconds