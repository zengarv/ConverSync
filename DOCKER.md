# Docker Setup for ConverSync

This document explains how to run ConverSync using Docker and Docker Compose.

## Prerequisites

- Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- Docker Compose (usually included with Docker Desktop)

## Quick Start

1. **Clone the repository and navigate to the project directory**
   ```bash
   git clone <repository-url>
   cd conversync
   ```

2. **Create environment file**
   ```bash
   copy .env.example .env
   ```
   Then edit `.env` with your actual API keys and configuration.

3. **Build and run the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Application: http://localhost:5000
   - With nginx (production profile): http://localhost

## Configuration Files

### Core Docker Files

- `Dockerfile` - Multi-stage build for the complete application
- `docker-compose.yml` - Production configuration
- `docker-compose.dev.yml` - Development overrides
- `.dockerignore` - Files to exclude from Docker build context
- `nginx.conf` - Nginx reverse proxy configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Required API Keys
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here

# Email Configuration (for sending meeting minutes)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your_email@gmail.com
APP_PASSWORD=your_app_password_here

# Model Configuration
GROQ_MODEL=whisper-large-v3-turbo
GEMINI_MODEL=gemini-2.5-flash

# Optional: Company branding
COMPANY_NAME=Your Company Name
```

## Docker Compose Profiles

### Default Profile (Production)
```bash
docker-compose up --build
```
- Runs the main application on port 5000
- Optimized for production use
- Frontend is built and served by Flask

### Development Profile
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```
- Enables hot reload for development
- Mounts source code as volumes
- Enables Flask debug mode

### Production with Nginx
```bash
docker-compose --profile production up --build
```
- Includes Nginx reverse proxy
- Rate limiting and security headers
- Serves on port 80
- Ready for SSL/HTTPS configuration

### Frontend Development Only
```bash
docker-compose --profile frontend-dev up frontend-dev
```
- Runs only the frontend development server
- Hot reload for React development
- Accessible on port 3000

## Docker Commands Reference

### Basic Operations
```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild without cache
docker-compose build --no-cache
```

### Development Commands
```bash
# Start development environment
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Access container shell
docker-compose exec conversync bash

# Install new Python packages
docker-compose exec conversync pip install package-name

# Restart specific service
docker-compose restart conversync
```

### Maintenance Commands
```bash
# Remove all containers and volumes
docker-compose down -v

# Clean up unused images
docker image prune

# View container resource usage
docker stats

# Check container health
docker-compose ps
```

## Volume Mounts

The application uses persistent volumes for:

- `./uploads` - Uploaded audio/video files
- `./outputs` - Generated PDF meeting minutes
- `./temp` - Temporary processing files

These directories are automatically created and persisted between container restarts.

## Health Checks

The application includes health checks:
- Endpoint: `http://localhost:5000/health`
- Checks database connectivity and service status
- Used by Docker Compose to monitor service health

## SSL/HTTPS Setup (Production)

To enable HTTPS with nginx:

1. **Generate SSL certificates** (example with Let's Encrypt):
   ```bash
   mkdir ssl
   # Copy your SSL certificates to ./ssl/cert.pem and ./ssl/key.pem
   ```

2. **Uncomment SSL configuration** in `nginx.conf`

3. **Start with production profile**:
   ```bash
   docker-compose --profile production up
   ```

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check what's using port 5000
   netstat -tulpn | grep :5000
   
   # Use different ports in docker-compose.yml
   ports:
     - "5001:5000"
   ```

2. **Permission issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER uploads outputs temp
   ```

3. **Build failures**
   ```bash
   # Clean build
   docker-compose down
   docker system prune -f
   docker-compose up --build
   ```

4. **Environment variables not loading**
   ```bash
   # Verify .env file exists and has correct format
   cat .env
   
   # Check container environment
   docker-compose exec conversync env | grep API_KEY
   ```

### Debugging

1. **Check logs**
   ```bash
   docker-compose logs conversync
   ```

2. **Access container**
   ```bash
   docker-compose exec conversync bash
   ```

3. **Test health endpoint**
   ```bash
   curl http://localhost:5000/health
   ```

### Performance Optimization

1. **Multi-stage builds** are used to minimize image size
2. **Layer caching** optimizes rebuild times
3. **Non-root user** enhances security
4. **Health checks** ensure service reliability

## Production Deployment

For production deployment:

1. Use environment-specific `.env` files
2. Enable nginx with SSL certificates
3. Configure log aggregation
4. Set up monitoring and alerting
5. Use Docker secrets for sensitive data
6. Consider using Docker Swarm or Kubernetes for orchestration

## Development Workflow

1. **Make code changes** in your editor
2. **With dev compose**: Changes are automatically reflected
3. **Test changes**: `docker-compose logs -f conversync`
4. **Debug issues**: `docker-compose exec conversync bash`
5. **Run tests**: `docker-compose exec conversync python -m pytest`

This Docker setup provides a complete, portable, and scalable deployment solution for ConverSync.
