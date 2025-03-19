"""WebServer that handles the github webhook,
it creates github runner after a workflow run has started"""

import logging
from threading import Thread

from flask import Flask, jsonify, request
from waitress import serve

from config import config
from services.runner_service import RunnerService

## Start Services
runner_service = RunnerService(config)

def _tunnel_url() -> (str | None):
    return

get_tunnel_url = _tunnel_url

if config.ngrok_authtoken:
    from services.tunnel_service import TunnelService

    tunnel_service = TunnelService(config)
    Thread(target=tunnel_service.monitor_tunnel).start()  # Monitor tunnel in the background

    get_tunnel_url = tunnel_service.get_current_tunnel_url()


logger = logging.getLogger("WebhookServer")

## Stat Server
app = Flask(__name__)


@app.route("/webhook", methods=["POST"])
def webhook():
    """Handles incoming GitHub Webhook events."""
    payload = request.json
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    logger.info("📩 Received GitHub Webhook: %s", event_type)

    if event_type == "ping":
        ## for debugging
        runner_service.create_runner()
        return jsonify({"message": "Webhook received!"}), 200

    if event_type != "workflow_job":
        return jsonify({"message": "Webhook received! no action needed"}), 200

    action = payload.get("action")

    if action == "queued":
        logger.info("🚀 New job detected! Checking for available runners...")
        runner_service.create_runner()

    elif action == "completed":
        logger.info("🛑 Job completed. Cleaning up runners...")
        runner_service.remove_runner(payload["workflow_job"]["runner_name"])

    return jsonify({"message": "Webhook processed"}), 200


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    """Health check for the server, tunnel, and runner image."""
    return (
        jsonify({
                "tunnel_url": get_tunnel_url(),
                "runner_image_exists": runner_service.image_exists(),
                "running_runners": runner_service.list_runners(),
        }),
        200
    )


serve(app, host="0.0.0.0", port=config.server_port)  # Start the server
