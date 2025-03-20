#!/bin/bash
# Step 1: Build the server Docker image
docker build -f Dockerfile.server -t github-webhook-server . 

echo "🚀 Starting GitHub Runner Webhook Setup..."

# Step 2: Start all services in the background
echo "▶️ Starting services with Docker Compose..."
docker compose up -d
