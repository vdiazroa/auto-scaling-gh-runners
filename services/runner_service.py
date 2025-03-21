"""Service that builds GitHub runner images
and starts containers on demand"""
import re
import subprocess
import logging
import time

from config import Config


class RunnerService:
    """Handles GitHub self-hosted runner management."""

    def __init__(self, config: Config):
        self.github_repo = config.github_repo
        self.github_token = config.github_token

        self.runner_image = f"{config.runner_image}:latest"
        self.runner_name_prefix = re.sub(r"(repos/|orgs/)", "", self.github_repo).replace("/", "-")

        self.max_runners = config.max_runners
        self.min_runners = config.min_runners
        self.logger = logging.getLogger("RunnerService")
        self.docker = config.docker
        self.node = config.node

        # Ensure the runner image exists before starting
        self.build_runner_image()
        self.generate_min_q_containers()

    def generate_min_q_containers(self):
        """Ensure minimum number of GitHub runners exist"""
        while self.runners_quantity() < self.min_runners:
            self.create_runner()
            time.sleep(5)

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

    def create_runner(self):
        """Create a new GitHub Actions runner container."""
        if self.runners_quantity() >= self.max_runners:
            self.logger.info("🚀 Max runners reached. No new runner created.")
            return False

        try:
            # Run the container and get its ID securely
            runner_cmd = [
                "docker","run","-d","--privileged","-v","/var/run/docker.sock:/var/run/docker.sock",
                "-e",f"GITHUB_TOKEN={self.github_token}","-e",f"GITHUB_REPO={self.github_repo}",
                "-e",f"DOCKER={self.docker}",self.runner_image
            ]
            container_id = subprocess.check_output(runner_cmd).decode().strip()

            # Rename the container using the generated ID
            new_container_name = f"{self.runner_name_prefix}-{container_id[:12]}"
            subprocess.run(["docker", "rename", container_id, new_container_name], check=True)

            self.logger.info("✅ Created and renamed runner: %s", new_container_name)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error("❌ Error creating runner: %s", e)
            return False

    def remove_runner(self, runner_name):
        """Remove a GitHub Actions runner."""
        self.logger.info("🛑 Removing runner: %s", runner_name)
        try:
            subprocess.run(["docker", "stop", runner_name], check=True)
            subprocess.run(["docker", "rm", runner_name], check=True)
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error("❌ Error removing runner: %s", e)
            return False

    def runners_quantity(self):
        """List running GitHub runner containers."""
        try:
            output = subprocess.check_output(
                ["docker", "ps", "--filter", f"name={self.runner_name_prefix}*", "--format", "{{.Names}}"]
            ).decode().strip()
            return len(output.split("\n")) if output else 0
        except subprocess.CalledProcessError:
            return 0