# Ncloud Single-Server Deployment

This guide deploys the FastAPI backend and Vite frontend to one Ubuntu server on NAVER Cloud Platform using Docker Compose and Nginx.

## Architecture

- Nginx listens on port 80 and serves the built React/Vite frontend.
- Frontend API calls use `VITE_API_BASE_URL=/api`.
- Nginx proxies `/api/*` to the FastAPI backend container.
- FastAPI runs with Uvicorn on `0.0.0.0:8000` inside Docker.
- `/health` is proxied directly to FastAPI.
- Supabase remains external.
- Logs are available with `docker compose -f docker-compose.prod.yml logs`.

The backend routes in this repository already include `/api`, so `nginx/default.conf` preserves that prefix when proxying to FastAPI.

## Ncloud ACG / Firewall

Open these inbound ports in the Ncloud ACG:

- SSH: `22` from your IP only.
- HTTP: `80` from `0.0.0.0/0`.
- HTTPS: `443` from `0.0.0.0/0` if you configure SSL.

On Ubuntu, allow the same ports if UFW is enabled:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw status
```

## Server Setup

Connect to the server:

```bash
ssh ubuntu@YOUR_SERVER_PUBLIC_IP
```

Install Docker and the Docker Compose plugin:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker "$USER"
newgrp docker
```

Clone the repository:

```bash
git clone https://github.com/Jaeuk-Han/2025-ermct-project.git
cd 2025-ermct-project
```

Create production env values:

```bash
cp .env.production.example .env.production
nano .env.production
```

Set real values for:

- `OPENAI_API_KEY`
- `ERMCT_SERVICE_KEY`
- `TMAP_APP_KEY`
- `KAKAO_REST_API_KEY`
- `CORS_ALLOW_ORIGINS`, for example `http://YOUR_SERVER_PUBLIC_IP` or `https://your-domain.example`
- `VITE_API_BASE_URL=/api`
- `VITE_TMAP_API_KEY`
- `VITE_KAKAO_MAP_KEY`
- `VITE_SUPABASE_URL`
- `VITE_SUPABASE_ANON_KEY`

Do not commit `.env.production`.

Configure external service consoles before testing the browser app:

- Kakao JavaScript key: add allowed domains for `http://YOUR_SERVER_PUBLIC_IP` and later `https://your-domain.example`.
- T-map browser key: add the production domain/IP in the app settings if your T-map console enforces web domain restrictions.
- Supabase Auth: if Auth is used, set the Site URL and Redirect URLs to the production origin, for example `http://YOUR_SERVER_PUBLIC_IP` and later `https://your-domain.example`.

Build and start:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml build
docker compose --env-file .env.production -f docker-compose.prod.yml up -d
```

Changing any `VITE_*` variable requires rebuilding the frontend image:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml build frontend
docker compose --env-file .env.production -f docker-compose.prod.yml up -d frontend
```

## Validation

Check containers:

```bash
docker compose -f docker-compose.prod.yml ps
```

Check logs:

```bash
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
```

Check backend health through Nginx:

```bash
curl -i http://YOUR_SERVER_PUBLIC_IP/health
```

Check API proxy:

```bash
curl -i http://YOUR_SERVER_PUBLIC_IP/api/ktas/predict-text
```

A `405 Method Not Allowed` response is acceptable for the proxy check because the endpoint expects `POST`.

Check frontend:

```bash
curl -I http://YOUR_SERVER_PUBLIC_IP/
```

Validate Compose and Nginx config:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml config
docker compose -f docker-compose.prod.yml exec frontend nginx -t
```

Check that env vars are loaded without printing secrets:

```bash
docker compose -f docker-compose.prod.yml exec backend sh -lc 'test -n "$ERMCT_SERVICE_KEY" && test -n "$TMAP_APP_KEY" && echo "backend env loaded"'
```

## Optional Domain and SSL

Point your domain A record to the Ncloud server public IP. After DNS resolves, install Certbot on the host or add a certificate-aware reverse proxy. A simple host-based Certbot flow is:

```bash
sudo apt-get install -y certbot
sudo certbot certonly --standalone -d your-domain.example
```

To terminate SSL in the Nginx container, mount the certificate files and add a `443` server block to `nginx/default.conf`, then uncomment the `443:443` port mapping in `docker-compose.prod.yml`.

## Local Validation Commands

Backend:

```bash
poetry run python -m unittest discover -s tests -v
poetry run python -m py_compile app/main.py app/ktas_engine.py app/stt_cleaner.py
```

Frontend:

```powershell
cd front
npm.cmd run build
```

Docker:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml config
docker compose --env-file .env.production -f docker-compose.prod.yml build
```

## Troubleshooting

- `401` or API-auth errors: confirm external API keys in `.env.production`.
- Frontend still calls the old API URL: rebuild the frontend image after changing `VITE_*` variables.
- Browser CORS errors: set `CORS_ALLOW_ORIGINS` to the exact frontend origin, including scheme and port.
- `/api/...` returns `502`: check `docker compose -f docker-compose.prod.yml logs backend`.
- `413 Request Entity Too Large` on audio upload: confirm `client_max_body_size 25m;` is present in `nginx/default.conf`, then rebuild and restart the frontend/Nginx container.
- Audio/STT failures: confirm the backend image includes `ffmpeg` and check backend logs.
- Supabase auth/realtime failures: confirm `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY`, then rebuild frontend.

## Rollback

Return to the previous Git revision and rebuild:

```bash
git log --oneline -5
git checkout PREVIOUS_COMMIT_SHA
docker compose --env-file .env.production -f docker-compose.prod.yml build
docker compose --env-file .env.production -f docker-compose.prod.yml up -d
```

Or stop the deployment:

```bash
docker compose -f docker-compose.prod.yml down
```
