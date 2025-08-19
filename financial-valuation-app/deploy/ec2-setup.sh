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

# Use Docker with default configuration (no custom daemon.json)
echo "✅ Using Docker with default configuration..."
if [ -f "/etc/docker/daemon.json" ]; then
    echo "🗑️  Removing existing Docker daemon configuration..."
    sudo rm -f /etc/docker/daemon.json
fi

# Ensure Docker is running with default settings
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

# Create initial HTTP-only nginx config (will be updated with SSL later)
echo "📝 Creating initial Nginx site configuration..."
sudo tee /etc/nginx/conf.d/financial-valuation.conf > /dev/null <<'SITE_CONFIG'
server {
    listen 80;
    server_name _;

    # Frontend (React on port 3001)
    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API (Flask on port 8001)
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Swagger or API Docs
    location /api/docs {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
SITE_CONFIG

# Create nginx configuration validation script
echo "🔍 Creating Nginx validation script..."
sudo tee /usr/local/bin/validate-nginx > /dev/null <<'VALIDATION_SCRIPT'
#!/bin/bash

# Nginx Configuration Validation Script
set -e

echo "🔍 Validating Nginx configuration..."

# Test configuration syntax
if sudo nginx -t; then
    echo "✅ Nginx configuration syntax is valid"
else
    echo "❌ Nginx configuration syntax is invalid"
    exit 1
fi

# Check if nginx is running
if sudo systemctl is-active --quiet nginx; then
    echo "✅ Nginx service is running"
else
    echo "⚠️  Nginx service is not running"
fi

# Test basic connectivity
if curl -s --max-time 5 http://localhost > /dev/null 2>&1; then
    echo "✅ Nginx is responding on port 80"
else
    echo "❌ Nginx is not responding on port 80"
fi

# Test health endpoint
if curl -s --max-time 5 http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Health check endpoint is working"
else
    echo "❌ Health check endpoint is not working"
fi

# Check upstream connectivity
echo "🔍 Checking upstream services..."
if curl -s --max-time 5 http://localhost:3001 > /dev/null 2>&1; then
    echo "✅ Frontend service (port 3001) is accessible"
else
    echo "❌ Frontend service (port 3001) is not accessible"
fi

if curl -s --max-time 5 http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Backend service (port 8001) is accessible"
else
    echo "❌ Backend service (port 8001) is not accessible"
fi

echo "✅ Nginx validation completed!"
VALIDATION_SCRIPT

sudo chmod +x /usr/local/bin/validate-nginx

# Create nginx monitoring script
echo "📊 Creating Nginx monitoring script..."
sudo tee /usr/local/bin/monitor-nginx > /dev/null <<'MONITOR_SCRIPT'
#!/bin/bash

# Nginx Monitoring Script
echo "📊 Nginx Status Report"
echo "======================"

# Service status
echo "🔧 Service Status:"
sudo systemctl status nginx --no-pager -l | head -10

# Process info
echo ""
echo "🔄 Process Information:"
ps aux | grep nginx | grep -v grep

# Connection status
echo ""
echo "🌐 Connection Status:"
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :8080

# Error log summary
echo ""
echo "❌ Recent Errors (last 10):"
sudo tail -10 /var/log/nginx/error.log 2>/dev/null || echo "No error log found"

# Access log summary
echo ""
echo "📝 Recent Access (last 5):"
sudo tail -5 /var/log/nginx/access.log 2>/dev/null || echo "No access log found"

# Upstream health
echo ""
echo "🔍 Upstream Health:"
echo "Frontend (3001): $(curl -s --max-time 2 http://localhost:3001 > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy")"
echo "Backend (8001): $(curl -s --max-time 2 http://localhost:8001/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy")"
MONITOR_SCRIPT

sudo chmod +x /usr/local/bin/monitor-nginx

# Start nginx
echo "🚀 Starting Nginx service..."
sudo systemctl enable nginx
sudo systemctl start nginx

# Wait for nginx to start
sleep 3

# Validate nginx configuration
echo "🔍 Validating Nginx configuration..."
if /usr/local/bin/validate-nginx; then
    echo "✅ Nginx setup completed successfully!"
else
    echo "⚠️  Nginx setup completed with warnings"
fi

# Create SSL setup script using Certbot via Docker
echo "🔐 Creating SSL setup script..."
tee setup-ssl.sh > /dev/null <<'EOF'
#!/bin/bash

# SSL Setup Script using Certbot via Docker
# This script should be run after your domain is pointing to this EC2 instance

set -e

DOMAIN=${1:-"valuationengine.app"}
EMAIL=${2:-"admin@valuationengine.app"}

if [ -z "$DOMAIN" ]; then
    echo "❌ Error: Domain name is required"
    echo "Usage: ./setup-ssl.sh <domain> [email]"
    echo "Example: ./setup-ssl.sh valuationengine.app admin@example.com"
    exit 1
fi

echo "🔐 Setting up SSL for domain: $DOMAIN"
echo "📧 Using email: $EMAIL"

# Check if domain is pointing to this server
echo "🔍 Checking if domain $DOMAIN points to this server..."
CURRENT_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
DOMAIN_IP=$(dig +short $DOMAIN | head -1)

if [ "$CURRENT_IP" != "$DOMAIN_IP" ]; then
    echo "⚠️  Warning: Domain $DOMAIN ($DOMAIN_IP) may not be pointing to this server ($CURRENT_IP)"
    echo "   Please ensure your DNS is configured correctly before proceeding"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create directories for SSL certificates
echo "📁 Creating SSL certificate directories..."
sudo mkdir -p /etc/letsencrypt
sudo mkdir -p /etc/letsencrypt/live/$DOMAIN

# Stop nginx temporarily to free up port 80
echo "🛑 Stopping Nginx temporarily..."
sudo systemctl stop nginx

# Run Certbot via Docker to obtain SSL certificates
echo "🔑 Obtaining SSL certificates using Certbot..."
sudo docker run --rm \
    -v /etc/letsencrypt:/etc/letsencrypt \
    -v /var/lib/letsencrypt:/var/lib/letsencrypt \
    -p 80:80 \
    -p 443:443 \
    certbot/certbot certonly \
    --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN,www.$DOMAIN

# Verify certificates were created
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ] || [ ! -f "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ]; then
    echo "❌ SSL certificates were not created successfully"
    echo "   Please check the Certbot output above for errors"
    exit 1
fi

echo "✅ SSL certificates created successfully!"

# Update nginx configuration with SSL (keeping your existing structure)
echo "⚙️  Updating Nginx configuration with SSL..."
sudo tee /etc/nginx/conf.d/financial-valuation.conf > /dev/null <<NGINX_SSL
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name $DOMAIN www.$DOMAIN;

    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # Optional security hardening
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Frontend (React on port 3001)
    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Backend API (Flask on port 8001)
    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # Swagger or API Docs
    location /api/docs {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
NGINX_SSL

# Test nginx configuration
echo "🧪 Testing Nginx configuration..."
sudo nginx -t

# Start nginx with SSL configuration
echo "🚀 Starting Nginx with SSL configuration..."
sudo systemctl start nginx

# Create SSL renewal script
echo "🔄 Creating SSL renewal script..."
sudo tee /etc/cron.daily/renew-ssl > /dev/null <<'RENEW_SCRIPT'
#!/bin/bash
# Renew SSL certificates daily
echo "Renewing SSL certificates for $(date)" >> /var/log/ssl-renewal.log

docker run --rm \
    -v /etc/letsencrypt:/etc/letsencrypt \
    -v /var/lib/letsencrypt:/var/lib/letsencrypt \
    certbot/certbot renew --quiet

# Reload nginx if certificates were renewed
if [ $? -eq 0 ]; then
    echo "Certificates renewed successfully, reloading nginx" >> /var/log/ssl-renewal.log
    nginx -s reload
else
    echo "Certificate renewal failed" >> /var/log/ssl-renewal.log
fi
RENEW_SCRIPT

sudo chmod +x /etc/cron.daily/renew-ssl

# Test SSL setup
echo "🧪 Testing SSL setup..."
sleep 5

if curl -s --max-time 10 https://$DOMAIN > /dev/null 2>&1; then
    echo "✅ HTTPS is working correctly!"
else
    echo "⚠️  HTTPS test failed, but certificates are installed"
    echo "   This might be normal if containers aren't running yet"
fi

echo "✅ SSL setup completed!"
echo "🔐 Your application is now available at: https://$DOMAIN"
echo "🔄 SSL certificates will be automatically renewed daily"
echo "📋 To renew certificates manually:"
echo "   sudo docker run --rm -v /etc/letsencrypt:/etc/letsencrypt -v /var/lib/letsencrypt:/var/lib/letsencrypt certbot/certbot renew"
echo ""
echo "🔍 To check SSL certificate status:"
echo "   sudo docker run --rm -v /etc/letsencrypt:/etc/letsencrypt -v /var/lib/letsencrypt:/var/lib/letsencrypt certbot/certbot certificates"
EOF

chmod +x setup-ssl.sh

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

# Set environment variables for production deployment
echo "⚙️  Setting production environment variables..."
export FLASK_ENV=production
export SECRET_KEY=${SECRET_KEY:-production-secret-key-change-me}
export DATABASE_URL=${DATABASE_URL:-sqlite:///financial_valuation.db}
export DEV_DATABASE_URL=${DEV_DATABASE_URL:-sqlite:///financial_valuation.db}
export TEST_DATABASE_URL=${TEST_DATABASE_URL:-sqlite:///financial_valuation.db}

# Set frontend API URL for production (replace with your actual domain)
export REACT_APP_API_URL=${REACT_APP_URL:-https://$(curl -s http://169.254.169.254/latest/meta-data/public-hostname)/api}

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
echo ""
echo "🔐 To enable SSL (after your domain points to this server):"
echo "   ./setup-ssl.sh yourdomain.com your-email@example.com"
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

# Create quick fix script for immediate issues
echo "🔧 Creating quick fix script for Nginx issues..."
tee fix-nginx-now.sh > /dev/null <<'QUICK_FIX'
#!/bin/bash

# Quick Fix Script for Immediate Nginx Issues
echo "🔧 Quick fix for Nginx configuration issues..."

# Check current status
echo "📊 Current Nginx status:"
sudo systemctl status nginx --no-pager -l | head -5

# Option 1: Fix SSL configuration (if certificates exist)
if [ -f "/etc/letsencrypt/live/valuationengine.app/fullchain.pem" ]; then
    echo "🔐 SSL certificates found, fixing SSL configuration..."
    
    # Create working SSL config
    sudo tee /etc/nginx/conf.d/financial-valuation.conf > /dev/null <<'SSL_CONFIG'
server {
    listen 80;
    server_name valuationengine.app www.valuationengine.app;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name valuationengine.app www.valuationengine.app;

    ssl_certificate /etc/letsencrypt/live/valuationengine.app/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/valuationengine.app/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/docs {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
SSL_CONFIG

    echo "✅ SSL configuration created"
    
else
    echo "⚠️  No SSL certificates found, creating HTTP-only configuration..."
    
    # Create HTTP-only config
    sudo tee /etc/nginx/conf.d/financial-valuation.conf > /dev/null <<'HTTP_CONFIG'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/docs {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
HTTP_CONFIG

    echo "✅ HTTP configuration created"
fi

# Test configuration
echo "🧪 Testing Nginx configuration..."
if sudo nginx -t; then
    echo "✅ Configuration test passed!"
    
    # Restart Nginx
    echo "🚀 Restarting Nginx..."
    sudo systemctl restart nginx
    
    # Check status
    echo "📊 Nginx status:"
    sudo systemctl status nginx --no-pager -l | head -5
    
    echo "✅ Nginx fix completed!"
else
    echo "❌ Configuration test failed!"
    exit 1
fi
QUICK_FIX

chmod +x fix-nginx-now.sh

echo "✅ EC2 setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Clone your repository: git clone <your-repo-url> /home/ec2-user/financial-valuation-app"
echo "2. Run deployment: cd /home/ec2-user/financial-valuation-app && ./deploy.sh"
echo "3. Access your application at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo ""
echo "🔐 SSL Setup (after domain points to this server):"
echo "   ./setup-ssl.sh yourdomain.com your-email@example.com"
echo ""
echo "🔧 Quick Fix (if Nginx has issues):"
echo "   ./fix-nginx-now.sh"
echo ""
echo "🔧 Useful commands:"
echo "- View logs: docker-compose logs -f"
echo "- Restart: docker-compose restart"
echo "- Stop: docker-compose down"
echo "- Update: git pull && docker-compose up -d --build"
echo "- SSL renewal: sudo docker run --rm -v /etc/letsencrypt:/etc/letsencrypt -v /var/lib/letsencrypt:/var/lib/letsencrypt certbot/certbot renew"
echo "- Nginx validation: /usr/local/bin/validate-nginx"
echo "- Nginx monitoring: /usr/local/bin/monitor-nginx" 