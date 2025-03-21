#!/bin/bash

if [ "$DOCKER" = "true" ]; then
    echo "🔧 Setting Docker socket permissions..."
    SOCKET="/var/run/docker.sock"
    if [ -S "$SOCKET" ]; then
        DOCKER_GID=$(stat -c '%g' "$SOCKET")
        echo "🧩 Detected Docker GID: $DOCKER_GID"
        # Create docker group with the same GID if it doesn't exist
        if ! getent group "$DOCKER_GID" > /dev/null; then
            echo "➕ Creating group with GID $DOCKER_GID"
            groupadd -g "$DOCKER_GID" docker
        else
            echo "✅ Group with GID $DOCKER_GID already exists"
        fi
        # Add current user to that group
        echo "➕ Adding $(whoami) to docker group"
        usermod -aG docker "$(whoami)"
    else
        echo "❌ Docker socket not found at $SOCKET"
    fi
fi

REGISTRATION_URL=$(echo "https://github.com/$GITHUB_REPO" | sed -E 's#/orgs##; s#/repos##')
TOKEN_URL="https://api.github.com/$GITHUB_REPO/actions/runners/registration-token"
TOKEN=$(curl -sX POST -H "Authorization: token $GITHUB_TOKEN" \
              -H "Accept: application/vnd.github.v3+json" \
              "$TOKEN_URL" | jq -r '.token')

# Ensure the token is valid
if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ ERROR: Failed to retrieve registration token from GitHub."
    exit 1
fi

echo "✅ GitHub Runner Token acquired, registering runner at $REGISTRATION_URL"

# Register the runner
./config.sh --url "$REGISTRATION_URL" --token "$TOKEN" --unattended --name "$(hostname)"

# Start the runner
echo "🚀 Starting GitHub Runner..."
./run.sh &

# Ensure the runner unregisters before exit
trap 'echo "🛑 Unregistering Runner..."; ./config.sh remove --token "$TOKEN"; exit 0' SIGTERM

# Keep the process running
wait $!