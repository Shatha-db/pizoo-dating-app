#!/bin/bash
# LiveKit Stack Testing Script
# Tests all components of the self-hosted stack

set -e

echo "🧪 LiveKit Stack Testing"
echo "========================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DOMAIN="${DOMAIN:-rtc.pizoo.app}"
PASSED=0
FAILED=0

# Test function
test_component() {
    local name=$1
    local command=$2
    
    echo -n "Testing $name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}❌ FAILED${NC}"
        ((FAILED++))
        return 1
    fi
}

# 1. DNS Resolution
echo "1️⃣ DNS Resolution"
echo "----------------"
test_component "DNS A Record" "dig +short $DOMAIN | grep -E '^[0-9.]+$'"
echo ""

# 2. Port Accessibility
echo "2️⃣ Port Accessibility"
echo "--------------------"
test_component "HTTP (80)" "timeout 5 bash -c '</dev/tcp/$DOMAIN/80'"
test_component "HTTPS (443)" "timeout 5 bash -c '</dev/tcp/$DOMAIN/443'"
test_component "STUN/TURN (3478)" "timeout 5 bash -c '</dev/udp/$DOMAIN/3478'"
echo ""

# 3. SSL Certificate
echo "3️⃣ SSL Certificate"
echo "-----------------"
test_component "SSL Certificate Valid" "curl -sS --connect-timeout 5 https://$DOMAIN/health"
test_component "Certificate Not Expired" "echo | openssl s_client -servername $DOMAIN -connect $DOMAIN:443 2>/dev/null | openssl x509 -noout -checkend 86400"
echo ""

# 4. Docker Services
echo "4️⃣ Docker Services"
echo "-----------------"
test_component "Caddy Running" "docker compose ps caddy | grep -q 'Up'"
test_component "LiveKit Running" "docker compose ps livekit | grep -q 'Up'"
test_component "Coturn Running" "docker compose ps coturn | grep -q 'Up'"
test_component "Redis Running" "docker compose ps redis | grep -q 'Up'"
echo ""

# 5. Service Health
echo "5️⃣ Service Health"
echo "----------------"
test_component "LiveKit Health" "curl -sS -f https://$DOMAIN/health"
test_component "Caddy Health" "docker compose exec caddy wget -q --spider http://localhost:2019/metrics"
test_component "Redis Health" "docker compose exec redis redis-cli -a \$REDIS_PASSWORD ping | grep -q PONG"
echo ""

# 6. WebSocket Connection
echo "6️⃣ WebSocket Connection"
echo "----------------------"
if command -v wscat &> /dev/null; then
    test_component "WebSocket Connection" "timeout 5 wscat -c wss://$DOMAIN"
else
    echo -e "${YELLOW}⚠️  wscat not installed (npm install -g wscat)${NC}"
fi
echo ""

# 7. STUN Server
echo "7️⃣ STUN Server"
echo "-------------"
if command -v stunclient &> /dev/null; then
    test_component "STUN Response" "timeout 5 stunclient $DOMAIN 3478"
else
    echo -e "${YELLOW}⚠️  stunclient not installed${NC}"
fi
echo ""

# 8. Firewall Rules
echo "8️⃣ Firewall Rules"
echo "----------------"
test_component "UFW Enabled" "sudo ufw status | grep -q 'Status: active'"
test_component "Port 443 Allowed" "sudo ufw status | grep -q '443'"
test_component "UDP 50000:60000 Allowed" "sudo ufw status | grep -q '50000:60000/udp'"
echo ""

# 9. Resource Usage
echo "9️⃣ Resource Usage"
echo "----------------"
echo "CPU Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
echo ""

# 10. Logs Check
echo "🔟 Recent Logs"
echo "-------------"
echo "Caddy (last 5 lines):"
docker compose logs --tail=5 caddy 2>/dev/null | grep -v "caddy_data" || echo "No recent logs"
echo ""
echo "LiveKit (last 5 lines):"
docker compose logs --tail=5 livekit 2>/dev/null | grep -v "livekit_data" || echo "No recent logs"
echo ""

# Summary
echo "========================"
echo "📊 Test Summary"
echo "========================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo "Your LiveKit stack is ready for production use."
    echo ""
    echo "Next steps:"
    echo "1. Update backend .env with:"
    echo "   LIVEKIT_URL=wss://$DOMAIN"
    echo "   LIVEKIT_API_KEY=<from your .env>"
    echo "   LIVEKIT_API_SECRET=<from your .env>"
    echo ""
    echo "2. Restart backend:"
    echo "   sudo supervisorctl restart backend"
    echo ""
    echo "3. Test video call from your app"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check service logs: docker compose logs"
    echo "2. Verify DNS: dig $DOMAIN"
    echo "3. Test ports: telnet $DOMAIN 443"
    echo "4. Review README.md troubleshooting section"
    exit 1
fi
