# YFITG Network Scout - Complete Setup Guide

This guide will walk you through setting up the entire YFITG Network Scout system from scratch.

## Prerequisites

### Hardware
- Raspberry Pi 5 (8 GB RAM recommended)
- MicroSD card (32 GB+)
- PoE HAT for Raspberry Pi 5
- e-Ink display HAT (Waveshare 7.5" or compatible)
- Red push button
- Ethernet cable (if using PoE)
- USB-C power supply (if not using PoE)

### Software Accounts
- Vercel account (free tier works)
- MQTT broker account (EMQX Cloud free tier, AWS IoT, or self-hosted)
- GitHub account (for deployment)

### Knowledge
- Basic Linux command line
- Basic understanding of networking
- Access to a test network for initial testing

---

## Step 1: Set Up MQTT Broker

You need an MQTT broker for device communication. Choose one option:

### Option A: EMQX Cloud (Recommended for Quick Start)

1. **Sign up**: Go to https://www.emqx.com/en/cloud
2. **Create deployment**:
   - Choose free tier
   - Select region closest to you
   - Wait for deployment (2-3 minutes)
3. **Get connection info**:
   - Note the broker address (e.g., `xxx.emqx.cloud`)
   - Default port: `1883` (non-TLS) or `8883` (TLS)
4. **Create device credentials**:
   - Go to "Authentication" → "Users"
   - Create new user: `device_user` with password
   - Create another user: `portal_user` with password
5. **Enable TLS** (recommended):
   - Go to "TLS/SSL"
   - Enable TLS listener on port 8883
   - Download CA certificate

**Save these values:**
- Broker address: `xxx.emqx.cloud`
- Port: `8883`
- Device username: `device_user`
- Device password: `[your_password]`
- Portal username: `portal_user`
- Portal password: `[your_password]`

### Option B: AWS IoT Core

1. **Create AWS account** (if needed)
2. **Create IoT Thing**:
   - AWS Console → IoT Core → Things → Create
   - Name: `yfitg-scout-001`
3. **Create certificates**:
   - Security → Certificates → Create
   - Download: Certificate, Private key, Root CA
4. **Create policy**:
   - Security → Policies → Create
   - Allow: `iot:Connect`, `iot:Publish`, `iot:Subscribe`, `iot:Receive`
   - Attach to certificate
5. **Get endpoint**:
   - Settings → Device data endpoint
   - Note the endpoint address

### Option C: Self-Hosted (Advanced)

```bash
# Using Docker
docker run -d --name emqx \
  -p 1883:1883 \
  -p 8883:8883 \
  -p 8083:8083 \
  -p 18083:18083 \
  emqx/emqx:latest

# Access dashboard at http://localhost:18083
# Default username: admin, password: public
```

---

## Step 2: Set Up Raspberry Pi Device

### 2.1 Flash Raspberry Pi OS

1. **Download Raspberry Pi Imager**: https://www.raspberrypi.com/software/
2. **Flash OS**:
   - Insert microSD card
   - Open Raspberry Pi Imager
   - Choose "Raspberry Pi OS (64-bit)"
   - Click gear icon → Enable SSH, set username/password
   - Write to SD card
3. **Boot Pi**:
   - Insert SD card into Pi
   - Connect to network (Ethernet or WiFi)
   - Power on

### 2.2 Initial Pi Setup

```bash
# SSH into Pi (replace with your Pi's IP)
ssh pi@192.168.1.100

# Update system
sudo apt update && sudo apt upgrade -y

# Install required system packages
sudo apt install -y \
  python3-pip \
  python3-venv \
  git \
  nmap \
  nikto \
  python3-dev \
  libssl-dev \
  build-essential

# Enable I2C for e-Ink display (if needed)
sudo raspi-config
# Navigate to Interface Options → I2C → Enable
```

### 2.3 Install Device Software

```bash
# Clone repository (or copy files)
cd ~
git clone https://github.com/yfitg42/YFITG-Recon
cd YFITG-Recon/device

# Run setup script
sudo chmod +x setup.sh
sudo ./setup.sh
```

### 2.4 Configure Device

```bash
# Edit configuration
sudo nano /opt/yfitg-scout/.config.json
```

**Update with your MQTT broker info:**

```json
{
  "device_id": "scout-001",
  "mqtt": {
    "broker": "xxx.emqx.cloud",
    "port": 8883,
    "username": "device_user",
    "password": "your_device_password",
    "ca_cert": "/opt/yfitg-scout/certs/ca.crt",
    "client_cert": "",
    "client_key": ""
  },
  "collector": {
    "api_url": "https://your-api-domain.com/reports",
    "api_token": "your_api_token_here"
  },
  "llm": {
    "model_path": "/opt/yfitg-scout/models/llama-3.2-3b-instruct-q4_k_m.gguf",
    "threads": 4,
    "fallback_api": ""
  },
  "scanning": {
    "max_duration_hours": 2,
    "default_timeout": 900,
    "allowed_ranges": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
  },
  "display": {
    "type": "waveshare_epd",
    "width": 800,
    "height": 480,
    "animation_fps": 6
  },
  "button": {
    "gpio_pin": 18,
    "long_press_duration": 3.0
  }
}
```

### 2.5 Add MQTT Certificates (if using TLS)

```bash
# Create certs directory
sudo mkdir -p /opt/yfitg-scout/certs

# Copy CA certificate (download from EMQX or AWS)
sudo nano /opt/yfitg-scout/certs/ca.crt
# Paste certificate content, save

# Set permissions
sudo chown -R pi:pi /opt/yfitg-scout/certs
```

### 2.6 Test Device Software

```bash
# Test manually first
cd /opt/yfitg-scout
source .venv/bin/activate
python main.py

# If it connects to MQTT, you'll see:
# "Connected to MQTT broker"
# "Subscribed to device/scout-001/start"

# Press Ctrl+C to stop
```

### 2.7 Enable Service

```bash
# Enable and start service
sudo systemctl enable yfitg-scout
sudo systemctl start yfitg-scout

# Check status
sudo systemctl status yfitg-scout

# View logs
journalctl -u yfitg-scout -f
```

---

## Step 3: Deploy Collector API

### Option A: Deploy to Cloud Server

```bash
# On your server (Ubuntu/Debian)
sudo apt update
sudo apt install -y python3-pip python3-venv

# Clone repository
git clone <your-repo-url> YFITG-Recon
cd YFITG-Recon/server

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export API_TOKEN="your-secure-random-token-here"
export STORAGE_DIR="/var/yfitg-scout/reports"

# Create storage directory
sudo mkdir -p /var/yfitg-scout/reports
sudo chown $USER:$USER /var/yfitg-scout/reports

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option B: Deploy with Docker

```bash
cd server

# Build image
docker build -t yfitg-collector .

# Run container
docker run -d \
  --name yfitg-collector \
  -p 8000:8000 \
  -v $(pwd)/reports:/app/reports \
  -e API_TOKEN="your-secure-random-token-here" \
  -e STORAGE_DIR="/app/reports" \
  yfitg-collector
```

### Option C: Deploy to Cloud Platform

**Heroku:**
```bash
cd server
heroku create yfitg-collector
heroku config:set API_TOKEN="your-token"
git push heroku main
```

**Railway/Render:**
- Connect GitHub repo
- Set environment variables
- Deploy

### 3.1 Test API

```bash
# Test health endpoint
curl https://your-api-domain.com/health

# Should return: {"status":"healthy"}

# Test with authentication
curl -H "Authorization: Bearer your-token" \
  https://your-api-domain.com/reports
```

### 3.2 Update Device Config

Update the device's `.config.json` with your API URL and token:

```json
"collector": {
  "api_url": "https://your-api-domain.com/reports",
  "api_token": "your-token-here"
}
```

---

## Step 4: Deploy Portal to Vercel

### 4.1 Prepare Portal

```bash
cd portal

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local
```

### 4.2 Configure Environment Variables

Edit `.env.local`:

```env
MQTT_BROKER=xxx.emqx.cloud
MQTT_PORT=8883
MQTT_USERNAME=portal_user
MQTT_PASSWORD=your_portal_password
MQTT_USE_TLS=true
DATABASE_URL=  # Optional, leave empty for now
NEXT_PUBLIC_APP_URL=https://your-portal.vercel.app
```

### 4.3 Deploy to Vercel

**Option A: Vercel CLI**

```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
cd portal
vercel

# Set production environment variables
vercel env add MQTT_BROKER
vercel env add MQTT_PORT
vercel env add MQTT_USERNAME
vercel env add MQTT_PASSWORD
vercel env add MQTT_USE_TLS
vercel env add NEXT_PUBLIC_APP_URL

# Deploy to production
vercel --prod
```

**Option B: GitHub Integration**

1. Push code to GitHub
2. Go to https://vercel.com
3. Import your repository
4. Set environment variables in Vercel dashboard
5. Deploy

### 4.4 Test Portal

1. Visit your Vercel URL
2. You should see the consent form
3. Test with a device ID: `scout-001`

---

## Step 5: Connect Everything Together

### 5.1 Test MQTT Connection

**From Portal to Device:**

1. Open portal in browser
2. Fill out consent form:
   - Name: Test User
   - Email: test@example.com
   - Company: Test Company
   - Device ID: `scout-001`
   - CIDR: `192.168.1.0/24`
   - Check authorization box
3. Click "Authorize & Start Scan"

**Check Device Logs:**

```bash
# On Raspberry Pi
journalctl -u yfitg-scout -f

# You should see:
# "Received start command: {...}"
# "Starting scan with consent_id: ..."
```

### 5.2 Test Scan (On Isolated Network)

**IMPORTANT**: Test on an isolated/test network first!

1. Connect device to test network
2. Trigger scan via portal
3. Watch e-Ink display (should show scanning animation)
4. Wait for completion
5. Check device logs for report generation
6. Verify report uploaded to collector API

### 5.3 Verify Report Upload

```bash
# Check collector API
curl -H "Authorization: Bearer your-token" \
  https://your-api-domain.com/reports

# Should list uploaded reports
```

---

## Step 6: Optional Enhancements

### 6.1 Download LLM Model (Optional)

```bash
# On Raspberry Pi
cd /opt/yfitg-scout/models

# Download model (example - adjust URL)
wget https://huggingface.co/.../llama-3.2-3b-instruct-q4_k_m.gguf \
  -O llama-3.2-3b-instruct-q4_k_m.gguf

# Verify file exists
ls -lh
```

### 6.2 Add Animation Frames (Optional)

```bash
# Create animations directory
sudo mkdir -p /opt/yfitg-scout/assets/animations

# Copy your animation frames (frame_00.png, frame_01.png, etc.)
sudo cp frame_*.png /opt/yfitg-scout/assets/animations/

# Set permissions
sudo chown -R pi:pi /opt/yfitg-scout/assets
```

### 6.3 Set Up Database for Portal (Optional)

For production, replace in-memory consent storage:

```bash
# Install PostgreSQL (example)
sudo apt install postgresql

# Create database
sudo -u postgres createdb yfitg_scout

# Update portal to use database
# Modify portal/app/api/consent/route.ts
```

---

## Step 7: Production Checklist

Before deploying to clients:

- [ ] All credentials changed from defaults
- [ ] Strong API tokens generated
- [ ] TLS enabled everywhere
- [ ] Firewall rules configured
- [ ] Device tested on isolated network
- [ ] Reports verified and reviewed
- [ ] Error handling tested
- [ ] Logs monitored
- [ ] Backup procedures in place
- [ ] Documentation reviewed
- [ ] Legal/consent forms reviewed

---

## Troubleshooting

### Device Won't Connect to MQTT

```bash
# Check network connectivity
ping mqtt-broker-address

# Test MQTT connection manually
mosquitto_pub -h broker -p 8883 -u username -P password -t test -m "test"

# Check device logs
journalctl -u yfitg-scout -n 50
```

### Portal Can't Publish to MQTT

- Verify MQTT credentials in Vercel environment variables
- Check MQTT broker logs
- Test MQTT connection from local machine

### Reports Not Uploading

```bash
# Check device logs
journalctl -u yfitg-scout | grep -i upload

# Test API manually
curl -X POST \
  -H "Authorization: Bearer your-token" \
  -F "report=@test.pdf" \
  -F "metadata={\"consent_id\":\"test\"}" \
  https://your-api-domain.com/reports
```

### e-Ink Display Not Working

```bash
# Check if display is detected
lsmod | grep i2c

# Test display library
python3 -c "from waveshare_epd import epd7in5_V2; print('OK')"

# Check permissions
ls -l /dev/i2c-*
```

---

## Quick Reference

### Device Commands

```bash
# Start service
sudo systemctl start yfitg-scout

# Stop service
sudo systemctl stop yfitg-scout

# View logs
journalctl -u yfitg-scout -f

# Restart service
sudo systemctl restart yfitg-scout

# Check status
sudo systemctl status yfitg-scout
```

### Portal URLs

- Production: `https://your-portal.vercel.app`
- With prefill: `https://your-portal.vercel.app?device=scout-001&name=John&email=john@example.com`

### API Endpoints

- Health: `GET /health`
- Upload: `POST /reports` (requires auth)
- List: `GET /reports` (requires auth)
- Get by ID: `GET /reports/{consent_id}` (requires auth)

---

## Support

For issues or questions:
1. Check logs first
2. Review documentation
3. Check GitHub issues
4. Contact YFITG support

---

## Next Steps After Setup

1. **Test thoroughly** on isolated network
2. **Create device labels** with QR codes
3. **Train team** on device usage
4. **Prepare client materials** (consent forms, etc.)
5. **Plan pilot deployment** with friendly client
6. **Gather feedback** and iterate

Good luck with your deployment! 🚀

