# Deploy Face AI to cloud

Deploy this once on the cloud VM. It requires Docker, Git LFS and the two repository checkpoints in `models/`.

```bash
git lfs install
git clone https://github.com/kienkien05/SIC_AI_Project.git
cd SIC_AI_Project
cp .env.example .env
```

Set a long `FACE_AI_TOKEN` in `.env`, then run:

```bash
docker compose -f docker-compose.ai-cloud.yml up -d --build
```

Put the service behind HTTPS (Caddy/Nginx) and forward requests to port `8503`. Configure every local member's `.env` with the resulting HTTPS URL and exactly the same `FACE_AI_TOKEN`.

The `ai_gallery` Docker volume contains enrollment crops and FaceNet gallery data. Back it up securely; do not copy it to GitHub.
