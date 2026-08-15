# SPAS — Smart Passive Attendance System

SPAS is a TypeScript microservice attendance system. The local stack provides the web portal, identity, attendance and AI adapter; the PyTorch face-AI service runs separately on the configured cloud endpoint.

## Services

| Service | Port | Responsibility |
| --- | ---: | --- |
| `gateway` | `8600` | React web, signed session, RBAC, public API |
| `identity-service` | internal | Users, roles and face-enrollment state |
| `attendance-service` | internal | Classes, schedules and attendance records |
| `ai-adapter-service` | internal | Validated/token-authenticated calls to cloud Face AI |
| `face-ai` | cloud | YOLO, FaceNet and encrypted enrollment gallery |

Only gateway is exposed to the browser. Internal services require `INTERNAL_SERVICE_TOKEN`; the browser never calls the cloud Face AI directly.

## Quick start for members

1. Install Docker Desktop and Git LFS.
2. Clone the repository:

   ```powershell
   git lfs install
   git clone https://github.com/kienkien05/SIC_AI_Project.git
   cd SIC_AI_Project
   Copy-Item .env.example .env
   ```

3. Set these `.env` values supplied by the project owner:

   ```text
   INTERNAL_SERVICE_TOKEN=<long-random-shared-token>
   SESSION_SECRET=<long-random-session-secret>
   FACE_AI_URL=https://<cloud-face-ai-domain>
   FACE_AI_TOKEN=<cloud-face-ai-token>
   ```

4. Start the local portal:

   ```powershell
   docker compose -f docker-compose.local.yml up --build
   ```

5. Open `http://127.0.0.1:8600`.

Demo accounts: `SV001/sv123`, `GV001/gv123`, `ADMIN001/admin123`.

## Security model

- User session is an `HttpOnly`, HMAC-signed cookie issued by gateway.
- Student cannot write attendance; teacher can only query assigned sections; internal services reject direct calls without their token.
- The AI cloud must set `FACE_AI_TOKEN`; it rejects requests without `x-spas-ai-token`.
- Do not commit `.env`, SQLite volumes, face gallery or enrollment images.

## Checks

```powershell
pnpm install
pnpm check
pnpm test:rbac
```

`test:rbac` proves an unauthenticated internal request is denied, a student attendance write gets `403`, and a teacher can access assigned sections.
