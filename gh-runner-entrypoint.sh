#!/bin/bash

# Start Docker daemon if DOCKER is enabled
if [ "$DOCKER" = "true" ]; then
    echo "🧱 DOCKER=true - Starting Docker daemon..."

    # Ensure Docker group exists
    if ! getent group docker > /dev/null; then
        groupadd docker
    fi

    usermod -aG docker $(whoami)

    # Start Docker daemon
    dockerd &
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