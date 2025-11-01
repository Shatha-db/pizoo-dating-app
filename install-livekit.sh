#!/bin/bash
#########################################
# LiveKit Automated Installation Script
# For Hetzner VPS - Ubuntu 24.04
# Run as: sudo bash install-livekit.sh
#########################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "==========================================="
echo "   LiveKit Server Auto-Installation"
echo "   Server: Hetzner VPS (116.203.90.124)"
echo "   OS: Ubuntu 24.04"
echo "==========================================="
echo -e "${NC}"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}❌ This script must be run as root${NC}"
   echo "Run: sudo bash install-livekit.sh"
   exit 1
fi

echo ""
echo -e "${GREEN}Step 1: System Update${NC}"
echo "--------------------------------------"
apt update && apt upgrade -y
echo -e "${GREEN}✅ System updated${NC}"

echo ""
echo -e "${GREEN}Step 2: Install Docker${NC}"
echo "--------------------------------------"
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo -e "${GREEN}✅ Docker installed${NC}"
else
    echo -e "${GREEN}✅ Docker already installed${NC}"
fi

echo ""
echo -e "${GREEN}Step 3: Install Docker Compose${NC}"
echo "--------------------------------------"
if ! command -v docker compose &> /dev/null; then
    echo "Installing Docker Compose..."
    apt install -y docker-compose-plugin
    echo -e "${GREEN}✅ Docker Compose installed${NC}"
else
    echo -e "${GREEN}✅ Docker Compose already installed${NC}"
fi

echo ""
echo -e "${GREEN}Step 4: Configure Firewall (UFW)${NC}"
echo "--------------------------------------"
apt install -y ufw

# Allow SSH first (important!)
ufw allow 22/tcp

# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 443/udp

# Allow LiveKit
ufw allow 7880:7881/tcp
ufw allow 7880:7881/udp

# Allow TURN/STUN
ufw allow 3478/tcp
ufw allow 3478/udp
ufw allow 5349/tcp
ufw allow 5349/udp

# Allow RTC ports
ufw allow 50000:60000/udp

# Enable firewall (non-interactive)
echo "y" | ufw enable

ufw status
echo -e "${GREEN}✅ Firewall configured${NC}"

echo ""
echo -e "${GREEN}Step 5: Generate LiveKit Credentials${NC}"
echo "--------------------------------------"

# Generate secure credentials
LK_API_KEY=$(openssl rand -hex 16)
LK_API_SECRET=$(openssl rand -base64 32)
TURN_USER="pizoo"
TURN_PASS=$(openssl rand -base64 24)
REDIS_PASS=$(openssl rand -base64 32)

echo ""
echo -e "${YELLOW}=========================================${NC}"
echo -e "${YELLOW}IMPORTANT: SAVE THESE CREDENTIALS!${NC}"
echo -e "${YELLOW}=========================================${NC}"
echo ""
echo -e "${GREEN}LiveKit API Key:${NC}     $LK_API_KEY"
echo -e "${GREEN}LiveKit API Secret:${NC}  $LK_API_SECRET"
echo -e "${GREEN}TURN User:${NC}           $TURN_USER"
echo -e "${GREEN}TURN Password:${NC}       $TURN_PASS"
echo -e "${GREEN}Redis Password:${NC}      $REDIS_PASS"
echo ""
echo -e "${YELLOW}=========================================${NC}"
echo ""

# Save credentials to file
cat > /root/livekit-credentials.txt << EOF
LiveKit Credentials - $(date)
========================================
Server IP: 116.203.90.124
LiveKit URL: wss://116.203.90.124:7880

API Key: $LK_API_KEY
API Secret: $LK_API_SECRET
TURN User: $TURN_USER
TURN Password: $TURN_PASS
Redis Password: $REDIS_PASS

IMPORTANT: Store these securely!
========================================
EOF

chmod 600 /root/livekit-credentials.txt
echo -e "${GREEN}✅ Credentials saved to: /root/livekit-credentials.txt${NC}"

echo ""
echo -e "${GREEN}Step 6: Create LiveKit Directory${NC}"
echo "--------------------------------------"
mkdir -p /opt/livekit
cd /opt/livekit

echo ""
echo -e "${GREEN}Step 7: Create Docker Compose Configuration${NC}"
echo "--------------------------------------"

# Create .env file
cat > .env << EOF
# LiveKit Configuration
LK_API_KEY=$LK_API_KEY
LK_API_SECRET=$LK_API_SECRET
TURN_USER=$TURN_USER
TURN_PASS=$TURN_PASS
REDIS_PASSWORD=$REDIS_PASS
SERVER_IP=116.203.90.124
EOF

chmod 600 .env

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF_COMPOSE'
version: '3.8'

services:
  livekit:
    image: livekit/livekit-server:latest
    container_name: livekit-server
    restart: unless-stopped
    ports:
      - "7880:7880"
      - "7881:7881/udp"
      - "50000-60000:50000-60000/udp"
    environment:
      - LIVEKIT_KEYS=${LK_API_KEY}:${LK_API_SECRET}
    command: >
      --config /etc/livekit.yaml
    volumes:
      - ./livekit.yaml:/etc/livekit.yaml
      - livekit_data:/data
    networks:
      - livekit-net
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:7880/"]
      interval: 30s
      timeout: 10s
      retries: 3

  coturn:
    image: coturn/coturn:latest
    container_name: coturn-server
    restart: unless-stopped
    network_mode: host
    volumes:
      - ./turnserver.conf:/etc/coturn/turnserver.conf:ro
    command: -c /etc/coturn/turnserver.conf

  redis:
    image: redis:7-alpine
    container_name: redis-server
    restart: unless-stopped
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - livekit-net

networks:
  livekit-net:
    driver: bridge

volumes:
  livekit_data:
  redis_data:
EOF_COMPOSE

echo -e "${GREEN}✅ Docker Compose configuration created${NC}"

echo ""
echo -e "${GREEN}Step 8: Create LiveKit Configuration${NC}"
echo "--------------------------------------"

cat > livekit.yaml << EOF
port: 7880
bind_addresses:
  - "0.0.0.0"

rtc:
  port_range_start: 50000
  port_range_end: 60000
  use_external_ip: true
  tcp_port: 7881

keys:
  ${LK_API_KEY}: ${LK_API_SECRET}

turn:
  enabled: true
  domain: 116.203.90.124
  tls_port: 5349
  udp_port: 3478
  username: ${TURN_USER}
  password: ${TURN_PASS}

logging:
  level: info
  sample: false

room:
  auto_create: true
  empty_timeout: 300
  max_participants: 10

EOF

echo -e "${GREEN}✅ LiveKit configuration created${NC}"

echo ""
echo -e "${GREEN}Step 9: Create Coturn Configuration${NC}"
echo "--------------------------------------"

cat > turnserver.conf << EOF
# Coturn Configuration for LiveKit
listening-port=3478
tls-listening-port=5349
listening-ip=0.0.0.0
relay-ip=0.0.0.0

external-ip=116.203.90.124

min-port=50000
max-port=60000

realm=pizoo-turn
server-name=pizoo-turn

lt-cred-mech
user=${TURN_USER}:${TURN_PASS}

fingerprint
log-file=stdout
verbose

no-multicast-peers
no-loopback-peers
no-cli

prod
no-software-attribute
EOF

echo -e "${GREEN}✅ Coturn configuration created${NC}"

echo ""
echo -e "${GREEN}Step 10: Start Services${NC}"
echo "--------------------------------------"

docker compose pull
docker compose up -d

echo ""
echo -e "${GREEN}✅ Services started${NC}"

echo ""
echo -e "${GREEN}Step 11: Wait for Services (30 seconds)${NC}"
echo "--------------------------------------"
sleep 30

echo ""
echo -e "${GREEN}Step 12: Health Check${NC}"
echo "--------------------------------------"

# Check if containers are running
if docker ps | grep -q livekit-server; then
    echo -e "${GREEN}✅ LiveKit server is running${NC}"
else
    echo -e "${RED}❌ LiveKit server failed to start${NC}"
    docker compose logs livekit
fi

if docker ps | grep -q coturn-server; then
    echo -e "${GREEN}✅ Coturn server is running${NC}"
else
    echo -e "${RED}❌ Coturn server failed to start${NC}"
    docker compose logs coturn
fi

if docker ps | grep -q redis-server; then
    echo -e "${GREEN}✅ Redis server is running${NC}"
else
    echo -e "${RED}❌ Redis server failed to start${NC}"
    docker compose logs redis
fi

# Test LiveKit endpoint
if curl -s -f http://localhost:7880/ > /dev/null; then
    echo -e "${GREEN}✅ LiveKit HTTP endpoint responding${NC}"
else
    echo -e "${YELLOW}⚠️  LiveKit HTTP endpoint not responding yet${NC}"
fi

echo ""
echo -e "${BLUE}==========================================="
echo "   Installation Complete!"
echo "==========================================="
echo -e "${NC}"
echo ""
echo -e "${GREEN}📊 Service Status:${NC}"
docker compose ps
echo ""
echo -e "${GREEN}🌐 Connection Information:${NC}"
echo ""
echo "  LiveKit WSS URL:    ws://116.203.90.124:7880"
echo "  LiveKit HTTP:       http://116.203.90.124:7880"
echo "  TURN Server:        turn:116.203.90.124:3478"
echo ""
echo -e "${GREEN}🔑 Credentials (also saved in /root/livekit-credentials.txt):${NC}"
echo ""
echo "  API Key:            $LK_API_KEY"
echo "  API Secret:         $LK_API_SECRET"
echo "  TURN User:          $TURN_USER"
echo "  TURN Password:      $TURN_PASS"
echo ""
echo -e "${YELLOW}⚠️  IMPORTANT SECURITY NOTES:${NC}"
echo ""
echo "1. Save credentials securely from: /root/livekit-credentials.txt"
echo "2. For production, set up proper domain and SSL:"
echo "   - Point domain to: 116.203.90.124"
echo "   - Use Caddy or Nginx for SSL termination"
echo "   - Then use: wss://your-domain.com"
echo ""
echo -e "${GREEN}📝 Next Steps:${NC}"
echo ""
echo "1. Test connection:"
echo "   curl http://116.203.90.124:7880/"
echo ""
echo "2. Update your Pizoo backend .env:"
echo "   LIVEKIT_URL=ws://116.203.90.124:7880"
echo "   LIVEKIT_API_KEY=$LK_API_KEY"
echo "   LIVEKIT_API_SECRET=$LK_API_SECRET"
echo ""
echo "3. Restart backend:"
echo "   sudo supervisorctl restart backend"
echo ""
echo "4. View logs:"
echo "   cd /opt/livekit && docker compose logs -f"
echo ""
echo -e "${GREEN}✅ Installation script completed successfully!${NC}"
echo ""
