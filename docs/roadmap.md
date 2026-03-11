 ## Roadmap / backlog (beyond timebox)
 
 ### Product / API
 - Add pagination, sorting, and richer filtering for `GET /vms`
 - Add `PATCH /vms/{id}` for metadata updates (name/tags)
 - Add asynchronous operation model (task IDs) for long-running operations
 
 ### OpenStack integration
 - Implement `OpenStackSDKDriver` using `openstacksdk`
 - Add “cloud configuration” via env vars or `clouds.yaml`
 - Map OpenStack server states and faults into the API’s error model
 
 ### Reliability & operations
 - Add structured logging and request correlation IDs
 - Add metrics (Prometheus) and tracing (OpenTelemetry)
 - Add persistent storage (SQLite/Postgres) instead of in-memory dict
 - Add retries/backoff/circuit breaking for driver operations
 
 ### Security
 - Add authentication (API keys / JWT) and RBAC
 - Input validation hardening + rate limiting
 - Audit log for lifecycle events
 
 ### DevOps / SDLC
 - Add pre-commit hooks and format/lint checks locally
 - Add containerization (Dockerfile) + compose for local run
 - Add contract tests and API versioning strategy
