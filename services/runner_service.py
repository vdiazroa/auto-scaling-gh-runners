"""Service that builds GitHub runner images
and starts containers on demand"""
import platform
import re
import subprocess
import logging

from __init__ import __version__ as version
from config import Config

class RunnerService:
    """Handles GitHub self-hosted runner management."""

    def __init__(self, config: Config):
        self.github_token = config.github_token
        self.docker_sock = config.docker_sock
        self.runner_image = f"{config.runner_image}:{version}{'_docker' if config.docker else ''}{'_node' if config.node else ''}"
        self.max_runners = config.max_runners
        self.logger = logging.getLogger("RunnerService")
        self.docker = config.docker
        self.node = config.node
        self.debug_runner = config.debug_runner

        # Ensure the runner image exists before starting
        self.build_runner_image()
        if config.debug_runner:
            self.create_runner(config.github_repos[0])

    def get_runner_name_prefix(self, github_repo: str):
        """get runner name prefix"""
        return re.sub(r"(repos/|orgs/)", "", github_repo).replace("/", "-")

    def image_exists(self):
        """Check if the runner Docker image exists."""
        try:
            output = subprocess.check_output(["docker", "images", "-q", self.runner_image]).decode().strip()
            does_image_exists = bool(output)
            if self.debug_runner:
                self.logger.info('Image: %s does %sexist', self.runner_image, "" if does_image_exists else "not ")
            return does_image_exists
        except subprocess.CalledProcessError:
            return False

    def get_docker_gid(self, default_gid=1000):
        """Get docker group"""
        try:
            return subprocess.check_output([
                "stat", "-f" if platform.system() == "Darwin" else "-c", "%g", self.docker_sock
            ]).decode().strip()
        except subprocess.CalledProcessError:
            print("⚠️ Could not get Docker GID. Default value")
            return str(default_gid)

    def build_runner_image(self):
        """Build the GitHub Actions runner image if it does not exist."""
        if self.image_exists():
            return
        self.logger.info("⚙️ Runner image %s not found. Building...", self.runner_image)
        try:
            build_cmd = [
                "docker","build","-f","Dockerfile.gh-runners",
                "--build-arg",f"DOCKER={str(self.docker).lower()}",
                "--build-arg",f"NODE={str(self.node).lower()}",
                "--build-arg", f"DOCKER_GID={self.get_docker_gid()}",
                "-t",self.runner_image,"."
            ]
            subprocess.run(
                build_cmd,
                check=True,
                stdout=None if self.debug_runner else subprocess.PIPE,
                stderr=None if self.debug_runner else subprocess.PIPE
                )
            self.logger.info("✅ Runner image %s built successfully.", self.runner_image)
        except subprocess.CalledProcessError as e:
            self.logger.error("❌ Error building runner image: %s", e.stderr.decode())
        return

    def create_runner(self, github_repo: str):
        """Create a new GitHub Actions runner container."""
        runner_name_prefix = self.get_runner_name_prefix(github_repo)

        if self.runners_quantity(runner_name_prefix) >= self.max_runners:
            self.logger.info("🚀 Max runners reached. No new runner created.")
            return False

        try:
            # ✅ Add Docker-specific options only if Docker is enabled
            runner_cmd_docker_options = [
                item
                for item in ["--privileged", "-v", f"{self.docker_sock}:{self.docker_sock}"]
                if self.docker
            ]
            runner_cmd = [
                "docker", "run","-d",
                *runner_cmd_docker_options,
                "-e", f"GITHUB_TOKEN={self.github_token}","-e", f"GITHUB_REPO={github_repo}",self.runner_image
            ]
            # Run the container and get its ID securely
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
        # TODO: get quantity from the repo api, and maybe save them in a var to be available for the healtcheck api
        try:
            output = subprocess.check_output(
                ["docker", "ps", "--filter", f"name={runner_name_prefix}*", "--format", "{{.Names}}"]
            ).decode().strip()
            return len(output.split("\n")) if output else 0
        except subprocess.CalledProcessError:
            return 0
