# Scanning Safety Guidelines

## Non-Intrusive Scanning Principles

The YFITG Network Scout is designed to perform **safe, non-intrusive** network assessments. This document outlines the safety measures and limitations.

## What We Do

### Safe Operations

1. **Port Enumeration**
   - TCP SYN scans (half-open)
   - Service version detection
   - No full connection attempts to all ports

2. **Service Detection**
   - Banner grabbing
   - Version identification
   - No exploitation attempts

3. **Web Server Scanning**
   - Nikto in safe mode
   - No brute force attempts
   - No exploit execution

4. **TLS/SSL Validation**
   - Certificate inspection
   - Protocol version checking
   - No man-in-the-middle attacks

## What We Don't Do

### Prohibited Operations

1. **No Password Attempts**
   - No brute force attacks
   - No credential testing
   - No authentication bypass attempts

2. **No Exploitation**
   - No vulnerability exploitation
   - No code injection
   - No denial of service

3. **No Data Exfiltration**
   - No data collection beyond service info
   - No file access
   - No sensitive data retrieval

4. **No Network Disruption**
   - Rate limiting to prevent overload
   - Respectful scan timing
   - No broadcast storms

## Safety Guardrails

### Technical Limits

- **Time Limits**: Maximum 2-hour scan duration
- **Rate Limiting**: Minimum 500 packets/second (nmap)
- **Host Timeout**: 15 minutes per host maximum
- **Retry Limits**: Single retry attempt only
- **Range Validation**: Only RFC1918 private ranges

### Operational Limits

- **Consent Required**: Mandatory authorization before scan
- **Scope Validation**: Only scan authorized ranges
- **Audit Logging**: All actions logged with consent ID
- **Abort Capability**: Long button press to abort

## Network Impact

### Expected Impact

- **Bandwidth**: Minimal (< 1 Mbps during scan)
- **Latency**: Negligible on modern networks
- **Device Load**: Minimal on scanned devices
- **Log Generation**: Normal security logs

### Monitoring Recommendations

- Monitor firewall logs during scan
- Check IDS/IPS alerts (may trigger on port scans)
- Review network traffic patterns
- Verify no service disruption

## Legal Considerations

### Authorization

- **Written Consent**: Required via portal
- **Scope Definition**: Clear CIDR ranges specified
- **Contact Information**: Required for accountability
- **Audit Trail**: Consent ID tracked throughout

### Compliance

- **GDPR**: No personal data collection
- **PCI DSS**: Safe for PCI environments (with approval)
- **HIPAA**: Safe for healthcare networks (with approval)
- **Corporate Policy**: Follow client security policies

## Best Practices

### Pre-Scan

1. Obtain explicit written consent
2. Define clear scan scope
3. Notify network administrators
4. Schedule during maintenance window (optional)

### During Scan

1. Monitor device status
2. Watch for network alerts
3. Be available for questions
4. Document any issues

### Post-Scan

1. Verify scan completion
2. Review report for accuracy
3. Share results securely
4. Archive consent records

## Incident Response

### If Issues Occur

1. **Abort Scan**: Long press button or power cycle
2. **Document Issue**: Note what happened
3. **Contact Support**: Reach out to YFITG
4. **Review Logs**: Check device logs for details

### Common False Positives

- IDS/IPS alerts on port scans (expected)
- Firewall logs showing connection attempts (normal)
- Security tools flagging reconnaissance (expected)
- Network monitoring alerts (normal)

## Disclaimer

This scanning tool is provided "as-is" for authorized network assessments only. Users are responsible for:

- Obtaining proper authorization
- Complying with local laws and regulations
- Following organizational security policies
- Using the tool responsibly

YFITG is not responsible for misuse or unauthorized scanning.

