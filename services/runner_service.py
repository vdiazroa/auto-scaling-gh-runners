import subprocess
import logging

from config import Config
class RunnerService:
    """Handles GitHub self-hosted runner management."""
    def __init__(self, config : Config):
        self.runner_image = f'{config.runner_image}:latest'
        self.runner_name_prefix = config.runner_image
        self.max_runners = config.max_runners
        self.github_token = config.github_token
        self.github_repo = config.github_repo

        self.logger = logging.getLogger("RunnerService")
        self.build_runner_image()  # Ensure the runner image exists before starting
        
    def image_exists(self):
        """Check if the runner Docker image exists."""
        try:
            output = subprocess.check_output(f"docker images -q {self.runner_image}", shell=True).decode().strip()
            return bool(output)
        except subprocess.CalledProcessError:
            return False

    def build_runner_image(self):
        """Build the GitHub Actions runner image if it does not exist."""
        if not self.image_exists():
            self.logger.info(f"⚙️ Runner image {self.runner_image} not found. Building...")
            build_cmd = f"docker build -f Dockerfile.gh-runners -t {self.runner_image} ."
            result = subprocess.run(build_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode == 0:
                self.logger.info(f"✅ Runner image {self.runner_image} built successfully.")
                return True
            else:
                self.logger.error(f"❌ Error building runner image: {result.stderr.decode()}")
                return False
        return True

    def create_runner(self):
        """Create a new GitHub Actions runner container."""
        running_runners = self.list_runners()
        if len(running_runners) >= self.max_runners:
            self.logger.info("🚀 Max runners reached. No new runner created.")
            return False

        runner_name = f"{self.runner_name_prefix}-{self.github_repo.replace("/","-")}-{len(running_runners) + 1}"
        self.logger.info(f"🚀 Creating new runner: {runner_name}")

        try:
            subprocess.run(
                f"docker run -d --name {runner_name} -e GITHUB_TOKEN={self.github_token} -e GITHUB_REPO={self.github_repo} {self.runner_image}",
                shell=True,
                check=True,
            )
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Error creating runner: {e}")
            return False

    def remove_runner(self, runner_name):
        """Remove a GitHub Actions runner."""
        self.logger.info(f"🛑 Removing runner: {runner_name}")
        try:
            subprocess.run(f"docker stop {runner_name} && docker rm {runner_name}", shell=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Error removing runner: {e}")
            return False

    def list_runners(self):
        """List running GitHub runner containers."""
        try:
            output = subprocess.check_output(f"docker ps --filter 'name={self.runner_name_prefix}*' --format '{{{{.Names}}}}'", shell=True).decode().strip()
            return output.split("\n") if output else []
        except subprocess.CalledProcessError:
            return []