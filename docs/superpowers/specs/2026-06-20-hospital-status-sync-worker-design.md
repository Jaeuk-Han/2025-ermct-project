# Hospital Status Sync Worker Design

## Goal

Run the existing ERMCT-to-Supabase hospital status synchronization continuously in production as a dedicated Docker Compose service.

## Architecture

The backend image will include the repository's `scripts/` directory. Production Compose will add a `hospital-status-sync` service built from the same context and Dockerfile as the FastAPI backend, while retaining an independent process lifecycle and restart policy.

The worker will execute:

```text
poetry run python scripts/sync_hospital_status.py --interval-seconds ${HOSPITAL_STATUS_SYNC_INTERVAL_SECONDS:-300}
```

Docker Compose performs interval interpolation. Deployments may tune the interval through `.env.production` without rebuilding; an omitted value uses 300 seconds.

## Configuration

The worker reads `.env.production` and requires:

- `ERMCT_SERVICE_KEY`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `HOSPITAL_STATUS_SYNC_SIDO`
- `HOSPITAL_STATUS_SYNC_SIGUNGU`

`HOSPITAL_STATUS_SYNC_INTERVAL_SECONDS` is optional and defaults to `300`. The Supabase service-role key remains server-only and will not have a `VITE_` equivalent.

## Scope

The patch changes only the backend image contents, production Compose configuration, production environment template, and deployment documentation or configuration tests needed to validate those changes. It does not modify FastAPI startup, frontend behavior, STT, KTAS, routing, recommendation, or sync-script behavior.

## Failure Behavior

The existing sync script logs failed cycles and continues after the configured interval. Compose uses `restart: unless-stopped` to restart the process after an unexpected process or host restart. Missing required variables cause the script to exit with its existing configuration error, making the failure visible in container logs.

## Validation

- Run the existing sync-script unit tests through Poetry.
- Run the full backend unit suite through Poetry.
- Compile the affected Python modules through Poetry.
- Render the production Compose configuration with `.env.production` and verify the worker command, environment source, build configuration, and default interval.

