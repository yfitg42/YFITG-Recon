# YFITG Network Scout

A plug-and-scan network assessment device based on Raspberry Pi 5 that performs non-intrusive security scans and generates AI-written executive reports.

## 🏗️ Project Structure

```
YFITG-Recon/
├── device/          # Raspberry Pi Python software
├── portal/          # Next.js Vercel portal (consent form)
├── server/          # FastAPI report collector API
├── assets/          # Logos, animation frames, 3D models
└── docs/            # Documentation
```

## 🚀 Quick Start

**New to the project?** Start here:
- **[Quick Start Guide](QUICK_START.md)** - 5-minute condensed setup
- **[Complete Setup Guide](docs/SETUP_GUIDE.md)** - Detailed step-by-step instructions

### Setup Overview

1. **MQTT Broker** - Set up EMQX Cloud, AWS IoT, or self-hosted broker
2. **Device** - Install software on Raspberry Pi 5
3. **Collector API** - Deploy FastAPI server for report storage
4. **Portal** - Deploy Next.js consent form to Vercel
5. **Test** - Verify end-to-end flow on isolated network

See [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md) for complete instructions.

## 📋 Development Phases

- **Phase 1**: Core infrastructure (MQTT + Portal + Handshake)
- **Phase 2**: Scanning engine (Nmap/Nikto/TLS)
- **Phase 3**: LLM reporting (Summary + PDF + Upload)
- **Phase 4**: UX polish (Branding + Animation + Errors)
- **Phase 5**: Field pilot (Testing + Refinement)

## 🔒 Security

- Mandatory consent before scanning
- Outbound-only communication
- TLS 1.2+ everywhere
- Encrypted local storage
- Automatic data deletion after upload

## 📄 License

Proprietary - YFITG Internal Use Only

