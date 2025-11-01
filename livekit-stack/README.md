# 🎥 LiveKit Self-Hosted Stack for Pizoo

Complete self-hosted LiveKit infrastructure with TURN server for production video/audio calling.

---

## 📋 Prerequisites

### Server Requirements:
- **VPS:** 2+ CPU cores, 4GB+ RAM, 20GB storage
- **OS:** Ubuntu 20.04/22.04 LTS or Debian 11+
- **Ports:** See firewall section below
- **Domain:** `rtc.pizoo.app` pointing to VPS public IP

### Software Requirements:
- Docker 20.10+
- Docker Compose 2.0+
- OpenSSL (for generating secrets)

---

## 🚀 Quick Start

### 1. Clone/Upload Files to VPS

```bash
# On your VPS
mkdir -p ~/pizoo-livekit
cd ~/pizoo-livekit

# Upload these files:
# - docker-compose.yml
# - Caddyfile
# - coturn.conf
# - .env.sample
# - deploy.sh
```

### 2. Generate Secrets

```bash
# API Key (short, alphanumeric)
export LK_API_KEY=$(openssl rand -hex 16)

# API Secret (long, strong)
export LK_API_SECRET=$(openssl rand -base64 32)

# TURN Password
export TURN_PASS=$(openssl rand -base64 24)

# Redis Password
export REDIS_PASSWORD=$(openssl rand -base64 32)

# Display generated secrets
echo "LK_API_KEY=$LK_API_KEY"
echo "LK_API_SECRET=$LK_API_SECRET"
echo "TURN_PASS=$TURN_PASS"
echo "REDIS_PASSWORD=$REDIS_PASSWORD"

# SAVE THESE SECURELY!
```

### 3. Configure Environment

```bash
# Copy sample env file
cp .env.sample .env

# Edit with your secrets
nano .env

# Fill in:
# - LK_API_KEY (from above)
# - LK_API_SECRET (from above)
# - TURN_PASS (from above)
# - REDIS_PASSWORD (from above)
```

### 4. Deploy

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
sudo ./deploy.sh
```

The script will:
- ✅ Check prerequisites
- ✅ Configure firewall
- ✅ Pull Docker images
- ✅ Generate SSL certificates
- ✅ Start all services
- ✅ Run health checks

---

## 🔥 Firewall Configuration

### Required Ports:

```bash
# TCP Ports
22      # SSH
80      # HTTP (Let's Encrypt)
443     # HTTPS/WSS
7880    # LiveKit
3478    # STUN/TURN
5349    # TURNS (TLS)

# UDP Ports
443     # HTTP/3
3478    # STUN/TURN
5349    # TURNS (TLS)
50000-60000  # RTC/Media relay
```

### UFW Configuration:

```bash
# Allow all required ports
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443
sudo ufw allow 7880/tcp
sudo ufw allow 3478
sudo ufw allow 5349
sudo ufw allow 50000:60000/udp

# Enable firewall
sudo ufw enable
```

### Cloud Provider Configuration:

If using AWS/GCP/Azure, also configure Security Groups/Firewall Rules in your cloud console.

---

## 🔐 SSL/TLS Certificates

### Automatic (Let's Encrypt):

Caddy automatically obtains and renews certificates:
- Certificates stored in: `/data/caddy/certificates/`
- Automatic renewal every 60 days
- No manual intervention needed

### Manual Renewal (if needed):

```bash
# Force certificate renewal
docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

### Certificate Export for TURN:

Certificates are automatically copied to shared volume for Coturn:
```bash
/certs/cert.pem
/certs/key.pem
```

---

## 📊 Service Management

### Start Services:

```bash
docker compose up -d
```

### Stop Services:

```bash
docker compose stop
```

### Restart Services:

```bash
# Restart all
docker compose restart

# Restart specific service
docker compose restart livekit
docker compose restart coturn
docker compose restart caddy
```

### View Logs:

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f livekit
docker compose logs -f coturn
docker compose logs -f caddy

# Last 100 lines
docker compose logs --tail=100 livekit
```

### Check Status:

```bash
docker compose ps
```

### Update Images:

```bash
# Pull latest images
docker compose pull

# Restart with new images
docker compose up -d
```

---

## 🧪 Testing

### 1. Health Check:

```bash
curl https://rtc.pizoo.app/health
# Expected: 200 OK
```

### 2. WebSocket Connection:

```bash
# Using wscat (install: npm install -g wscat)
wscat -c wss://rtc.pizoo.app
# Should connect successfully
```

### 3. STUN Test:

```bash
# Test STUN server
stunclient rtc.pizoo.app 3478
```

### 4. LiveKit Token Test:

From your backend, generate a test token:

```bash
curl -X POST https://your-backend/api/livekit/token \
  -H "Authorization: Bearer YOUR_USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"match_id": "test123", "call_type": "video"}'
```

### 5. Full Call Test:

1. Open your app on 2 devices
2. Start video call
3. Verify:
   - Video/audio works
   - Low latency
   - Connection stable
   - Works on mobile data (TURN)

---

## 🔧 Troubleshooting

### Issue: Services won't start

**Check logs:**
```bash
docker compose logs
```

**Common causes:**
- Port already in use
- Firewall blocking ports
- DNS not configured
- Insufficient resources

### Issue: SSL certificate fails

**Check:**
1. DNS points to correct IP: `dig rtc.pizoo.app`
2. Port 80/443 accessible
3. Caddy logs: `docker compose logs caddy`

**Manual fix:**
```bash
# Stop all services
docker compose down

# Start only Caddy
docker compose up -d caddy

# Wait for cert generation
sleep 30

# Check certificates
docker compose exec caddy ls -la /data/caddy/certificates/

# Start other services
docker compose up -d
```

### Issue: Video works but audio doesn't

**Possible causes:**
- TURN not working
- UDP ports blocked
- Firewall misconfigured

**Test TURN:**
```bash
# Check Coturn logs
docker compose logs coturn | grep -i error

# Verify UDP ports
sudo netstat -tulpn | grep coturn
```

### Issue: Works on WiFi but not on mobile data

**Cause:** TURN server issue

**Fix:**
1. Verify UDP ports 50000-60000 are open
2. Check Coturn configuration
3. Test with external STUN/TURN tester:
   - https://webrtc.github.io/samples/src/content/peerconnection/trickle-ice/

### Issue: High CPU usage

**Possible causes:**
- Too many concurrent calls
- Video quality too high
- Insufficient resources

**Solutions:**
- Upgrade VPS
- Limit video quality in app
- Implement room limits

---

## 📈 Monitoring

### View Service Status:

```bash
watch docker compose ps
```

### Resource Usage:

```bash
# CPU/Memory per container
docker stats

# Disk usage
docker system df
```

### LiveKit Metrics (Optional):

Add Prometheus/Grafana for detailed metrics:

```yaml
# Add to docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  
grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

---

## 🔄 Backup & Restore

### Backup:

```bash
# Backup configuration
tar -czf livekit-backup-$(date +%Y%m%d).tar.gz \
  docker-compose.yml Caddyfile coturn.conf .env

# Backup volumes
docker run --rm \
  -v livekit-stack_caddy_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/caddy-data-backup.tar.gz /data
```

### Restore:

```bash
# Restore configuration
tar -xzf livekit-backup-YYYYMMDD.tar.gz

# Restore volumes
docker run --rm \
  -v livekit-stack_caddy_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/caddy-data-backup.tar.gz -C /
```

---

## 🔐 Security Best Practices

1. **Secrets Management:**
   - Never commit `.env` to git
   - Use strong, randomly generated passwords
   - Rotate credentials regularly

2. **Firewall:**
   - Only open required ports
   - Use cloud provider security groups
   - Consider VPN for admin access

3. **Updates:**
   - Regularly update Docker images
   - Apply OS security patches
   - Monitor security advisories

4. **Monitoring:**
   - Set up log aggregation
   - Configure alerts for failures
   - Monitor resource usage

5. **Backup:**
   - Regular automated backups
   - Test restore procedures
   - Keep backups off-site

---

## 📝 Maintenance

### Weekly:

- Check service status
- Review logs for errors
- Monitor resource usage

### Monthly:

- Update Docker images
- Review and rotate logs
- Check SSL certificate expiry

### Quarterly:

- Review security settings
- Update firewall rules
- Performance optimization
- Backup verification

---

## 🆘 Support

### Logs to Collect:

When requesting help, provide:

```bash
# Service status
docker compose ps > status.txt

# All logs
docker compose logs > logs.txt

# System info
uname -a > system.txt
docker version >> system.txt
docker compose version >> system.txt

# Network info
ip addr > network.txt
ss -tulpn >> network.txt
```

### Useful Links:

- LiveKit Docs: https://docs.livekit.io
- Coturn Docs: https://github.com/coturn/coturn
- Caddy Docs: https://caddyserver.com/docs

---

## 📄 License

LiveKit: Apache 2.0  
Coturn: BSD  
Caddy: Apache 2.0  

---

## ✅ Checklist

Before going live:

- [ ] DNS configured (`rtc.pizoo.app` → VPS IP)
- [ ] Firewall rules applied
- [ ] `.env` file configured with strong secrets
- [ ] SSL certificates obtained
- [ ] All services running
- [ ] Health check passes
- [ ] Test call successful (2 users)
- [ ] TURN working on mobile data
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Backend updated with new credentials

---

**Deployment completed! 🎉**
