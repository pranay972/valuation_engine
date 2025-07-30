# AWS EC2 Deployment Guide

This guide will help you deploy the Financial Valuation Application to AWS EC2.

## Prerequisites

- AWS EC2 instance (Amazon Linux 2 recommended)
- Security group with ports 80 (HTTP), 22 (SSH), 3001, and 8001 open
- SSH access to your EC2 instance
- **Note**: This deployment uses ports 3001 (frontend) and 8001 (backend) to avoid conflicts with existing services

## Step 1: Initial EC2 Setup

1. **Connect to your EC2 instance:**
   ```bash
   ssh -i your-key.pem ec2-user@your-ec2-public-ip
   ```

2. **Run the EC2 setup script:**
   ```bash
   # Download and run the setup script
   curl -sSL https://raw.githubusercontent.com/your-repo/financial-valuation-app/main/deploy/ec2-setup.sh | bash
   ```

   Or if you have the files locally:
   ```bash
   chmod +x deploy/ec2-setup.sh
   ./deploy/ec2-setup.sh
   ```

## Step 2: Deploy the Application

1. **Clone your repository:**
   ```bash
   cd /home/ec2-user
   git clone https://github.com/your-username/financial-valuation-app.git
   cd financial-valuation-app
   ```

2. **Run the deployment:**
   ```bash
   chmod +x deploy/deploy.sh
   ./deploy/deploy.sh
   ```

## Step 3: Verify Deployment

After deployment, you should be able to access:

- **Frontend**: `http://your-ec2-public-ip`
- **Backend API**: `http://your-ec2-public-ip/api`
- **Swagger UI**: `http://your-ec2-public-ip/api/docs`
- **Health Check**: `http://your-ec2-public-ip/health`

## Management Commands

### View Logs
```bash
cd /home/ec2-user/financial-valuation-app
docker-compose logs -f
```

### Restart Services
```bash
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Update Application
```bash
./deploy/deploy.sh
```

### Check Status
```bash
docker-compose ps
```

## Troubleshooting

### Check Docker Status
```bash
sudo systemctl status docker
```

### Check Nginx Status
```bash
sudo systemctl status nginx
```

### View Nginx Logs
```bash
sudo tail -f /var/log/nginx/error.log
```

### Check Application Logs
```bash
docker-compose logs backend
docker-compose logs frontend
```

### Restart Everything
```bash
sudo systemctl restart docker
sudo systemctl restart nginx
docker-compose down && docker-compose up -d
```

## Security Considerations

1. **Update Security Groups**: Ensure only necessary ports are open
2. **Use HTTPS**: Consider setting up SSL/TLS certificates
3. **Regular Updates**: Keep the system and Docker images updated
4. **Backup**: Consider setting up automated backups

## Environment Variables

You can customize the deployment by setting environment variables in the `docker-compose.yml` file:

```yaml
environment:
  - FLASK_ENV=production
  - REACT_APP_API_URL=http://your-domain.com/api
```

## Monitoring

Consider setting up monitoring tools like:
- CloudWatch for AWS monitoring
- Docker monitoring tools
- Application performance monitoring (APM)

## Backup and Recovery

1. **Backup Docker volumes:**
   ```bash
   docker run --rm -v financial-valuation-app_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .
   ```

2. **Restore from backup:**
   ```bash
   docker run --rm -v financial-valuation-app_data:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /data
   ```

## Support

If you encounter issues:
1. Check the logs: `docker-compose logs`
2. Verify network connectivity
3. Check AWS security groups
4. Review the troubleshooting section above 