# 🏃‍♂️ Auto-Scaling GitHub Self-Hosted Runners

Auto-scale your GitHub self-hosted runners using Docker, webhooks, and ngrok! This project dynamically creates and removes containers to act as runners, only when needed — saving you resources and money 💸

---

## ✨ Features

Web-server to handle GitHub webhook and autoscale runners:

- 🚀 Uses github webhook to automatically spin up new runners when a workflow job is queued, it can also create the webhook if does not exist and CREATE_WEBHOOK_If_NOT_EXIST is set to true
- 🧼 Automatically stop and clean up runners after job completion
- 🔐 Secure webhook with ngrok tunnel
- 🌐 Supports both **ngrok free tier** (dynamic URLs) and **custom domain**, it can be disabled when NGROK_AUTHTOKEN is not set and you can use your own proxy solution

Self-hosted runner:

- 🐳 Full Docker-in-Docker support — can build and publish Docker images, need to set DOCKER=true
- 📦 Install Docker, Node.js via Docker ARGs

---

## 📦 Requirements

| Tool             | Required                                  | Notes                                                                                  |
| ---------------- | ----------------------------------------- | -------------------------------------------------------------------------------------- |
| Docker           | ✅                                        | Needed to build and run runner containers and user permissions                         |
| GitHub Token     | ✅                                        | Must have repo/workflow scope rights                                                   |
| Ngrok (optional) | ❌ (for options 1-3 already in the image) | Only required if you use Option 4 & you want automatic tunneling (free tier supported) |
| Python 3.8+, pip | ❌ (for options 1-3 already in the image) | Only required if you use Option 4                                                      |

---

## 📦 Architecture Diagram

```
GitHub Webhook -> Flask Web Server -> Runner Service -> Docker Container (GitHub Runner)
                                                             |
                                                             +-- Docker-in-Docker
                                                             +-- Optional Node.js/Python
```

---

## 🚀 Quickstart

Fill in your config in .env.local

```bash
cp .env.dist .env.local
```

Option 1 (Recommended),
create a `docker-compose.yaml` file with the following content, and then run `docker compose up -d`

```yaml
services:
  webhook-handler:
    image: vdiazroa/auto-scaling-gh-runners:latest
    restart: always
    env_file:
      - .env.local
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - 5001:5001
```

Option 2,
pull image from docker hub, and starts container

```bash
docker pull vdiazroa/auto-scaling-gh-runners:latest
docker run -d -v /var/run/docker.sock:/var/run/docker.sock --env-file ./.env.local vdiazroa/auto-scaling-gh-runners:latest
```

Option 3,
it clones the repository, builds the docker image and docker compose up

```bash
git clone https://github.com/vdiazroa/auto-scaling-gh-runners.git
cd auto-scaling-gh-runners
./start.sh
```

Option 4
it clones the repository, install requirements, and it starts the python server

```bash
git clone https://github.com/vdiazroa/auto-scaling-gh-runners.git
cd auto-scaling-gh-runners
make install
make run
```

---

## ⚙️ Configuration

Create a `.env.local` file with:

```env
####################################
# ### REQUIRED CONFIGURATION ###
####################################

GITHUB_TOKEN=ghp_...your_pat...

# ### needs to be at least one of the following provided
GITHUB_REPO=your_org_or_user/your_repo # or GITHUB_REPO=your_org_or_user/your_repo1,your_org_or_user/your_repo2
GITHUB_ORG=your_org # or GITHUB_ORG=your_org1,your_org2

####################################
# ### OPTIONAL CONFIGURATION ###
####################################

# ####### GITHUB RUNNER ##########

MAX_RUNNERS=5 # limit of github agents created # default is 10
DOCKER=false # installs docker to the agent # default false
NODE=true # installs node to the agent as well pnpm and yarn # default true
# python3 and pip is installed by default in the gh runner image

# ###### WEBSERVER CONFIG ########

SERVER_PORT=5001 # webserver port to listen the github webhool
CREATE_WEBHOOK_If_NOT_EXIST=true

# ########### NGROk ##############
NGROK_AUTHTOKEN=your_ngrok_token # if not provided, you need to setup your own tunnel or an nginx server to make webserver public
NGROK_DOMAIN=your ngrok domain # if not defined, the webserver will handle the changes of the ngrok url
```

---

## 🔄 Webhook Endpoint

When GitHub sends an event:

- If it's `workflow_job.queued`, a new runner container is started
- If it's `workflow_job.completed`, the runner is stopped and removed

Supports `/webhook` endpoint for GitHub configuration.

Health check is available at `/healthcheck`, by default localhost:5001/healtcheck.

---

## 🌐 ngrok Support

Out-of-the-box ngrok tunnel support. Works great with:

- ✅ Free tier (dynamic URLs)
- ✅ static subdomain or custom domain (also an option available in free tier)

Webhook URL is automatically retrieved from ngrok’s API.
No need to care if the dymanic Urls changes with dynamic URLs, the webserver handles it and updates the Github webhook Url

---

## 📝 Notes

- Runners are created with unique names: `RUNNER_NAME_PREFIX-shortid`
- Uses Flask + Waitress server
- Logs are printed to stdout
- Easy to extend and debug 🛠️

---

## 📜 License

MIT — use it, improve it, share it 🙌
