# AWS EC2 Deployment Guide

Complete guide for deploying the Financial Valuation Application to AWS EC2.

## 📋 Prerequisites

- AWS EC2 instance (Amazon Linux 2 recommended)
- Security group with ports 80 (HTTP), 22 (SSH), 3001, and 8001 open
- SSH access to your EC2 instance

**Note**: Uses ports 3001 (frontend) and 8001 (backend) to avoid conflicts.

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

Customize deployment in `docker-compose.yml`:
```yaml
environment:
  - FLASK_ENV=production
  - REACT_APP_API_URL=http://your-domain.com/api
```

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