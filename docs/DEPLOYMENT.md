# Deployment Guide

## Device Deployment

### 1. Hardware Setup

- Install Raspberry Pi OS on SD card
- Attach PoE HAT and e-Ink display
- Connect red button to GPIO pin 18 (configurable)
- Power via PoE or USB-C

### 2. Software Installation

```bash
cd device
sudo ./setup.sh
```

### 3. Configuration

Edit `/opt/yfitg-scout/.config.json`:

```json
{
  "device_id": "scout-001",
  "mqtt": {
    "broker": "mqtt.yfitg.com",
    "port": 8883,
    "username": "device_user",
    "password": "secure_password",
    "ca_cert": "/opt/yfitg-scout/certs/ca.crt",
    "client_cert": "/opt/yfitg-scout/certs/client.crt",
    "client_key": "/opt/yfitg-scout/certs/client.key"
  },
  "collector": {
    "api_url": "https://api.yfitg.com/reports",
    "api_token": "your_api_token"
  }
}
```

### 4. MQTT Certificates

Place TLS certificates in `/opt/yfitg-scout/certs/`:
- `ca.crt` - CA certificate
- `client.crt` - Client certificate
- `client.key` - Client private key

### 5. LLM Model (Optional)

Download Llama model:
```bash
wget https://huggingface.co/.../llama-3.2-3b-instruct-q4_k_m.gguf \
  -O /opt/yfitg-scout/models/llama-3.2-3b-instruct-q4_k_m.gguf
```

### 6. Enable Service

```bash
sudo systemctl enable yfitg-scout
sudo systemctl start yfitg-scout
sudo systemctl status yfitg-scout
```

## Portal Deployment (Vercel)

### 1. Setup

```bash
cd portal
npm install
```

### 2. Environment Variables

Set in Vercel dashboard:
- `MQTT_BROKER`
- `MQTT_PORT`
- `MQTT_USERNAME`
- `MQTT_PASSWORD`
- `MQTT_USE_TLS`
- `DATABASE_URL` (optional)
- `NEXT_PUBLIC_APP_URL`

### 3. Deploy

```bash
vercel deploy --prod
```

Or connect GitHub repository to Vercel for automatic deployments.

## Collector API Deployment

### Option 1: Standalone Server

```bash
cd server
pip install -r requirements.txt
export API_TOKEN="your-secure-token"
export STORAGE_DIR="/var/yfitg-scout/reports"
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Option 2: Docker

```bash
docker build -t yfitg-collector .
docker run -d \
  -p 8000:8000 \
  -v /var/yfitg-scout/reports:/app/reports \
  -e API_TOKEN="your-secure-token" \
  yfitg-collector
```

### Option 3: Cloud Platform

Deploy to:
- AWS Lambda + API Gateway
- Google Cloud Run
- Azure Container Instances
- Heroku

## MQTT Broker Setup

### Option 1: EMQX Cloud

1. Sign up at https://www.emqx.com/en/cloud
2. Create deployment
3. Configure TLS
4. Create device credentials
5. Update device and portal configs

### Option 2: AWS IoT Core

1. Create IoT Thing
2. Generate certificates
3. Create policy
4. Configure endpoint
5. Update device and portal configs

### Option 3: Self-Hosted (EMQX)

```bash
docker run -d --name emqx \
  -p 1883:1883 \
  -p 8883:8883 \
  -p 8083:8083 \
  -p 8084:8084 \
  -p 18083:18083 \
  emqx/emqx:latest
```

Configure TLS and authentication in EMQX dashboard.

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong API tokens
- [ ] Enable TLS everywhere
- [ ] Validate certificates
- [ ] Restrict MQTT broker access
- [ ] Use firewall rules
- [ ] Enable logging and monitoring
- [ ] Regular security updates
- [ ] Encrypt stored reports
- [ ] Implement rate limiting

## Monitoring

### Device Logs

```bash
journalctl -u yfitg-scout -f
```

### Portal Logs

Check Vercel dashboard or logs:
```bash
vercel logs
```

### API Logs

Check application logs or use monitoring service.

## Troubleshooting

### Device won't connect to MQTT

- Check network connectivity
- Verify MQTT credentials
- Check certificate validity
- Review firewall rules

### Scans not starting

- Verify MQTT message format
- Check device logs
- Confirm consent was recorded
- Verify device_id matches

### Reports not uploading

- Check API token
- Verify network connectivity
- Check API endpoint URL
- Review API logs

