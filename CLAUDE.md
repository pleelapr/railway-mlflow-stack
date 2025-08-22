# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a containerized MLFlow stack designed for deployment on Railway. The stack consists of four main services:

- **Caddy**: Reverse proxy with authentication (auth gateway)
- **MLFlow Server**: Python-based ML experiment tracking server
- **PostgreSQL**: Backend database for MLFlow metadata storage
- **MinIO**: S3-compatible object storage for MLFlow artifacts

## Architecture

The entire stack is orchestrated via Docker Compose with service dependencies and health checks:
- Caddy acts as an authentication gateway, proxying requests to MLFlow
- MLFlow depends on both PostgreSQL and MinIO being healthy before starting
- MLFlow is only accessible through Caddy (no direct external access)
- PostgreSQL uses persistent volume at `./postgres-data/`
- MinIO automatically creates a "bucket" for artifact storage and serves a web console
- All services use custom Dockerfiles with startup scripts

## Development Commands

### Running the Stack
```bash
# Start all services
docker-compose up

# Start services in background
docker-compose up -d

# View logs for specific service
docker-compose logs caddy
docker-compose logs mlflow
docker-compose logs minio
docker-compose logs postgres

# Stop all services
docker-compose down

# Rebuild and restart services
docker-compose up --build
```

### Service Access Points
- **MLFlow UI**: https://localhost:443 (through Caddy auth proxy)
- **MinIO Console**: http://localhost:9001
- **PostgreSQL**: localhost:5432

**Note**: MLFlow is only accessible through Caddy's authenticated proxy. Direct access on port 5000 is disabled for security.

### Troubleshooting
```bash
# Check service health status
docker-compose ps

# Restart individual service
docker-compose restart caddy
docker-compose restart mlflow

# View real-time logs (especially useful for auth debugging)
docker-compose logs -f caddy
docker-compose logs -f mlflow
```

## Configuration

### Environment Variables
Key environment variables are defined in docker-compose.yml:

**Authentication (Caddy)**
- `AUTH_USERNAME`: Basic auth username (Railway will generate, defaults to "admin")
- `AUTH_PASSWORD`: Basic auth password (Railway will generate, defaults to "changeme")
- `OAUTH2_CLIENT_ID`: OAuth2 client ID (optional, for OAuth2 setup)
- `OAUTH2_CLIENT_SECRET`: OAuth2 client secret (optional, for OAuth2 setup)

**MLFlow & Storage**
- `DB_URL`: PostgreSQL connection string for MLFlow
- `MLFLOW_S3_ENDPOINT_URL`: MinIO endpoint for artifact storage  
- `AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY`: MinIO credentials
- `MINIO_ROOT_USER/MINIO_ROOT_PASSWORD`: MinIO admin credentials

### Database
- Database: `mlflowdb`
- User: `user` 
- Password: `password`
- Default storage in `./postgres-data/`

### Object Storage
- MinIO creates bucket named "bucket" automatically
- Artifacts stored in `./minio/data/`
- Console credentials: minio_user/minio_password

## File Structure
- `caddy/`: Caddy reverse proxy with authentication configuration
- `mlflow/`: MLFlow server container configuration
- `minio/`: MinIO object storage container configuration  
- `postgresql/`: PostgreSQL configuration directory
- `docker-compose.yml`: Main orchestration file

## Authentication & Security

### Basic Authentication (Default)
The stack uses Caddy as an authentication gateway with basic auth by default:
- Username/password are set via `AUTH_USERNAME` and `AUTH_PASSWORD` environment variables
- Railway will automatically generate secure credentials on deployment
- For local development, defaults to admin/changeme
- Passwords are automatically hashed using bcrypt during startup

### Railway Deployment
When deploying to Railway:
1. Railway will provide `AUTH_USERNAME` and `AUTH_PASSWORD` as environment variables
2. Caddy will be exposed on port 443 (Railway handles SSL termination automatically)
3. MLFlow service remains internal-only (no direct external access)
4. Railway's edge proxy provides automatic SSL certificates

### OAuth2 Setup (Advanced)
To enable OAuth2 authentication (e.g., Google, GitHub):

1. Uncomment the OAuth2 section in `caddy/Caddyfile`
2. Set up OAuth2 application with your provider
3. Configure environment variables:
   ```bash
   OAUTH2_CLIENT_ID=your_client_id
   OAUTH2_CLIENT_SECRET=your_client_secret
   ```
4. Update the redirect URI in Caddyfile to match your Railway domain
5. Configure allowed users/domains in the Caddyfile

**Supported OAuth2 Providers**: Google, GitHub, Facebook, Microsoft, and others supported by Caddy's oauth directive.

### Rate Limiting (Optional)
To enable rate limiting, uncomment the rate_limit section in `caddy/Caddyfile`:
- Default: 100 requests per minute per IP
- Configurable per zone and time window
- Useful for protecting against abuse

### Security Features
- **HTTPS Only**: All traffic encrypted (Railway provides SSL)
- **Security Headers**: XSS protection, clickjacking prevention, HSTS
- **No Direct MLFlow Access**: All access goes through authenticated proxy
- **Bcrypt Password Hashing**: Secure password storage
- **Request Logging**: All authentication attempts logged