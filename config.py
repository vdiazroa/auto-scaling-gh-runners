"""Format and type the env variables as a config var"""

import logging
import os
from dataclasses import dataclass
from typing import Optional, Tuple

from dotenv import load_dotenv

if os.path.exists(".env.local"):
    load_dotenv(dotenv_path=".env.local")
else:
    load_dotenv()

logger = logging.getLogger("Config")


def get_github_repo():
    """Format github_repo and github_org"""
    github_repos = os.getenv("GITHUB_REPO")
    github_orgs = os.getenv("GITHUB_ORG")

    if not github_repos and not github_orgs:
        raise ValueError("Please provide either GITHUB_REPO or GITHUB_ORG")

    all_repos = [
        f"{'orgs' if is_org else 'repos'}/{item.strip()}"
        for is_org, source in [(True, github_orgs), (False, github_repos)]
        if source for item in source.split(",")
    ]

    return all_repos


@dataclass
class Config:
    """Configuration class to store environment variables for the webhook server and runner."""
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
    github_repos: Tuple[str] = tuple(get_github_repo())

    ngrok_authtoken: Optional[str] = os.getenv("NGROK_AUTHTOKEN")
    ngrok_static_url: Optional[str] = os.getenv("NGROK_DOMAIN")

    server_port: int = int(os.getenv("SERVER_PORT", "5001"))
    should_create_webhook: bool = os.getenv("CREATE_WEBHOOK_If_NOT_EXIST", "false").lower() == "true"
    webhook_event: str = "workflow_job"
    # Runner-related settings
    docker_sock: str = "/var/run/docker.sock"
    runner_image: str = os.getenv("RUNNER_IMAGE", "gh-runner")
    docker: bool = os.getenv("DOCKER", "false").lower() == "true"
    node: bool = os.getenv("NODE", "true").lower() == "true"
    max_runners: int = int(os.getenv("MAX_RUNNERS", "10"))
    debug_runner: bool = os.getenv("DEBUG_RUNNER", "false").lower() == "true"


config = Config()
