# AWS EC2 Deployment Summary

## 🌐 Port Configuration
- **Frontend**: Port 3001 (React)
- **Backend**: Port 8001 (Flask API)
- **Nginx**: Port 80 (Reverse proxy)

## 🚀 Quick Deployment

### 1. Server Setup
```bash
# Setup the server (run once)
chmod +x deploy/ec2-setup.sh
./deploy/ec2-setup.sh

# Deploy the application
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```

### 2. Access URLs
- **Frontend**: `http://your-ec2-ip`
- **Backend API**: `http://your-ec2-ip/api`
- **Swagger UI**: `http://your-ec2-ip/api/docs`
- **Health Check**: `http://your-ec2-ip/health`

### 3. Direct Port Access (if needed)
- **Frontend**: `http://your-ec2-ip:3001`
- **Backend**: `http://your-ec2-ip:8001`

## 🔒 Security Group Requirements
Make sure your EC2 security group allows:
- Port 22 (SSH)
- Port 80 (HTTP)
- Port 3001 (Frontend)
- Port 8001 (Backend)

## 🔧 Management Commands
```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop services
docker-compose down

# Update application
./deploy/deploy.sh
```

## 🆘 Troubleshooting
```bash
# Check if containers are running
docker-compose ps

# Check nginx status
sudo systemctl status nginx

# Check docker status
sudo systemctl status docker
``` 