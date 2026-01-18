# 🚀 Deployment Guide - Orders Service

## Overview

This guide covers deploying the Orders Service to various platforms including Railway, Heroku, local Docker, and Docker Compose.

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+ (for local development)
- PostgreSQL 15+ (or use provided docker-compose)
- Python 3.11+ (for local development without Docker)

## 🏗️ Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│   Orders API    │────▶│   PostgreSQL     │     │   RabbitMQ     │
│   (Port 8003)   │     │   (Port 5435)    │     │   (Optional)   │
└─────────────────┘     └──────────────────┘     └────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     External Services                            │
│  - Customer Service (8001)                                       │
│  - Product Service (8002)                                        │
│  - Payment Gateway (9000)                                        │
└─────────────────────────────────────────────────────────────────┘
```

## 🐳 Docker Deployment

### Local Docker (Single Container)

```bash
cd api-orders

# Build the image
docker build -t orders-api:latest .

# Run the container
docker run -d \
  --name orders-api \
  -p 8003:8003 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/orders_db" \
  -e RABBITMQ_HOST="host.docker.internal" \
  orders-api:latest
```

### Docker Compose (Full Stack)

```bash
cd api-orders

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f orders-api

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

**Services Started:**
- PostgreSQL Database (port 5435)
- Orders API (port 8003)

**Access Points:**
- API: http://localhost:8003
- API Docs: http://localhost:8003/docs
- Health Check: http://localhost:8003/health

## ☁️ Railway Deployment

### Configuration

The service is configured via `railway.toml`:

```toml
[build]
builder = "DOCKERFILE"
dockerfilePath = "Dockerfile"

[deploy]
startCommand = "bash entrypoint.sh"
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
healthcheckPath = "/health"
healthcheckTimeout = 100
```

### Required Environment Variables

Set these in Railway dashboard:

```bash
# Database (Railway provides DATABASE_URL automatically)
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Optional: Override port (Railway sets this automatically)
PORT=8003

# RabbitMQ (optional - service works without it)
RABBITMQ_HOST=your-rabbitmq-host
RABBITMQ_USER=your-user
RABBITMQ_PASSWORD=your-password

# External Services
CUSTOMER_SERVICE_URL=http://your-customer-service
PRODUCT_SERVICE_URL=http://your-product-service

# Security
SECRET_KEY=your-secure-secret-key
```

### Deployment Steps

1. **Connect Repository**
   - Go to Railway dashboard
   - Create new project
   - Connect GitHub repository
   - Select `api-orders` as root directory

2. **Add PostgreSQL**
   - Click "New" → "Database" → "PostgreSQL"
   - Railway automatically sets DATABASE_URL

3. **Configure Service**
   - Environment variables are set automatically
   - Verify in Variables tab

4. **Deploy**
   - Push to main branch or click "Deploy"
   - Monitor deployment logs
   - Wait for "healthy" status

### Monitoring Deployment

```bash
# Expected log sequence:
🚀 Orders Service - Starting Deployment
📊 Environment Information
🔍 Checking database connectivity
📦 Running database migrations
   ✅ Migrations completed successfully
🌐 Starting Orders API Server
✨ Orders Service is starting up...
INFO: Started server process
INFO: Waiting for application startup.
INFO: Application startup complete.
```

### Troubleshooting Railway

**Issue: Deployment stuck at "complete"**
- Check DATABASE_URL is set correctly
- Verify migrations can connect to database
- Check logs for error messages

**Issue: Health check failing**
- Ensure PORT env variable matches startCommand
- Verify /health endpoint responds
- Check healthcheckTimeout is sufficient

**Issue: Import errors**
- Ensure all dependencies in requirements.txt
- Check PYTHONPATH is correct
- Verify working directory is /app

## 🌐 Heroku Deployment

Uses `Procfile`:

```
web: bash entrypoint.sh
```

Required buildpacks:
- heroku/python

Required add-ons:
- Heroku Postgres

Environment variables (same as Railway)

## 🔧 Configuration Files

### Key Files

- **Dockerfile**: Multi-stage optimized Docker image
- **docker-compose.yml**: Local full-stack development
- **entrypoint.sh**: Production startup script
- **railway.toml**: Railway platform configuration
- **Procfile**: Heroku configuration
- **requirements.txt**: Python dependencies
- **alembic.ini**: Database migration configuration

### Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| DATABASE_URL | - | ✅ | PostgreSQL connection string |
| PORT | 8003 | ❌ | API server port |
| API_HOST | 0.0.0.0 | ❌ | API bind address |
| DEBUG | false | ❌ | Debug mode |
| RABBITMQ_HOST | localhost | ❌ | RabbitMQ host |
| RABBITMQ_USER | payetonkawa | ❌ | RabbitMQ username |
| RABBITMQ_PASSWORD | - | ❌ | RabbitMQ password |
| CUSTOMER_SERVICE_URL | - | ❌ | Customer service endpoint |
| PRODUCT_SERVICE_URL | - | ❌ | Product service endpoint |
| SECRET_KEY | - | ✅ | JWT secret key |

## 🧪 Testing Deployment

### Health Check

```bash
curl http://localhost:8003/health

# Expected response:
{
  "status": "healthy",
  "service": "orders-api",
  "version": "1.0.0"
}
```

### API Documentation

```bash
# Swagger UI
open http://localhost:8003/docs

# ReDoc
open http://localhost:8003/redoc
```

### Database Migrations

```bash
# Check current revision
docker exec orders-api alembic current

# Run migrations manually
docker exec orders-api alembic upgrade head

# Rollback migration
docker exec orders-api alembic downgrade -1
```

## 📊 Monitoring

### Logs

```bash
# Docker Compose
docker-compose logs -f orders-api

# Docker
docker logs -f orders-api

# Railway
# View in Railway dashboard under Deployments → Logs
```

### Metrics

Monitor these endpoints:
- Health: `GET /health`
- Metrics: `GET /metrics` (if implemented)

### Common Issues

1. **Database Connection Errors**
   - Verify DATABASE_URL format
   - Check database is accessible
   - Ensure asyncpg driver in URL

2. **Port Conflicts**
   - Change host port in docker-compose.yml
   - Ensure PORT env variable is correct

3. **Migration Failures**
   - Check database permissions
   - Verify alembic.ini configuration
   - Ensure migrations/ directory exists

4. **RabbitMQ Connection Issues**
   - Service gracefully degrades without RabbitMQ
   - Check RABBITMQ_HOST is accessible
   - Verify credentials

## 🔐 Security Considerations

1. **Environment Variables**
   - Never commit .env files
   - Use secrets management (Railway Secrets, etc.)
   - Rotate keys regularly

2. **Database**
   - Use strong passwords
   - Enable SSL/TLS connections
   - Restrict network access

3. **Container**
   - Runs as non-root user (appuser)
   - Minimal base image (python:3.11-slim)
   - No unnecessary packages

## 🚀 Performance Optimization

1. **Docker Build**
   - Uses layer caching
   - .dockerignore excludes unnecessary files
   - Multi-stage build pattern

2. **Application**
   - Async/await throughout
   - Connection pooling
   - Graceful shutdown

3. **Database**
   - Indexed columns
   - Connection pool configured
   - Query optimization

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Railway Documentation](https://docs.railway.app/)

---

**Last Updated**: January 5, 2026
**Version**: 1.0.0
