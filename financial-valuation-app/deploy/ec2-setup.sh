#!/bin/bash

# EC2 Setup Script for Financial Valuation Application
# This script should be run on a fresh EC2 instance

set -e

echo "🚀 Setting up EC2 instance for Financial Valuation Application..."

# Clean up system for lightweight deployment
echo "🧹 Cleaning up system for lightweight deployment..."

# Remove unnecessary packages
echo "🗑️  Removing unnecessary packages..."
sudo yum remove -y postfix sendmail rsh rlogin telnet talk 2>/dev/null || true
sudo yum remove -y cups cups-libs cups-client 2>/dev/null || true
sudo yum remove -y avahi avahi-autoipd 2>/dev/null || true
sudo yum remove -y abrt abrt-addon-ccpp abrt-addon-python abrt-addon-python 2>/dev/null || true

# Clean up package cache
echo "🧹 Cleaning up package cache..."
sudo yum clean all
sudo rm -rf /var/cache/yum
sudo rm -rf /var/cache/dnf

# Clean up log files
echo "🧹 Cleaning up old log files..."
sudo find /var/log -name "*.log" -type f -mtime +1 -delete 2>/dev/null || true
sudo find /var/log -name "*.gz" -type f -mtime +1 -delete 2>/dev/null || true

# Clean up temporary files
echo "🧹 Cleaning up temporary files..."
sudo rm -rf /tmp/*
sudo rm -rf /var/tmp/*

# Show available disk space before setup
echo "💾 Available disk space before setup:"
df -h /

# Update system packages
echo "📦 Updating system packages..."
sudo yum update -y

# Install Docker
echo "🐳 Installing Docker..."
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Configure Docker for lightweight instances
echo "⚙️  Configuring Docker for lightweight instances..."
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "default-ulimits": {
    "nofile": {
      "Hard": 64000,
      "Name": "nofile",
      "Soft": 64000
    }
  }
}
EOF

# Restart Docker with new configuration
sudo systemctl restart docker

# Install Docker Compose
echo "📋 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
echo "📚 Installing Git..."
sudo yum install -y git

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /home/ec2-user/financial-valuation-app
cd /home/ec2-user/financial-valuation-app

# Create nginx configuration for reverse proxy
echo "🌐 Setting up Nginx..."
sudo yum install -y nginx

# Create nginx config
sudo tee /etc/nginx/conf.d/financial-valuation.conf > /dev/null <<EOF
server {
    listen 80;
    server_name _;

    # Frontend
    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }

    # Swagger UI
    location /api/docs {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Start nginx
sudo systemctl enable nginx
sudo systemctl start nginx

# Create deployment script
echo "📝 Creating deployment script..."
tee deploy.sh > /dev/null <<'EOF'
#!/bin/bash

set -e

echo "🚀 Deploying Financial Valuation Application..."

# Check if backend run.py exists (Flask entry point)
if [ ! -f "backend/run.py" ]; then
    echo "❌ Error: backend/run.py not found. Flask entry point is missing!"
    exit 1
fi

# Pull latest changes
git pull origin main

# Build and start containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Test backend health endpoint
echo "🔍 Testing backend health endpoint..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s --max-time 10 http://localhost:8001/health > /dev/null; then
        echo "✅ Backend health check passed!"
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "⏳ Backend not ready yet (attempt $RETRY_COUNT/$MAX_RETRIES)..."
        sleep 5
    fi
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "❌ Backend health check failed after $MAX_RETRIES attempts"
    docker-compose logs backend
    exit 1
fi

echo "✅ Deployment completed!"
echo "🌐 Application should be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "📊 Swagger UI: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/api/docs"
echo "🔍 Health Check: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/health"
echo "🌸 Celery Flower: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):5555"
EOF

chmod +x deploy.sh

# Create systemd service for auto-start
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/financial-valuation.service > /dev/null <<EOF
[Unit]
Description=Financial Valuation Application
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/home/ec2-user/financial-valuation-app
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
User=ec2-user
Group=ec2-user

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable financial-valuation.service

# Optimize system for lightweight deployment
echo "⚙️  Optimizing system for lightweight deployment..."

# Configure log rotation
sudo tee /etc/logrotate.d/docker > /dev/null <<EOF
/var/lib/docker/containers/*/*.log {
    rotate 3
    daily
    compress
    size=10M
    missingok
    notifempty
    copytruncate
}
EOF

# Configure system limits
echo "ec2-user soft nofile 64000" | sudo tee -a /etc/security/limits.conf
echo "ec2-user hard nofile 64000" | sudo tee -a /etc/security/limits.conf

# Create cleanup cron job
echo "🕐 Setting up automatic cleanup cron job..."
sudo tee /etc/cron.daily/docker-cleanup > /dev/null <<'EOF'
#!/bin/bash
# Clean up Docker resources daily
docker system prune -af --volumes 2>/dev/null || true
docker image prune -af 2>/dev/null || true
docker container prune -f 2>/dev/null || true
docker volume prune -f 2>/dev/null || true
docker network prune -f 2>/dev/null || true

# Clean up old logs
find /var/log -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
find /var/log -name "*.gz" -type f -mtime +7 -delete 2>/dev/null || true

# Clean up temporary files
rm -rf /tmp/*
rm -rf /var/tmp/*
EOF

sudo chmod +x /etc/cron.daily/docker-cleanup

# Show final disk space
echo "💾 Available disk space after setup:"
df -h /

echo "✅ EC2 setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Clone your repository: git clone <your-repo-url> /home/ec2-user/financial-valuation-app"
echo "2. Run deployment: cd /home/ec2-user/financial-valuation-app && ./deploy.sh"
echo "3. Access your application at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "🔧 Useful commands:"
echo "- View logs: docker-compose logs -f"
echo "- Restart: docker-compose restart"
echo "- Stop: docker-compose down"
echo "- Update: git pull && docker-compose up -d --build" 