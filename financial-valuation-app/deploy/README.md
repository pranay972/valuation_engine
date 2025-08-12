# AWS EC2 Deployment Guide

Complete guide for deploying the Financial Valuation Application to AWS EC2.

## 📋 Prerequisites

- AWS EC2 instance (Amazon Linux 2 recommended)
  - **Minimum**: t3.micro (1 vCPU, 1 GB RAM)
  - **Recommended**: t3.small (2 vCPU, 2 GB RAM) or t3.medium (2 vCPU, 4 GB RAM)
- Security group with ports 80 (HTTP), 22 (SSH), 3001, 8001, and 5555 open
- SSH access to your EC2 instance
- At least 8 GB available disk space

**Note**: Uses ports 3001 (frontend), 8001 (backend), and 5555 (Celery Flower) to avoid conflicts.

## 🚀 Deployment Steps

### Step 1: Initial EC2 Setup
```bash
# Connect to your EC2 instance
ssh -i your-key.pem ec2-user@your-ec2-public-ip

# Run the setup script
chmod +x deploy/ec2-setup.sh
./deploy/ec2-setup.sh
```

### Step 2: Deploy Application
```bash
# Clone repository
cd /home/ec2-user
git clone https://github.com/your-username/financial-valuation-app.git
cd financial-valuation-app

# Validate deployment (optional but recommended)
chmod +x deploy/validate-deployment.sh
./deploy/validate-deployment.sh

# Deploy
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### Step 3: Verify Deployment
Access your application:
- **Frontend**: `http://your-ec2-public-ip`
- **Backend API**: `http://your-ec2-public-ip/api`
- **Swagger UI**: `http://your-ec2-public-ip/api/docs`
- **Health Check**: `http://your-ec2-public-ip/health`
- **Celery Flower**: `http://your-ec2-public-ip:5555`

## 🔧 Management Commands

```bash
# View logs
cd /home/ec2-user/financial-valuation-app
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update application
./deploy/deploy.sh

# Check status
docker-compose ps

# Validate deployment
./deploy/validate-deployment.sh

# Clean up system (for lightweight instances)
sudo yum clean all
docker system prune -af --volumes
sudo journalctl --vacuum-time=7d
```

## 🆘 Troubleshooting

### Check Services
```bash
# Docker status
sudo systemctl status docker

# Nginx status
sudo systemctl status nginx

# View logs
sudo tail -f /var/log/nginx/error.log
docker-compose logs backend
docker-compose logs frontend
docker-compose logs celery
```

### Health Check Issues
```bash
# Test backend health directly
curl -v http://localhost:8001/health

# Check if Flask app is running
docker-compose exec backend ps aux | grep python

# Verify Flask entry point
ls -la backend/run.py
```

### Lightweight Instance Issues
```bash
# Check available memory
free -h

# Check available disk space
df -h /

# Check Docker resource usage
docker system df

# Monitor container resources
docker stats

# Clean up if running out of space
docker system prune -af --volumes
sudo yum clean all
sudo journalctl --vacuum-time=1d
```

### API Connection Issues (Common Production Problem)
If you see errors like "requested insecure content from http://localhost:8001/api":

```bash
# 1. Check your .env file
cat .env | grep REACT_APP_API_URL

# 2. Verify the URL is correct (should NOT be localhost)
# Should be: https://yourdomain.com/api
# NOT: http://localhost:8001/api

# 3. Rebuild and restart containers
docker-compose down
docker-compose up -d --build

# 4. Check container environment variables
docker-compose exec frontend env | grep REACT_APP_API_URL

# 5. Verify frontend is using correct API URL
docker-compose logs frontend | grep "API_URL\|localhost"
```

**Common Fix**: Update your `.env` file with the correct production domain:
```bash
REACT_APP_API_URL=https://yourdomain.com/api
```

### Restart Everything
```bash
sudo systemctl restart docker
sudo systemctl restart nginx
docker-compose down && docker-compose up -d
```

## 🔒 Security Considerations

1. **Update Security Groups** - Ensure only necessary ports are open
2. **Use HTTPS** - Consider setting up SSL/TLS certificates
3. **Regular Updates** - Keep system and Docker images updated
4. **Backup** - Consider setting up automated backups

## 📊 Environment Variables

### Production Environment Setup
For production deployments, create a `.env` file in your deployment directory:

```bash
# Copy the production template
cp deploy/production.env .env

# Edit the file with your production values
nano .env
```

### Required Environment Variables
```bash
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-change-this-immediately

# Frontend Configuration (CRITICAL for production)
REACT_APP_API_URL=https://your-domain.com/api

# Database Configuration
DATABASE_URL=sqlite:///financial_valuation.db

# Redis Configuration
REDIS_URL=redis://redis:6379/0
```

### Production Configuration
For production deployments, ensure:
- `FLASK_ENV=production` is set
- Strong `SECRET_KEY` is configured (change from default)
- `REACT_APP_API_URL` points to your production domain (not localhost!)
- Production database credentials are used
- Redis is properly secured
- Health checks are enabled

## 💾 Backup and Recovery

### Backup Docker volumes
```bash
docker run --rm -v financial-valuation-app_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .
```

### Restore from backup
```bash
docker run --rm -v financial-valuation-app_data:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /data
```

## 📈 Monitoring

Consider setting up:
- CloudWatch for AWS monitoring
- Docker monitoring tools
- Application performance monitoring (APM)

## 🔄 CI/CD Integration

### Updated Flask Entry Point
The application now uses `backend/run.py` as the Flask entry point instead of `app.py`. This change improves:
- **Reliability**: Better error handling and startup process
- **Testing**: Flask test client integration for CI/CD
- **Health Checks**: Improved endpoint validation

### CI/CD Pipeline
The GitHub Actions workflow now:
- Tests Flask app creation with `create_app('testing')`
- Uses Flask test client for endpoint testing
- Validates all API endpoints without server startup
- Provides better error reporting and debugging

### Deployment Validation
The deployment scripts now include:
- Flask entry point verification (`backend/run.py` exists)
- Enhanced health check monitoring
- Retry logic for service startup
- Better error logging and debugging

### Pre-deployment Validation
Use `./deploy/validate-deployment.sh` to:
- Verify all required files exist
- Test Flask app creation
- Validate Docker configuration
- Check environment setup
- Ensure deployment readiness

## 🚀 Lightweight Deployment Optimizations

### System Cleanup
The deployment scripts automatically perform comprehensive cleanup for lightweight EC2 instances:
- **Docker Resources**: Removes all containers, images, volumes, and networks
- **System Packages**: Cleans package cache and removes unnecessary packages
- **Log Files**: Removes old logs and journal entries
- **Temporary Files**: Cleans /tmp and /var/tmp directories
- **Kernel Cleanup**: Removes old kernel versions (keeps only current)

### Resource Limits
Containers are automatically configured with resource constraints:
- **Backend**: 512MB RAM, 0.5 CPU cores
- **Frontend**: 256MB RAM, 0.3 CPU cores  
- **Celery Worker**: 256MB RAM, 0.3 CPU cores
- **Redis**: 128MB RAM, 0.2 CPU cores

### Docker Optimizations
- **BuildKit**: Enabled for faster, more efficient builds
- **Parallel Builds**: Multiple images built simultaneously
- **Log Rotation**: Automatic log cleanup (10MB max, 3 files max)
- **Storage Driver**: Uses overlay2 for better performance
- **Daily Cleanup**: Automatic cron job for resource cleanup

### Performance Monitoring
- **Disk Space**: Monitored before and after deployment
- **Resource Usage**: Container CPU and memory usage displayed
- **Docker Stats**: Real-time resource monitoring available 