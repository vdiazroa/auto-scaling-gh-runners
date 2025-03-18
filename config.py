from dataclasses import dataclass
from dotenv import load_dotenv
from typing import Optional
import os

if os.path.exists(".env.local"):
    load_dotenv(dotenv_path=".env.local")
else:
    load_dotenv()
    
@dataclass
class Config:
    smtp_server: Optional[str] = os.getenv("SMTP_SERVER")
    smtp_port: int = int(os.getenv("SMTP_PORT") or "587") 
    smtp_username: Optional[str] = os.getenv("SMTP_USERNAME")
    smtp_password: Optional[str] = os.getenv("SMTP_PASSWORD")
    alert_emails: Optional[str] = os.getenv("ALERT_EMAILS")
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
    github_repo: str = os.getenv("GITHUB_REPO") or ""
    github_org: str = os.getenv("GITHUB_ORG") or ""
    runner_image: str = os.getenv("RUNNER_IMAGE") or "github-runner"
    runner_name_prefix: Optional[str] = os.getenv("RUNNER_NAME_PREFIX")
    max_runners: int = int(os.getenv("MAX_RUNNERS") or "10")
    tunnel_service_name: Optional[str] = os.getenv("TUNNEL_SERVICE_NAME")

config = Config()