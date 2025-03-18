
from flask import Flask, request, jsonify
import logging
from threading import Thread

from services.runner_service import RunnerService
from config import config

## Start Services 
runner_service = RunnerService(config)

def tunnel_url(): None

if config.ngrok_authtoken:
    from services.tunnel_service import TunnelService
    tunnel_service = TunnelService(config)
    Thread(target=tunnel_service.monitor_tunnel).start()  # Monitor tunnel in the background
    def tunnel_url(): 
        return tunnel_service.current_tunnel_url

logger = logging.getLogger("WebhookServer")

## Stat Server
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handles incoming GitHub Webhook events."""
    payload = request.json
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    logger.info(f"📩 Received GitHub Webhook: {event_type}")

    if event_type == "ping":
        ## for debugging
        runner_service.create_runner()
        return jsonify({"message": "Webhook received!"}), 200
    
    if event_type != "workflow_job":
        return jsonify({"message": "Webhook received! no action needed"}), 200

    action = payload.get("action")
    
    if action == "queued":
        logger.info(f"🚀 New job detected! Checking for available runners...")
        runner_service.create_runner()
        
    elif action == "completed":
        logger.info(f"🛑 Job completed. Cleaning up runners...")
        runner_service.remove_runner(payload["workflow_job"]["runner_name"])

    return jsonify({"message": "Webhook processed"}), 200

@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    """Health check for the server, tunnel, and runner image."""
    return jsonify({
        "tunnel_url": tunnel_url(),
        "runner_image_exists": runner_service.image_exists(),
        "running_runners": runner_service.list_runners(),
    }), 200
        
app.run(host="0.0.0.0", port=config.server_port)  # Start the server