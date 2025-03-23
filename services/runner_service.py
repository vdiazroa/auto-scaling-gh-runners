"""Service that builds GitHub runner images
and starts containers on demand"""
import re
import subprocess
import logging

from config import Config


class RunnerService:
    """Handles GitHub self-hosted runner management."""

    def __init__(self, config: Config):
        self.github_token = config.github_token
        self.runner_image = f"{config.runner_image}:latest"
        self.max_runners = config.max_runners
        self.logger = logging.getLogger("RunnerService")
        self.docker = str(config.docker).lower()
        self.node = str(config.node).lower()

        # Ensure the runner image exists before starting
        self.build_runner_image()

    def get_runner_name_prefix(self, github_repo: str):
        """get runner name prefix"""
        return re.sub(r"(repos/|orgs/)", "", github_repo).replace("/", "-")

    def image_exists(self):
        """Check if the runner Docker image exists."""
        try:
            output = subprocess.check_output(["docker", "images", "-q", self.runner_image]).decode().strip()
            return bool(output)
        except subprocess.CalledProcessError:
            return False

    def build_runner_image(self):
        """Build the GitHub Actions runner image if it does not exist."""
        if not self.image_exists():
            self.logger.info("⚙️ Runner image %s not found. Building...", self.runner_image)
            try:
                build_cmd = [
                    "docker","build","-f","Dockerfile.gh-runners",
                    "--build-arg",f"DOCKER={self.docker}",
                    "--build-arg",f"NODE={self.node}",
                    "--build-arg", "DOCKER_GID=$(getent group docker | cut -d: -f3)",
                    "-t",self.runner_image,"."
                ]
                subprocess.run(build_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                self.logger.info("✅ Runner image %s built successfully.", self.runner_image)
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error("❌ Error building runner image: %s", e.stderr.decode())
                return False
        return True

    def create_runner(self, github_repo: str):
        """Create a new GitHub Actions runner container."""
        runner_name_prefix = self.get_runner_name_prefix(github_repo)
        
        if self.runners_quantity(runner_name_prefix) >= self.max_runners:
            self.logger.info("🚀 Max runners reached. No new runner created.")
            return False

        try:
            # Run the container and get its ID securely
            runner_cmd = [
                "docker","run","-d","--privileged","-v","/var/run/docker.sock:/var/run/docker.sock",
                "-e",f"GITHUB_TOKEN={self.github_token}","-e",f"GITHUB_REPO={github_repo}",
                "-e",f"DOCKER={self.docker}",self.runner_image
            ]
            container_id = subprocess.check_output(runner_cmd).decode().strip()

            # Rename the container using the generated ID
            new_container_name = f"{runner_name_prefix}-{container_id[:12]}"
            subprocess.run(["docker", "rename", container_id, new_container_name], check=True)

            self.logger.info("✅ Created and renamed runner: %s", new_container_name)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error("❌ Error creating runner: %s", e)
            return False

    def remove_runner(self, runner_name: str):
        """Remove a GitHub Actions runner."""
        self.logger.info("🛑 Removing runner: %s", runner_name)
        try:
            subprocess.run(["docker", "stop", runner_name], check=True)
            subprocess.run(["docker", "rm", runner_name], check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error("❌ Error removing runner: %s", e)
            return False

    def runners_quantity(self, github_repo: str):
        """List running GitHub runner containers."""
        runner_name_prefix = self.get_runner_name_prefix(github_repo)
        try:
            output = subprocess.check_output(
                ["docker", "ps", "--filter", f"name={runner_name_prefix}*", "--format", "{{.Names}}"]
            ).decode().strip()
            return len(output.split("\n")) if output else 0
        except subprocess.CalledProcessError:
            return 0