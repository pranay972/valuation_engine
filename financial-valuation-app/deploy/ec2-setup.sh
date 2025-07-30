#!/bin/bash

# EC2 Setup Script for Financial Valuation Application
# This script should be run on a fresh EC2 instance

set -e

echo "🚀 Setting up EC2 instance for Financial Valuation Application..."

# Update system packages
echo "📦 Updating system packages..."
sudo yum update -y

# Install Docker
echo "🐳 Installing Docker..."
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

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

# Pull latest changes
git pull origin main

# Build and start containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d

echo "✅ Deployment completed!"
echo "🌐 Application should be available at: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)"
echo "📊 Swagger UI: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/api/docs"
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