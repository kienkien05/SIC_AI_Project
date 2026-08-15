# Deploy Face AI to cloud

Deploy this once on the cloud VM. It requires Docker, Git LFS and the two repository checkpoints in `models/`.

```bash
git lfs install
git clone https://github.com/kienkien05/SIC_AI_Project.git
cd SIC_AI_Project
git lfs pull
cp .env.example .env
```

Set a long `FACE_AI_TOKEN` in `.env`, then validate and run:

```bash
docker compose -f docker-compose.ai-cloud.yml config
docker compose -f docker-compose.ai-cloud.yml up -d --build
curl http://127.0.0.1:8503/health
```

Port `8503` binds only to loopback. Put the service behind HTTPS (Caddy/Nginx) and proxy to `127.0.0.1:8503`; do not expose the port directly. Configure every local member's `.env` with the resulting HTTPS URL and exactly the same `FACE_AI_TOKEN`.

The `ai_gallery` Docker volume contains enrollment crops and FaceNet gallery data. Back it up securely and use encrypted cloud storage; do not copy it to GitHub.
