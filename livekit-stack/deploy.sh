#!/bin/bash
# LiveKit Stack Deployment Script
# Run this on your VPS to deploy the stack

set -e  # Exit on error

echo "🚀 Starting LiveKit Stack Deployment..."
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root or with sudo${NC}" 
   exit 1
fi

# 1. Check prerequisites
echo ""
echo "📋 Step 1: Checking prerequisites..."
echo "------------------------------------"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Install Docker: curl -fsSL https://get.docker.com | sh"
    exit 1
fi
echo -e "${GREEN}✅ Docker is installed${NC}"

# Check Docker Compose
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed${NC}"
    echo "Install Docker Compose plugin: apt-get install docker-compose-plugin"
    exit 1
fi
echo -e "${GREEN}✅ Docker Compose is installed${NC}"

# 2. Check environment file
echo ""
echo "🔐 Step 2: Checking environment variables..."
echo "--------------------------------------------"

if [ ! -f .env ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please create .env from .env.sample and fill in your values"
    echo "cp .env.sample .env && nano .env"
    exit 1
fi
echo -e "${GREEN}✅ .env file found${NC}"

# Check required variables
required_vars=("LK_API_KEY" "LK_API_SECRET" "TURN_PASS")
for var in "${required_vars[@]}"; do
    if ! grep -q "^${var}=" .env || grep -q "${var}=your_" .env; then
        echo -e "${YELLOW}⚠️  Warning: ${var} may not be configured properly${NC}"
    fi
done

# 3. Configure firewall
echo ""
echo "🔥 Step 3: Configuring firewall..."
echo "----------------------------------"

# Check if ufw is installed
if command -v ufw &> /dev/null; then
    echo "Configuring UFW..."
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
    ufw allow 443/udp   # HTTP/3
    ufw allow 7880/tcp  # LiveKit
    ufw allow 3478/tcp  # STUN/TURN
    ufw allow 3478/udp  # STUN/TURN
    ufw allow 5349/tcp  # TURNS
    ufw allow 5349/udp  # TURNS
    ufw allow 50000:60000/udp  # RTC/Media
    echo -e "${GREEN}✅ UFW firewall configured${NC}"
else
    echo -e "${YELLOW}⚠️  UFW not found. Please configure firewall manually:${NC}"
    echo "   TCP: 22, 80, 443, 7880, 3478, 5349"
    echo "   UDP: 443, 3478, 5349, 50000-60000"
fi

# 4. Update Coturn configuration with TURN password
echo ""
echo "🔧 Step 4: Updating Coturn configuration..."
echo "--------------------------------------------"

source .env
sed "s/REPLACE_WITH_TURN_PASSWORD/${TURN_PASS}/g" coturn.conf > coturn.conf.tmp
mv coturn.conf.tmp coturn.conf
echo -e "${GREEN}✅ Coturn configuration updated${NC}"

# 5. Pull Docker images
echo ""
echo "📦 Step 5: Pulling Docker images..."
echo "-----------------------------------"

docker compose pull
echo -e "${GREEN}✅ Docker images pulled${NC}"

# 6. Stop existing containers (if any)
echo ""
echo "🛑 Step 6: Stopping existing containers..."
echo "------------------------------------------"

docker compose down 2>/dev/null || true
echo -e "${GREEN}✅ Existing containers stopped${NC}"

# 7. Start Caddy first to generate certificates
echo ""
echo "🔐 Step 7: Generating SSL certificates..."
echo "-----------------------------------------"

echo "Starting Caddy to obtain Let's Encrypt certificates..."
docker compose up -d caddy
sleep 10  # Wait for certificate generation

# Check if certificates were generated
if docker compose exec caddy test -f /data/caddy/certificates/acme-v02.api.letsencrypt.org-directory/rtc.pizoo.app/rtc.pizoo.app.crt; then
    echo -e "${GREEN}✅ SSL certificates generated${NC}"
    
    # Copy certificates to shared volume
    docker compose exec caddy sh -c "cp /data/caddy/certificates/acme-v02.api.letsencrypt.org-directory/rtc.pizoo.app/rtc.pizoo.app.crt /certs/cert.pem"
    docker compose exec caddy sh -c "cp /data/caddy/certificates/acme-v02.api.letsencrypt.org-directory/rtc.pizoo.app/rtc.pizoo.app.key /certs/key.pem"
else
    echo -e "${RED}❌ SSL certificate generation failed${NC}"
    echo "Please check:"
    echo "  1. DNS points rtc.pizoo.app to this server's IP"
    echo "  2. Port 80 and 443 are accessible"
    echo "  3. Caddy logs: docker compose logs caddy"
    exit 1
fi

# 8. Start all services
echo ""
echo "🚀 Step 8: Starting all services..."
echo "-----------------------------------"

docker compose up -d
echo -e "${GREEN}✅ All services started${NC}"

# 9. Wait for services to be ready
echo ""
echo "⏳ Step 9: Waiting for services to be ready..."
echo "----------------------------------------------"

sleep 15

# 10. Health checks
echo ""
echo "🏥 Step 10: Running health checks..."
echo "------------------------------------"

# Check Caddy
if curl -s -f https://rtc.pizoo.app/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Caddy is healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Caddy health check failed${NC}"
fi

# Check LiveKit
if docker compose ps livekit | grep -q "Up"; then
    echo -e "${GREEN}✅ LiveKit is running${NC}"
else
    echo -e "${RED}❌ LiveKit is not running${NC}"
fi

# Check Coturn
if docker compose ps coturn | grep -q "Up"; then
    echo -e "${GREEN}✅ Coturn is running${NC}"
else
    echo -e "${RED}❌ Coturn is not running${NC}"
fi

# Check Redis
if docker compose ps redis | grep -q "Up"; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${YELLOW}⚠️  Redis is not running (optional service)${NC}"
fi

# 11. Display status
echo ""
echo "========================================"
echo "✅ Deployment Complete!"
echo "========================================"
echo ""
echo "📊 Service Status:"
docker compose ps
echo ""
echo "🌐 Access URLs:"
echo "   LiveKit WSS: wss://rtc.pizoo.app"
echo "   Health Check: https://rtc.pizoo.app/health"
echo ""
echo "🔑 Credentials:"
echo "   API Key: ${LK_API_KEY}"
echo "   TURN User: ${TURN_USER}"
echo ""
echo "📝 Next Steps:"
echo "   1. Update your backend .env:"
echo "      LIVEKIT_URL=wss://rtc.pizoo.app"
echo "      LIVEKIT_API_KEY=${LK_API_KEY}"
echo "      LIVEKIT_API_SECRET=<same_as_LK_API_SECRET>"
echo ""
echo "   2. Restart your backend:"
echo "      sudo supervisorctl restart backend"
echo ""
echo "   3. Test video call from your app"
echo ""
echo "📖 Useful Commands:"
echo "   View logs: docker compose logs -f"
echo "   Restart: docker compose restart"
echo "   Stop: docker compose stop"
echo "   Status: docker compose ps"
echo ""
echo "🔧 Troubleshooting:"
echo "   If issues occur, check logs:"
echo "   - Caddy: docker compose logs caddy"
echo "   - LiveKit: docker compose logs livekit"
echo "   - Coturn: docker compose logs coturn"
echo ""
