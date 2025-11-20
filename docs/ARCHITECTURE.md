# System Architecture

## Overview

The YFITG Network Scout system consists of three main components:

1. **Device Software** - Runs on Raspberry Pi 5
2. **Consent Portal** - Next.js web application on Vercel
3. **Report Collector** - FastAPI server for receiving reports

## Component Interaction

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Device   │◄───────►│  MQTT Broker │◄───────►│   Portal    │
│ (Raspberry │         │              │         │  (Vercel)   │
│    Pi 5)   │         └──────────────┘         └─────────────┘
└──────┬──────┘
       │
       │ HTTPS
       ▼
┌─────────────┐
│   Collector │
│    API      │
└─────────────┘
```

## Data Flow

### 1. Consent & Authorization

1. User scans QR code or visits portal URL
2. Portal displays consent form (prefilled if info available)
3. User submits consent
4. Portal stores consent record
5. Portal publishes MQTT message: `device/{device_id}/start`
6. Device receives start command

### 2. Scanning

1. Device validates consent and scope
2. Device displays scanning animation
3. Device runs:
   - Nmap port scan
   - Nikto web scan
   - TLS validation
4. Device aggregates results
5. Device generates JSON summary

### 3. Report Generation

1. Device sends results to local LLM
2. LLM generates executive summary
3. Device renders PDF using Jinja2 template
4. Device calculates file hash
5. Device uploads PDF + metadata to collector API

### 4. Report Storage

1. Collector API validates token
2. Collector API verifies file hash
3. Collector API stores PDF and metadata
4. Collector API optionally sends notification

## Security Architecture

### Authentication

- **MQTT**: TLS 1.2+ with client certificates or username/password
- **API**: Bearer token authentication
- **Device**: Unique device ID + token pair

### Network Security

- Device uses outbound-only connections
- No inbound ports required
- All communication over TLS
- Certificate validation enforced

### Data Security

- Reports encrypted in transit (HTTPS)
- Optional encryption at rest
- Automatic deletion after upload (configurable)
- Audit logging with consent IDs

## Scalability Considerations

### Device

- Single device per network
- Stateless operation
- No persistent connections required

### Portal

- Stateless Next.js app
- Can scale horizontally on Vercel
- Database for consent storage (optional)

### Collector

- Stateless API
- Can scale horizontally
- File storage can be S3/cloud storage

### MQTT Broker

- Cloud-hosted broker recommended
- Supports thousands of devices
- Message persistence optional

## Failure Handling

### Device Failures

- Automatic restart via systemd
- MQTT reconnection with exponential backoff
- Partial scan results uploaded on abort
- Error state displayed on e-ink

### Network Failures

- Device retries uploads
- MQTT reconnection
- Graceful degradation (local storage)

### API Failures

- Device retries with backoff
- Local storage as backup
- Manual upload option

## Monitoring & Logging

### Device Logs

- Systemd journal
- File-based logs
- Structured JSON logs

### Portal Logs

- Vercel logs
- Application logs
- Error tracking

### API Logs

- Application logs
- Access logs
- Error tracking

## Performance Targets

- Scan duration: < 90 minutes for /24 network
- Report generation: < 5 minutes
- Upload time: < 2 minutes (depends on size)
- Portal response: < 500ms
- API response: < 200ms

