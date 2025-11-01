# 🚀 LiveKit Self-Hosted Deployment - Complete Guide

## 📦 What's Included

Your complete self-hosted LiveKit infrastructure:

```
livekit-stack/
├── docker-compose.yml      # Main stack configuration
├── Caddyfile              # Reverse proxy & SSL config
├── coturn.conf            # TURN server config
├── .env.sample            # Environment variables template
├── deploy.sh              # Automated deployment script
├── test.sh                # Testing & validation script
└── README.md              # Complete documentation
```

---

## 🎯 Deployment Overview

### Phase 1: VPS Setup (You Do This)
1. Provision VPS (2+ CPU, 4GB RAM)
2. Configure DNS: `rtc.pizoo.app` → VPS IP
3. Install Docker & Docker Compose
4. Upload stack files to VPS

### Phase 2: Stack Deployment (Automated)
1. Generate secure credentials
2. Configure environment variables
3. Run deployment script
4. Verify all services

### Phase 3: App Integration (Backend Update)
1. Update backend .env with new LiveKit URL
2. Restart backend service
3. Test from app

---

## 🚀 Step-by-Step Deployment

### Step 1: Prepare VPS

```bash
# 1.1 SSH into your VPS
ssh root@YOUR_VPS_IP

# 1.2 Update system
apt update && apt upgrade -y

# 1.3 Install Docker
curl -fsSL https://get.docker.com | sh

# 1.4 Install Docker Compose
apt install -y docker-compose-plugin

# 1.5 Start Docker
systemctl enable docker
systemctl start docker

# 1.6 Create directory
mkdir -p ~/pizoo-livekit
cd ~/pizoo-livekit
```

### Step 2: Upload Stack Files

**Option A: Using SCP (from your local machine):**
```bash
# From directory containing livekit-stack folder
scp -r livekit-stack/* root@YOUR_VPS_IP:~/pizoo-livekit/
```

**Option B: Using Git:**
```bash
# On VPS
cd ~/pizoo-livekit
git clone YOUR_REPO_URL .
# Or copy files manually
```

**Option C: Manual Copy:**
Upload these files via SFTP/FTP to `~/pizoo-livekit/`:
- docker-compose.yml
- Caddyfile
- coturn.conf
- .env.sample
- deploy.sh
- test.sh
- README.md

### Step 3: Configure DNS

**Important:** Do this BEFORE deployment!

1. Go to your DNS provider (Cloudflare, Route53, etc.)
2. Create A record:
   ```
   Type: A
   Name: rtc
   Value: YOUR_VPS_IP
   TTL: Auto or 300
   ```
3. Verify DNS propagation:
   ```bash
   dig rtc.pizoo.app
   # Should return your VPS IP
   ```

### Step 4: Generate Credentials

```bash
cd ~/pizoo-livekit

# Generate strong credentials
LK_API_KEY=$(openssl rand -hex 16)
LK_API_SECRET=$(openssl rand -base64 32)
TURN_PASS=$(openssl rand -base64 24)
REDIS_PASSWORD=$(openssl rand -base64 32)

# Display (SAVE THESE!)
echo "========================================="
echo "SAVE THESE CREDENTIALS SECURELY!"
echo "========================================="
echo ""
echo "LK_API_KEY=$LK_API_KEY"
echo "LK_API_SECRET=$LK_API_SECRET"
echo "TURN_PASS=$TURN_PASS"
echo "REDIS_PASSWORD=$REDIS_PASSWORD"
echo ""
echo "========================================="
echo "Copy these to a password manager NOW!"
echo "========================================="
```

### Step 5: Configure Environment

```bash
# Copy sample env
cp .env.sample .env

# Edit with your values
nano .env

# Paste the credentials generated above
# Then save (Ctrl+X, Y, Enter)
```

Your `.env` should look like:
```bash
LK_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
LK_API_SECRET=Ym9vdHN0cmFwIHNlY3JldA==
TURN_DOMAIN=rtc.pizoo.app
TURN_USER=pizoo
TURN_PASS=U3Ryb25nUGFzc3dvcmQ=
REDIS_PASSWORD=UmVkaXNQYXNzd29yZA==
```

### Step 6: Deploy Stack

```bash
# Make scripts executable
chmod +x deploy.sh test.sh

# Run deployment
sudo ./deploy.sh
```

**Expected Output:**
```
🚀 Starting LiveKit Stack Deployment...
========================================

📋 Step 1: Checking prerequisites...
✅ Docker is installed
✅ Docker Compose is installed

🔐 Step 2: Checking environment variables...
✅ .env file found

🔥 Step 3: Configuring firewall...
✅ UFW firewall configured

🔧 Step 4: Updating Coturn configuration...
✅ Coturn configuration updated

📦 Step 5: Pulling Docker images...
✅ Docker images pulled

🛑 Step 6: Stopping existing containers...
✅ Existing containers stopped

🔐 Step 7: Generating SSL certificates...
✅ SSL certificates generated

🚀 Step 8: Starting all services...
✅ All services started

⏳ Step 9: Waiting for services to be ready...

🏥 Step 10: Running health checks...
✅ Caddy is healthy
✅ LiveKit is running
✅ Coturn is running
✅ Redis is running

========================================
✅ Deployment Complete!
========================================
```

### Step 7: Run Tests

```bash
# Run test suite
sudo ./test.sh
```

**Expected Output:**
```
🧪 LiveKit Stack Testing
========================

1️⃣ DNS Resolution
Testing DNS A Record... ✅ PASSED

2️⃣ Port Accessibility
Testing HTTP (80)... ✅ PASSED
Testing HTTPS (443)... ✅ PASSED
Testing STUN/TURN (3478)... ✅ PASSED

3️⃣ SSL Certificate
Testing SSL Certificate Valid... ✅ PASSED
Testing Certificate Not Expired... ✅ PASSED

[... more tests ...]

========================
📊 Test Summary
========================
Passed: 15
Failed: 0

🎉 All tests passed!
```

### Step 8: Update Backend

Now update your Pizoo backend to use the new self-hosted LiveKit:

```bash
# On your backend server (not VPS)
cd /app/backend

# Edit .env
nano .env

# Update these values:
LIVEKIT_URL=wss://rtc.pizoo.app
LIVEKIT_API_KEY=<your_LK_API_KEY_from_step_4>
LIVEKIT_API_SECRET=<your_LK_API_SECRET_from_step_4>

# Save and exit

# Restart backend
sudo supervisorctl restart backend

# Verify it loaded
tail -f /var/log/supervisor/backend.err.log | grep -i livekit
# Should see: ✅ LiveKit configured successfully
```

### Step 9: Test from App

1. Open your Pizoo app on 2 devices/browsers
2. Login with 2 different test accounts
3. Start a video call
4. Verify:
   - ✅ Video/audio works
   - ✅ Low latency (<300ms)
   - ✅ Good quality
   - ✅ Stable connection

5. Test on mobile data (not WiFi):
   - ✅ Call connects (TURN working)
   - ✅ Audio/video works
   - ✅ No connection drops

---

## 🎬 Video Call Test Plan

### Test Case 1: WiFi to WiFi (STUN)

**Participants:**
- User A: On WiFi
- User B: On WiFi

**Steps:**
1. User A opens chat with User B
2. User A clicks video call button 🎥
3. Wait for connection (2-3 seconds)
4. Verify:
   - Both see each other's video
   - Audio is clear
   - Latency is low
   - No freezing/stuttering

**Expected Result:** ✅ Call works perfectly

---

### Test Case 2: Mobile Data to Mobile Data (TURN)

**Participants:**
- User A: On 4G/5G mobile data
- User B: On 4G/5G mobile data

**Steps:**
1. User A starts video call
2. User B joins
3. Verify:
   - TURN is used (check Coturn logs)
   - Video/audio works
   - Quality adapts to bandwidth
   - Connection stable

**Expected Result:** ✅ Call works with TURN relay

**Verify TURN is working:**
```bash
# On VPS
docker compose logs coturn | grep -i "allocation created"
# Should see entries when call is active
```

---

### Test Case 3: Voice Call (Audio Only)

**Steps:**
1. User A starts voice call 🎤
2. Verify:
   - Camera stays off
   - Audio is crystal clear
   - Low bandwidth usage
   - Works on poor network

**Expected Result:** ✅ Audio-only call works

---

### Test Case 4: Connection Recovery

**Steps:**
1. Start video call
2. Switch between WiFi and mobile data
3. Verify:
   - Call reconnects automatically
   - Quality adjusts
   - No need to restart call

**Expected Result:** ✅ Resilient to network changes

---

## 📊 Monitoring & Maintenance

### Check Service Status

```bash
# On VPS
cd ~/pizoo-livekit

# View all services
docker compose ps

# Check logs
docker compose logs -f

# Restart if needed
docker compose restart livekit
```

### Monitor Resource Usage

```bash
# CPU/Memory per container
docker stats

# Disk usage
df -h
docker system df
```

### View Active Calls

```bash
# Check LiveKit logs for active rooms
docker compose logs livekit | grep -i "room created"
docker compose logs livekit | grep -i "participant joined"
```

### Certificate Renewal

Caddy handles this automatically, but you can check:

```bash
# View certificate expiry
docker compose exec caddy caddy list-certificates

# Force renewal (if needed)
docker compose exec caddy caddy reload
```

---

## 🐛 Troubleshooting

### Problem: SSL Certificate Failed

**Symptoms:**
- Deploy script shows: ❌ SSL certificate generation failed
- HTTPS doesn't work

**Solutions:**
```bash
# 1. Verify DNS
dig rtc.pizoo.app
# Must return YOUR VPS IP

# 2. Check ports
telnet rtc.pizoo.app 80
telnet rtc.pizoo.app 443

# 3. Check Caddy logs
docker compose logs caddy | grep -i error

# 4. Retry certificate
docker compose restart caddy
sleep 30
docker compose logs caddy
```

---

### Problem: Video Works on WiFi but Not Mobile Data

**Symptoms:**
- Calls work on WiFi
- Calls fail or have poor quality on mobile data

**Solutions:**
```bash
# 1. Verify TURN is running
docker compose ps coturn
# Should show: Up

# 2. Check TURN logs
docker compose logs coturn | grep -i error

# 3. Test TURN server
# Use: https://webrtc.github.io/samples/src/content/peerconnection/trickle-ice/
# Add TURN server:
#   URL: turn:rtc.pizoo.app:3478
#   Username: pizoo
#   Password: <your TURN_PASS>

# 4. Verify UDP ports
sudo ufw status | grep 50000:60000
# Should be ALLOW

# 5. Check firewall on cloud provider
# AWS: Security Groups
# GCP: Firewall Rules
# Azure: Network Security Groups
```

---

### Problem: High CPU Usage

**Symptoms:**
- VPS CPU at 80-100%
- Calls lag/freeze

**Solutions:**
```bash
# 1. Check which service
docker stats

# 2. Reduce video quality in app
# Or upgrade VPS to more CPU cores

# 3. Limit concurrent rooms (in app logic)

# 4. Consider scaling horizontally
# Deploy multiple LiveKit servers with load balancer
```

---

## 🔐 Security Checklist

- [ ] Strong credentials generated (not default)
- [ ] `.env` file secured (chmod 600)
- [ ] Firewall configured (only required ports)
- [ ] SSL/TLS enabled (HTTPS/WSS)
- [ ] No secrets in git
- [ ] Regular updates enabled
- [ ] Monitoring configured
- [ ] Backup strategy in place

---

## 📈 Scaling (Future)

When you outgrow a single server:

1. **Vertical Scaling:**
   - Upgrade VPS (more CPU/RAM)
   - Simple, but has limits

2. **Horizontal Scaling:**
   - Deploy multiple LiveKit servers
   - Add load balancer
   - Use Redis for session sharing

3. **Geographic Distribution:**
   - Deploy in multiple regions
   - Route users to nearest server
   - Reduce latency globally

---

## ✅ Success Criteria

Your deployment is successful when:

- [x] All tests pass (`./test.sh`)
- [x] Health check returns 200: `curl https://rtc.pizoo.app/health`
- [x] 2 users can video call on WiFi
- [x] 2 users can video call on mobile data (TURN working)
- [x] Backend connects successfully
- [x] No errors in logs
- [x] Resource usage is normal (<50% CPU)
- [x] SSL certificate valid
- [x] Firewall configured

---

## 📞 Support

**If you encounter issues:**

1. Collect logs:
   ```bash
   docker compose logs > full-logs.txt
   ```

2. Check README.md troubleshooting section

3. Review LiveKit docs: https://docs.livekit.io

4. Test with LiveKit Playground:
   - https://livekit.io/playground
   - Use your generated token
   - Verify server connectivity

---

**Deployment Guide Complete! 🎉**

You now have a production-ready, self-hosted LiveKit infrastructure!
