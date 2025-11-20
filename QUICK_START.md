# Quick Start Guide - YFITG Network Scout

This is a condensed version for experienced users. For detailed instructions, see [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md).

## Prerequisites Checklist

- [ ] Raspberry Pi 5 with PoE HAT and e-Ink display
- [ ] MQTT broker (EMQX Cloud, AWS IoT, or self-hosted)
- [ ] Server for collector API (or cloud platform)
- [ ] Vercel account

## 5-Minute Setup

### 1. MQTT Broker (2 minutes)

**EMQX Cloud:**
1. Sign up at emqx.com/en/cloud
2. Create free deployment
3. Note: broker address, port (8883), create users
4. Download CA cert

### 2. Device Setup (5 minutes)

```bash
# On Raspberry Pi
git clone <repo> && cd YFITG-Recon/device
sudo ./setup.sh
sudo nano /opt/yfitg-scout/.config.json  # Add MQTT & API config
sudo systemctl enable --now yfitg-scout
journalctl -u yfitg-scout -f  # Verify connection
```

### 3. Collector API (3 minutes)

```bash
# On server or locally
cd server
pip install -r requirements.txt
export API_TOKEN="secure-token"
export STORAGE_DIR="./reports"
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or with Docker:
```bash
docker run -d -p 8000:8000 \
  -e API_TOKEN="secure-token" \
  -v $(pwd)/reports:/app/reports \
  yfitg-collector
```

### 4. Portal (3 minutes)

```bash
cd portal
npm install
cp .env.example .env.local  # Add MQTT config
vercel deploy
# Or: npm run dev (for local testing)
```

Set environment variables in Vercel dashboard.

### 5. Test (2 minutes)

1. Visit portal URL
2. Fill consent form (device: `scout-001`, CIDR: `192.168.1.0/24`)
3. Submit
4. Check device logs: `journalctl -u yfitg-scout -f`
5. Verify scan starts

## Configuration Files

### Device: `/opt/yfitg-scout/.config.json`
```json
{
  "device_id": "scout-001",
  "mqtt": {
    "broker": "xxx.emqx.cloud",
    "port": 8883,
    "username": "device_user",
    "password": "password"
  },
  "collector": {
    "api_url": "https://api.example.com/reports",
    "api_token": "token"
  }
}
```

### Portal: `.env.local`
```env
MQTT_BROKER=xxx.emqx.cloud
MQTT_PORT=8883
MQTT_USERNAME=portal_user
MQTT_PASSWORD=password
MQTT_USE_TLS=true
```

## Common Issues

**Device won't connect:**
- Check MQTT credentials
- Verify network connectivity
- Check firewall rules

**Portal can't publish:**
- Verify environment variables in Vercel
- Test MQTT connection manually

**Reports not uploading:**
- Check API token
- Verify API URL is accessible
- Check device logs

## Next Steps

1. Test on isolated network
2. Download LLM model (optional)
3. Add animation frames (optional)
4. Deploy to production

For detailed instructions, see [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md).

