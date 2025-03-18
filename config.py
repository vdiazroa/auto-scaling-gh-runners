from dataclasses import dataclass
import logging
from dotenv import load_dotenv
from typing import Optional
import os

if os.path.exists(".env.local"):
    load_dotenv(dotenv_path=".env.local")
else:
    load_dotenv()
    
logger = logging.getLogger("Config")

def get_github_repo():
    github_repo = os.getenv("GITHUB_REPO")
    github_org = os.getenv("GITHUB_ORG")
    
    ## needs to be provided github_repo or github_org, but no both
    if (not github_repo and not github_org):   
        raise Exception("Please provide either GITHUB_REPO or GITHUB_ORG")
    if github_repo and github_org:   
        raise Exception("Please provide either GITHUB_REPO or GITHUB_ORG, not both")
    
    github_rel_url = github_repo if github_repo else github_org
    logger.info(f"Github repo url: {github_rel_url}")
    
    return github_rel_url
    
@dataclass
class Config:
    smtp_server: Optional[str] = os.getenv("SMTP_SERVER")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587")) 
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    alert_emails: Optional[str] = os.getenv("ALERT_EMAILS")
    
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
    github_repo: str = get_github_repo()
    
    server_port: int = int(os.getenv("SERVER_PORT", "5001"))
    
    runner_image: str = os.getenv("RUNNER_IMAGE", "gh-runner")
    min_runners: int = int(os.getenv("MIN_RUNNERS", "1"))
    max_runners: int = int(os.getenv("MAX_RUNNERS", "10"))
    
    ngrok_authtoken: str = os.getenv("NGROK_AUTHTOKEN")
    
    should_create_webhook: bool = os.getenv("CREATE_WEBHOOK_If_NOT_EXIST", "false").lower() == "true"
    webhook_events: tuple[str] = tuple(event.strip() for event in os.getenv("WORKFLOW_EVENTS_NEW_WEBHOOK", "workflow_run").split(","))
    
config = Config() 
