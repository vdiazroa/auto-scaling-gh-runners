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
    
    if not github_repo and not github_org:   
        raise Exception("Please provide either GITHUB_REPO, GITHUB_ORG, or both env variable")
    
    github_rel_url = f'{github_org}/' if github_org else '/'
    github_rel_url = f'repos/{github_rel_url}{github_repo}/' if github_repo else f'orgs/{github_rel_url}'
    logger.info(f"Github repo url: {github_rel_url}")
    
    return github_rel_url[:-1]
    
@dataclass
class Config:
    smtp_server: Optional[str] = os.getenv("SMTP_SERVER")
    smtp_port: int = int(os.getenv("SMTP_PORT") or "587") 
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    alert_emails: Optional[str] = os.getenv("ALERT_EMAILS")
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
    github_repo: str = get_github_repo()
    runner_image: str = os.getenv("RUNNER_IMAGE") or "github-runner"
    runner_name_prefix: Optional[str] = os.getenv("RUNNER_NAME_PREFIX")
    max_runners: int = int(os.getenv("MAX_RUNNERS") or "10")
    tunnel_service_name: Optional[str] = os.getenv("TUNNEL_SERVICE_NAME")
    
config = Config() 
