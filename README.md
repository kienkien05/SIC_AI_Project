# SPAS Attendance

TypeScript web system for class schedules, face enrollment and AI attendance. The face model is accessed through the configured AI endpoint; this repository contains only the application services.

## Run on localhost

Prerequisite: Docker Desktop with Docker Compose v2.

```powershell
git clone https://github.com/kienkien05/SIC_AI_Project.git
cd SIC_AI_Project
Copy-Item .env.example .env
```

Set `.env` values:

```text
INTERNAL_SERVICE_TOKEN=<long-random-token>
SESSION_SECRET=<long-random-secret>
FACE_AI_TOKEN=<face-ai-token>
```

Start project:

```powershell
docker compose -f docker-compose.local.yml up --build
```

Lần khởi động đầu tiên, service AI tự tải checkpoint từ model repository trong `services/face-ai/seed.json`; các lần sau dùng cache Docker volume.

Open `http://127.0.0.1:8600`.

Demo accounts: `SV001/sv123`, `GV001/gv123`, `ADMIN001/admin123`.

## Useful commands

```powershell
docker compose -f docker-compose.local.yml down
```

## Structure

```text
frontend/   React portal
services/   gateway, identity, attendance, AI adapter
packages/   shared contracts and service security
```
