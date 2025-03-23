#!/bin/bash
# set -e

if [ "$DOCKER" = "true" ]; then
    echo "🔧 Docker support enabled"
    if [ ! -S /var/run/docker.sock ]; then
        echo "❌ Docker socket not found!"
        exit 1
    fi
fi

REGISTRATION_URL=$(echo "https://github.com/$GITHUB_REPO" | sed -E 's#/orgs##; s#/repos##')
TOKEN_URL="https://api.github.com/$GITHUB_REPO/actions/runners/registration-token"
TOKEN=$(curl -sX POST -H "Authorization: token $GITHUB_TOKEN" \
              -H "Accept: application/vnd.github.v3+json" \
              "$TOKEN_URL" | jq -r '.token')

if [ "$TOKEN" = "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ ERROR: Failed to retrieve registration token from GitHub."
    exit 1
fi

echo "✅ GitHub Runner Token acquired, registering runner at $REGISTRATION_URL"
./config.sh --url "$REGISTRATION_URL" --token "$TOKEN" --unattended --name "$(hostname)"

echo "🚀 Starting GitHub Runner..."

# Ensure we can cleanup on SIGTERM
_cleanup() {
    echo "🛑 Unregistering Runner..."
    ./config.sh remove --token "$TOKEN"
    exit 0
}
trap _cleanup SIGTERM

./run.sh &
wait $!