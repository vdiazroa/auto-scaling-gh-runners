# 🏃‍♂️ Auto-Scaling GitHub Self-Hosted Runners

Auto-scale your GitHub self-hosted runners using Docker, webhooks, and ngrok! This project dynamically creates and removes containers to act as runners, only when needed — saving you resources and money 💸

---

## ✨ Features

- 🚀 Automatically spin up new runners when a workflow job is queued
- 🧼 Automatically stop and clean up runners after job completion
- 🐳 Full Docker-in-Docker support — can build and publish Docker images
- 📦 Install Docker, Node.js, and Python optionally via Docker ARGs
- 🔐 Secure webhook with ngrok tunnel
- 🌐 Supports both **ngrok free tier** (dynamic URLs) and **custom domain**

---

## 📦 Requirements

| Tool             | Required | Notes                                                               |
| ---------------- | -------- | ------------------------------------------------------------------- |
| Docker           | ✅       | Needed to build and run runner containers                           |
| GitHub Token     | ✅       | Must have repo/workflow scope                                       |
| Ngrok (optional) | ❌       | Required only if you want automatic tunneling (free tier supported) |
| Python 3.8+, pip |          | required if you use Option 4                                        |

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

Option 1,
it clones the repository, builds the docker image and docker compose up

```bash
git clone https://github.com/vdiazroa/auto-scaling-gh-runners.git
cd auto-scaling-gh-runners
./start.sh
```

Option 2,
pull image from docker hub, and starts container

```bash
docker pull vdiazroa/auto-scaling-gh-runners:latest
docker run -d -v /var/run/docker.sock:/var/run/docker.sock --env-file ./env.local vdiazroa/auto-scaling-gh-runners:latest
```

Option 3,
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

Option 4
it clones the repository, install requirements, and it starts the python server

```bash
git clone https://github.com/vdiazroa/auto-scaling-gh-runners.git
cd auto-scaling-gh-runners
pip install -r requirements.txt
python app.py
```

---

## ⚙️ Configuration

Create a `.env.local` file with:

```env
####################################
# ### REQUIRED CONFIGURATION ###
####################################

GITHUB_TOKEN=ghp_...your_pat...

# ### checks if the GITHUB_REPO exists then it uses the repo, else uses the org
GITHUB_REPO=your_org_or_user/your_repo
GITHUB_REPO=your_org

####################################
# ### OPTIONAL CONFIGURATION ###
####################################

# ####### GITHUB RUNNER ##########

MAX_RUNNERS=5 # limit of github agents created # default is 10
MIN_RUNNERS=1 # runnes created at startup # default is 1
DOCKER=false # installs docker to the agent # default false
NODE=true # installs node to the agent as well pnpm and yarn # default true
# python3 and pip is installed by default in the gh runner image

# ###### WEBSERVER CONFIG ########

SERVER_PORT=5001 # webserver port to listen the github webhool
CREATE_WEBHOOK_If_NOT_EXIST

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
No need to care if the dymanic Urls changes, the webserver handles it and updates the Github webhook Url

---

## 📝 Notes

- Runners are created with unique names: `RUNNER_NAME_PREFIX-shortid`
- Uses Flask + Waitress server
- Logs are printed to stdout
- Easy to extend and debug 🛠️

---

## 📜 License

MIT — use it, improve it, share it 🙌
