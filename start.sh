#!/bin/bash
echo "test"
docker build -f Dockerfile.server -t webhook-ngrok . 

echo "🚀 Starting GitHub Runner Webhook Setup..."

# Step 2: Start all services in the background
echo "▶️ Starting services with Docker Compose..."
docker-compose up -d

# Step 3: Wait for ngrok to be available
echo "⏳ Waiting for ngrok to be ready..."
sleep 10

# Step 4: Fetch the ngrok public URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | jq -r '.tunnels[0].public_url')

if [[ -z "$NGROK_URL" || "$NGROK_URL" == "null" ]]; then
  echo "❌ Failed to retrieve ngrok URL. Make sure ngrok is running."
  exit 1
fi

echo "✅ ngrok is running at: $NGROK_URL"

# Step 5: Check the webhook health
echo "🔍 Checking webhook health..."
curl -s http://localhost:5000/health | jq

# Step 6: Display logs for debugging
echo "📜 Showing last 10 log entries..."
docker-compose logs --tail=10 webhook-handler

echo "🚀 Setup complete! The webhook is live at: $NGROK_URL"
echo "🔗 Add this URL to GitHub Webhooks: $NGROK_URL/webhook"