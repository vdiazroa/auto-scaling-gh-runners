"""Script to publish new version"""
import sys
import re
import subprocess
from pathlib import Path

VERSION_FILE = Path("./__init__.py")

def get_current_version():
    """Get current version from __init__.py (supports v-prefixed versions)"""
    text = VERSION_FILE.read_text(encoding="utf-8")
    match = re.search(r'__version__\s*=\s*["\']v?(\d+)\.(\d+)\.(\d+)["\']', text)
    if not match:
        raise ValueError("❌ Could not find version in file.")
    return tuple(map(int, match.groups()))

def update_version(part):
    """Increment version number based on part type"""
    major, minor, patch = get_current_version()

    if part == "patch":
        patch += 1
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "major":
        major += 1
        minor = patch = 0
    else:
        raise ValueError("❌ Part must be one of: patch, minor, or major")

    new_version = f"v{major}.{minor}.{patch}"
    text = VERSION_FILE.read_text(encoding="utf-8")

    # Update the version string in the file
    new_text = re.sub(
        r'(__version__\s*=\s*["\'])v?\d+\.\d+\.\d+(["\'])',
        rf'\1{new_version}\2',
        text
    )
    VERSION_FILE.write_text(new_text, encoding="utf-8")
    print(f"✅ New version updated to: {new_version}")
    return new_version

def git_commit_and_tag(version):
    """Commit version bump and create Git tag"""
    subprocess.run(["git", "add", str(VERSION_FILE)], check=True)
    subprocess.run(["git", "commit", "-m", f"🔖 Update version to {version}"], check=True)
    subprocess.run(["git", "tag", version], check=True)
    subprocess.run(["git", "push"], check=True)
    subprocess.run(["git", "push", "--tags"], check=True)
    print(f"✅ Committed and tagged as {version}")

def main():
    """Start Script"""
    if len(sys.argv) != 2:
        print("Usage: python publish.py [patch|minor|major]")
        sys.exit(1)

    part = sys.argv[1].lower()
    version = update_version(part)
    git_commit_and_tag(version)

if __name__ == "__main__":
    main()
