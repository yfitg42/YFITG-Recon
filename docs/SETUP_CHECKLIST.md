# Setup Checklist - YFITG Network Scout

Use this checklist to track your setup progress. Check off items as you complete them.

## Phase 1: Prerequisites ✅

- [ ] Raspberry Pi 5 (8 GB) purchased
- [ ] PoE HAT purchased
- [ ] e-Ink display HAT purchased
- [ ] Red push button purchased
- [ ] MicroSD card (32 GB+) purchased
- [ ] Vercel account created
- [ ] MQTT broker account created (EMQX/AWS/self-hosted)
- [ ] Server/cloud platform for API ready

## Phase 2: MQTT Broker Setup ✅

- [ ] MQTT broker deployed/configured
- [ ] TLS enabled (port 8883)
- [ ] Device user created (`device_user`)
- [ ] Portal user created (`portal_user`)
- [ ] CA certificate downloaded
- [ ] Connection tested manually
- [ ] Broker address noted: `_________________`
- [ ] Device password noted: `_________________`
- [ ] Portal password noted: `_________________`

## Phase 3: Device Setup ✅

### Hardware
- [ ] Raspberry Pi OS flashed to SD card
- [ ] SSH enabled during imaging
- [ ] Pi booted and accessible via SSH
- [ ] PoE HAT installed
- [ ] e-Ink display connected
- [ ] Button connected to GPIO 18
- [ ] Network connectivity verified

### Software
- [ ] System updated (`apt update && apt upgrade`)
- [ ] Required packages installed (nmap, nikto, python3-dev, etc.)
- [ ] Repository cloned/copied to Pi
- [ ] Setup script executed (`./device/setup.sh`)
- [ ] Configuration file created (`/opt/yfitg-scout/.config.json`)
- [ ] MQTT credentials added to config
- [ ] API credentials added to config
- [ ] CA certificate copied to `/opt/yfitg-scout/certs/`
- [ ] Device ID set: `scout-XXX`
- [ ] Manual test successful (MQTT connection)
- [ ] Systemd service enabled
- [ ] Service started and running
- [ ] Logs verified (no errors)

### Optional
- [ ] LLM model downloaded to `/opt/yfitg-scout/models/`
- [ ] Animation frames added to `/opt/yfitg-scout/assets/animations/`
- [ ] YFITG logo added for reports

## Phase 4: Collector API Setup ✅

- [ ] Server/cloud platform ready
- [ ] API code deployed
- [ ] Dependencies installed
- [ ] Environment variables set:
  - [ ] `API_TOKEN` generated: `_________________`
  - [ ] `STORAGE_DIR` configured
- [ ] API server running
- [ ] Health endpoint tested (`/health`)
- [ ] Authentication tested
- [ ] Storage directory writable
- [ ] API URL noted: `https://_________________`

### Update Device Config
- [ ] Device config updated with API URL
- [ ] Device config updated with API token
- [ ] Device service restarted

## Phase 5: Portal Setup ✅

- [ ] Portal code prepared
- [ ] Dependencies installed (`npm install`)
- [ ] Environment file created (`.env.local`)
- [ ] MQTT credentials added:
  - [ ] `MQTT_BROKER`
  - [ ] `MQTT_PORT`
  - [ ] `MQTT_USERNAME`
  - [ ] `MQTT_PASSWORD`
  - [ ] `MQTT_USE_TLS`
- [ ] Local test successful (`npm run dev`)
- [ ] Deployed to Vercel
- [ ] Environment variables set in Vercel dashboard
- [ ] Production URL noted: `https://_________________`
- [ ] Portal accessible and form loads
- [ ] MQTT publishing tested

## Phase 6: Integration Testing ✅

### MQTT Flow
- [ ] Device connects to MQTT broker
- [ ] Device subscribes to `device/{device_id}/start`
- [ ] Portal can publish to MQTT
- [ ] Device receives start command
- [ ] Device logs show received message

### Scan Flow
- [ ] Consent form submitted via portal
- [ ] Consent ID generated
- [ ] MQTT message published
- [ ] Device receives start command
- [ ] e-Ink display shows "Scanning..."
- [ ] Scan executes (nmap, nikto, TLS)
- [ ] Progress visible in logs
- [ ] Scan completes successfully

### Report Flow
- [ ] Report generated (PDF)
- [ ] Executive summary created
- [ ] Report uploaded to API
- [ ] API receives and stores report
- [ ] Report retrievable via API
- [ ] e-Ink display shows "Complete"

### End-to-End Test
- [ ] Full workflow tested on isolated network
- [ ] Report reviewed and verified
- [ ] All components working together
- [ ] Error handling tested (abort button, network issues)

## Phase 7: Production Readiness ✅

### Security
- [ ] All default passwords changed
- [ ] Strong API tokens generated
- [ ] TLS enabled everywhere
- [ ] Certificates valid and not expired
- [ ] Firewall rules configured
- [ ] Access controls in place

### Documentation
- [ ] Device ID documented
- [ ] All credentials stored securely
- [ ] Network requirements documented
- [ ] Troubleshooting guide reviewed
- [ ] Team trained on usage

### Testing
- [ ] Tested on isolated network
- [ ] Tested with various network sizes
- [ ] Error scenarios tested
- [ ] Recovery procedures tested
- [ ] Performance verified (< 90 min for /24)

### Deployment
- [ ] Device labeled with ID and QR code
- [ ] Portal URL added to QR code
- [ ] Shipping materials prepared
- [ ] Client onboarding materials ready
- [ ] Support contact information available

## Phase 8: First Client Deployment ✅

- [ ] Device shipped to client
- [ ] Client receives device
- [ ] Client scans QR code
- [ ] Consent form completed
- [ ] Scan initiated
- [ ] Scan completed successfully
- [ ] Report received and reviewed
- [ ] Client feedback collected
- [ ] Issues documented and resolved

---

## Quick Reference

### Device Commands
```bash
sudo systemctl status yfitg-scout    # Check status
journalctl -u yfitg-scout -f          # View logs
sudo systemctl restart yfitg-scout   # Restart service
```

### Important Files
- Device config: `/opt/yfitg-scout/.config.json`
- Device logs: `journalctl -u yfitg-scout`
- Portal config: `portal/.env.local`
- API config: Environment variables

### Test URLs
- Portal: `https://your-portal.vercel.app`
- API Health: `https://your-api.com/health`
- API Reports: `https://your-api.com/reports` (requires auth)

---

## Notes

Use this space to jot down important information:

**Device ID:** _________________________________

**MQTT Broker:** _________________________________

**API URL:** _________________________________

**Portal URL:** _________________________________

**API Token:** _________________________________

**Issues Encountered:**
- 
- 
- 

**Solutions:**
- 
- 
- 

---

**Setup Date:** _______________

**Completed By:** _______________

**Next Review Date:** _______________

