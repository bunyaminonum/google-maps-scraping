# 🐳 Docker Deployment Guide

Complete guide for deploying Google Maps Reviews Dashboard using Docker Compose.

## 📋 Prerequisites

- **Docker**: Version 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: Version 2.0+ (included with Docker Desktop)
- **API Keys**: 
  - Google Maps API Key (Places API enabled)
  - Gemini AI API Key (for AI analysis)

## 🚀 Quick Start

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd google-maps-scraping-1
git checkout feature/docker-deployment
```

### 2. Configure Environment

Create `.env` file in project root:

```env
# Google Maps API (Required)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Gemini AI API (Required for AI Analysis)
GEMINI_API_KEY=your_gemini_api_key_here
```

**🔒 Security Note:** Never commit `.env` file to version control!

### 3. Build and Run

```bash
# Build and start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Access Dashboard

Open browser and navigate to: **http://localhost:8501**

## 📦 What Gets Deployed?

### Container: `google-maps-dashboard`

- **Image**: Python 3.11 slim (multi-stage build)
- **Port**: 8501 (Streamlit default)
- **Features**:
  - Streamlit Dashboard UI
  - Background scheduler (optional)
  - Database persistence
  - API key management
  - Health checks

### Volumes (Persistent Data)

- `reviews.db` - SQLite database with all reviews
- `scheduler_status.json` - Scheduler state
- `scheduler_config.json` - Scheduler configuration
- `.env` - Environment variables (read-only)

## 🛠️ Docker Commands

### Basic Operations

```bash
# Start containers
docker-compose up -d

# Stop containers
docker-compose down

# Restart containers
docker-compose restart

# View logs (real-time)
docker-compose logs -f dashboard

# View logs (last 100 lines)
docker-compose logs --tail=100 dashboard
```

### Container Management

```bash
# Check container status
docker-compose ps

# Enter container shell
docker-compose exec dashboard /bin/bash

# View container resource usage
docker stats google-maps-dashboard

# Rebuild image (after code changes)
docker-compose build --no-cache
docker-compose up -d
```

### Data Management

```bash
# Backup database
docker cp google-maps-dashboard:/app/reviews.db ./backup_reviews.db

# Restore database
docker cp ./backup_reviews.db google-maps-dashboard:/app/reviews.db

# Clear all data and restart
docker-compose down -v
docker-compose up -d
```

## 🔧 Configuration Options

### Environment Variables

Edit `docker-compose.yml` to customize:

```yaml
environment:
  - STREAMLIT_SERVER_PORT=8501  # Change port if needed
  - STREAMLIT_THEME_BASE=light  # light or dark
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### Port Mapping

Change external port (default 8501):

```yaml
ports:
  - "8080:8501"  # Access via localhost:8080
```

### Resource Limits

Add resource constraints:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 512M
```

## 🔄 Running Scheduler Independently

To run scheduler as separate container (recommended for production):

1. **Edit `docker-compose.yml`** - Uncomment scheduler service:

```yaml
scheduler:
  build:
    context: .
    dockerfile: Dockerfile
  container_name: google-maps-scheduler
  volumes:
    - ./reviews.db:/app/reviews.db
    - ./scheduler_status.json:/app/scheduler_status.json
    - ./scheduler_config.json:/app/scheduler_config.json
    - ./.env:/app/.env:ro
  command: ["python", "run_scheduler_standalone.py"]
  restart: unless-stopped
  networks:
    - app-network
```

2. **Restart services:**

```bash
docker-compose up -d
```

## 🏥 Health Checks

### Automatic Health Monitoring

Container includes automatic health checks:

- **Interval**: Every 30 seconds
- **Timeout**: 10 seconds
- **Start Period**: 40 seconds (initial startup)
- **Retries**: 3 attempts before marking unhealthy

### Manual Health Check

```bash
# Check if dashboard is responding
curl http://localhost:8501/_stcore/health

# Expected response: "ok"
```

### View Health Status

```bash
# Check health status in docker-compose
docker-compose ps

# Detailed container health info
docker inspect google-maps-dashboard | grep -A 10 Health
```

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs dashboard

# Common issues:
# 1. Port 8501 already in use
docker-compose down
# Change port in docker-compose.yml
docker-compose up -d

# 2. Missing .env file
# Create .env with API keys

# 3. Permission issues
sudo chown -R $USER:$USER .
```

### Dashboard Not Accessible

```bash
# Check if container is running
docker-compose ps

# Check if port is listening
netstat -tuln | grep 8501  # Linux/Mac
netstat -an | findstr 8501  # Windows

# Check firewall rules
sudo ufw allow 8501  # Linux

# Restart container
docker-compose restart dashboard
```

### Database Issues

```bash
# Check database file exists
docker-compose exec dashboard ls -la /app/reviews.db

# Check permissions
docker-compose exec dashboard stat /app/reviews.db

# Reset database (⚠️ deletes all data)
docker-compose down
rm reviews.db
docker-compose up -d
```

### Performance Issues

```bash
# Check resource usage
docker stats google-maps-dashboard

# Increase resources in docker-compose.yml
# Add under dashboard service:
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '4'

# Restart
docker-compose restart
```

### Logs Showing Errors

```bash
# View detailed logs
docker-compose logs -f dashboard | grep ERROR

# Common errors:

# 1. "API key not found"
# → Check .env file exists and is mounted correctly

# 2. "Permission denied"
# → Fix file permissions: chmod 644 reviews.db

# 3. "Port already in use"
# → Change port in docker-compose.yml

# 4. "Module not found"
# → Rebuild image: docker-compose build --no-cache
```

## 🔐 Security Best Practices

### 1. API Keys

```bash
# Never commit .env to git
echo ".env" >> .gitignore

# Use read-only mount for .env
# Already configured in docker-compose.yml:
- ./.env:/app/.env:ro
```

### 2. Network Security

```bash
# Run on isolated network (already configured)
# Only expose necessary ports

# For production, use reverse proxy:
# - Nginx
# - Traefik
# - Caddy
```

### 3. Container Security

```bash
# Container runs as non-root user (configured in Dockerfile)
# Regular security updates:
docker-compose pull
docker-compose up -d
```

## 📊 Production Deployment

### Recommended Setup

```yaml
version: '3.8'

services:
  dashboard:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./reviews.db:/app/reviews.db
      - ./scheduler_status.json:/app/scheduler_status.json
      - ./scheduler_config.json:/app/scheduler_config.json
      - ./.env:/app/.env:ro
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 512M
      restart_policy:
        condition: on-failure
        max_attempts: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Monitoring

```bash
# Setup monitoring with Prometheus + Grafana
# Or use Docker stats API

# View real-time metrics
watch -n 2 'docker stats google-maps-dashboard'

# Export logs to external system
docker-compose logs dashboard | your-log-aggregator
```

## 🔄 Updates and Maintenance

### Updating Code

```bash
# 1. Pull latest changes
git pull origin feature/docker-deployment

# 2. Rebuild image
docker-compose build --no-cache

# 3. Restart with new image
docker-compose up -d

# 4. Verify
docker-compose logs -f dashboard
```

### Backup Strategy

```bash
# Create backup script (backup.sh)
#!/bin/bash
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
docker cp google-maps-dashboard:/app/reviews.db $BACKUP_DIR/
cp scheduler_status.json $BACKUP_DIR/
cp scheduler_config.json $BACKUP_DIR/
echo "Backup completed: $BACKUP_DIR"

# Make executable
chmod +x backup.sh

# Run backup
./backup.sh
```

### Restore from Backup

```bash
# Stop container
docker-compose down

# Restore files
cp backups/YYYYMMDD_HHMMSS/reviews.db ./
cp backups/YYYYMMDD_HHMMSS/scheduler_status.json ./
cp backups/YYYYMMDD_HHMMSS/scheduler_config.json ./

# Restart
docker-compose up -d
```

## 📈 Scaling (Future)

For high-traffic scenarios:

```yaml
# Use Docker Swarm or Kubernetes
# Example: Multiple dashboard replicas with load balancer

version: '3.8'
services:
  dashboard:
    # ... existing config
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
```

## 🆘 Support

### Debug Mode

```bash
# Run with debug output
docker-compose up

# Access container shell for debugging
docker-compose exec dashboard /bin/bash

# Check Python environment
docker-compose exec dashboard python --version
docker-compose exec dashboard pip list
```

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Container exits immediately | Check logs: `docker-compose logs dashboard` |
| Can't access localhost:8501 | Check firewall, port mapping, container status |
| API errors | Verify API keys in .env file |
| Database locked | Stop all processes accessing DB, restart container |
| Out of memory | Increase Docker memory limit in Docker Desktop settings |

## ✅ Verification Checklist

After deployment, verify:

- [ ] Container is running: `docker-compose ps`
- [ ] Dashboard accessible: http://localhost:8501
- [ ] Database exists: `docker-compose exec dashboard ls /app/reviews.db`
- [ ] Environment loaded: `docker-compose exec dashboard env | grep API`
- [ ] Health check passing: `docker inspect google-maps-dashboard | grep Health`
- [ ] Logs clean: `docker-compose logs dashboard | grep ERROR`

---

**Last Updated:** November 8, 2025  
**Docker Version:** 20.10+  
**Docker Compose Version:** 2.0+
