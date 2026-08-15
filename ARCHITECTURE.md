# SPAS microservices

```mermaid
flowchart LR
  Web[React web] --> Gateway[API gateway]
  Gateway --> Identity[Identity service]
  Gateway --> Attendance[Attendance service]
  Gateway --> Adapter[AI adapter]
  Adapter --> AI[Face AI cloud]
  Identity --> DB[(PostgreSQL)]
  Attendance --> DB
  AI --> Gallery[Encrypted gallery volume]
```

External clients call only the gateway. Identity owns users/roles; attendance owns courses, sections and attendance records; the AI adapter owns the cloud-AI contract. Face images and embeddings never enter the TypeScript databases.
