"""
Scan Orchestrator - Coordinates nmap, nikto, and TLS scanning.
"""

import json
import logging
import subprocess
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

import nmap
from cryptography import x509
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class ScanOrchestrator:
    """Orchestrates network scanning operations."""
    
    def __init__(
        self,
        cidr_ranges: List[str],
        http_hosts: List[str],
        config: dict,
        on_progress: Optional[Callable[[str, float], None]] = None,
        on_complete: Optional[Callable[[dict], None]] = None,
        on_error: Optional[Callable[[str], None]] = None
    ):
        self.cidr_ranges = cidr_ranges
        self.http_hosts = http_hosts
        self.config = config
        self.on_progress = on_progress
        self.on_complete = on_complete
        self.on_error = on_error
        
        self.running = False
        self.aborted = False
        self.results = {
            'start_time': datetime.utcnow().isoformat(),
            'cidr_ranges': cidr_ranges,
            'http_hosts': http_hosts,
            'hosts': [],
            'tls_issues': [],
            'summary': {
                'total_hosts': 0,
                'open_ports': 0,
                'high_severity': 0,
                'medium_severity': 0,
                'low_severity': 0
            }
        }
        
        self.max_duration = config.get('max_duration_hours', 2) * 3600
        self.start_time = None
    
    def is_running(self) -> bool:
        """Check if scan is currently running."""
        return self.running
    
    def abort(self):
        """Abort the current scan."""
        self.aborted = True
        logger.warning("Scan aborted by user")
    
    def get_status(self) -> dict:
        """Get current scan status."""
        if not self.running:
            return {'status': 'idle'}
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        return {
            'status': 'scanning',
            'elapsed_seconds': int(elapsed),
            'hosts_scanned': len(self.results['hosts']),
            'phase': 'discovery'  # Simplified
        }
    
    def run(self):
        """Execute the full scan workflow."""
        self.running = True
        self.start_time = time.time()
        
        try:
            # Phase 1: Network Discovery
            if self.aborted:
                return
            
            self._update_progress("Discovery", 10.0)
            nmap_results = self._run_nmap_scan()
            
            # Phase 2: Web Server Scanning
            if self.aborted:
                return
            
            self._update_progress("Web Scanning", 50.0)
            nikto_results = self._run_nikto_scan()
            
            # Phase 3: TLS Validation
            if self.aborted:
                return
            
            self._update_progress("TLS Validation", 80.0)
            tls_results = self._run_tls_validation()
            
            # Phase 4: Aggregate Results
            if self.aborted:
                return
            
            self._update_progress("Aggregating", 90.0)
            self._aggregate_results(nmap_results, nikto_results, tls_results)
            
            # Complete
            self.results['end_time'] = datetime.utcnow().isoformat()
            self.results['duration_seconds'] = int(time.time() - self.start_time)
            
            self._update_progress("Complete", 100.0)
            
            if self.on_complete:
                self.on_complete(self.results)
        
        except Exception as e:
            logger.error(f"Scan error: {e}", exc_info=True)
            if self.on_error:
                self.on_error(str(e))
        finally:
            self.running = False
    
    def _update_progress(self, phase: str, percent: float):
        """Update scan progress."""
        if self.on_progress:
            self.on_progress(phase, percent)
    
    def _run_nmap_scan(self) -> dict:
        """Run nmap port scan."""
        logger.info("Starting nmap scan...")
        nm = nmap.PortScanner()
        
        results = {
            'hosts': [],
            'scan_time': datetime.utcnow().isoformat()
        }
        
        for cidr in self.cidr_ranges:
            if self.aborted:
                break
            
            try:
                # Safe nmap scan parameters
                nm.scan(
                    hosts=cidr,
                    arguments='-sS -sV --version-light --open --max-retries 1 '
                             '--host-timeout 15m --min-rate 500 --defeat-rst-ratelimit'
                )
                
                for host in nm.all_hosts():
                    if self.aborted:
                        break
                    
                    host_data = {
                        'ip': host,
                        'hostname': nm[host].hostname(),
                        'state': nm[host].state(),
                        'ports': []
                    }
                    
                    for proto in nm[host].all_protocols():
                        ports = nm[host][proto].keys()
                        for port in ports:
                            port_data = nm[host][proto][port]
                            host_data['ports'].append({
                                'port': port,
                                'protocol': proto,
                                'state': port_data['state'],
                                'service': port_data.get('name', 'unknown'),
                                'product': port_data.get('product', ''),
                                'version': port_data.get('version', ''),
                                'extrainfo': port_data.get('extrainfo', '')
                            })
                    
                    results['hosts'].append(host_data)
                    self.results['summary']['total_hosts'] += 1
                    self.results['summary']['open_ports'] += len(host_data['ports'])
            
            except Exception as e:
                logger.error(f"Error scanning {cidr}: {e}")
        
        return results
    
    def _run_nikto_scan(self) -> dict:
        """Run nikto web server scan."""
        logger.info("Starting nikto scan...")
        results = {
            'findings': [],
            'scan_time': datetime.utcnow().isoformat()
        }
        
        for host in self.http_hosts:
            if self.aborted:
                break
            
            try:
                # Run nikto with JSON output
                cmd = ['nikto', '-h', host, '-Format', 'json', '-output', '-']
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if process.returncode == 0:
                    try:
                        nikto_data = json.loads(process.stdout)
                        if 'host' in nikto_data:
                            for item in nikto_data.get('host', []):
                                results['findings'].append({
                                    'host': host,
                                    'port': item.get('port', ''),
                                    'method': item.get('method', ''),
                                    'uri': item.get('uri', ''),
                                    'description': item.get('description', ''),
                                    'severity': self._classify_nikto_severity(item)
                                })
                    except json.JSONDecodeError:
                        logger.warning(f"Could not parse nikto JSON for {host}")
            
            except subprocess.TimeoutExpired:
                logger.warning(f"Nikto scan timeout for {host}")
            except Exception as e:
                logger.error(f"Error running nikto on {host}: {e}")
        
        return results
    
    def _classify_nikto_severity(self, item: dict) -> str:
        """Classify nikto finding severity."""
        desc = item.get('description', '').lower()
        if any(word in desc for word in ['critical', 'exploit', 'vulnerability']):
            return 'high'
        elif any(word in desc for word in ['warning', 'issue', 'problem']):
            return 'medium'
        return 'low'
    
    def _run_tls_validation(self) -> dict:
        """Validate TLS/SSL certificates."""
        logger.info("Starting TLS validation...")
        results = {
            'issues': [],
            'scan_time': datetime.utcnow().isoformat()
        }
        
        # Check TLS on discovered HTTPS services
        for host_data in self.results.get('hosts', []):
            if self.aborted:
                break
            
            for port_data in host_data.get('ports', []):
                if port_data.get('service') in ['https', 'ssl', 'tls']:
                    port = port_data['port']
                    host = host_data['ip']
                    
                    try:
                        cert_issues = self._check_certificate(host, port)
                        if cert_issues:
                            results['issues'].extend(cert_issues)
                    except Exception as e:
                        logger.error(f"Error checking TLS for {host}:{port}: {e}")
        
        return results
    
    def _check_certificate(self, host: str, port: int) -> List[dict]:
        """Check SSL/TLS certificate for issues."""
        issues = []
        
        try:
            import socket
            import ssl
            
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    cert_der = ssock.getpeercert_chain()[0]
                    cert = x509.load_der_x509_certificate(
                        cert_der,
                        default_backend()
                    )
                    
                    # Check expiration
                    now = datetime.utcnow()
                    if cert.not_valid_after.replace(tzinfo=None) < now:
                        issues.append({
                            'host': host,
                            'port': port,
                            'issue': 'expired_certificate',
                            'severity': 'high',
                            'details': f"Certificate expired on {cert.not_valid_after}"
                        })
                    elif (cert.not_valid_after.replace(tzinfo=None) - now).days < 30:
                        issues.append({
                            'host': host,
                            'port': port,
                            'issue': 'certificate_expiring_soon',
                            'severity': 'medium',
                            'details': f"Certificate expires in {(cert.not_valid_after.replace(tzinfo=None) - now).days} days"
                        })
                    
                    # Check protocol version
                    if ssock.version() in ['TLSv1', 'TLSv1.1']:
                        issues.append({
                            'host': host,
                            'port': port,
                            'issue': 'weak_tls_protocol',
                            'severity': 'high',
                            'details': f"Using deprecated TLS version: {ssock.version()}"
                        })
        
        except ssl.SSLError as e:
            issues.append({
                'host': host,
                'port': port,
                'issue': 'ssl_error',
                'severity': 'medium',
                'details': str(e)
            })
        except Exception as e:
            logger.debug(f"Could not check certificate for {host}:{port} - {e}")
        
        return issues
    
    def _aggregate_results(self, nmap_results: dict, nikto_results: dict, tls_results: dict):
        """Aggregate all scan results."""
        # Merge nmap hosts
        self.results['hosts'] = nmap_results.get('hosts', [])
        
        # Add nikto findings to relevant hosts
        for finding in nikto_results.get('findings', []):
            host_ip = finding.get('host')
            for host in self.results['hosts']:
                if host['ip'] == host_ip:
                    if 'web_findings' not in host:
                        host['web_findings'] = []
                    host['web_findings'].append(finding)
                    
                    # Update severity counts
                    severity = finding.get('severity', 'low')
                    if severity == 'high':
                        self.results['summary']['high_severity'] += 1
                    elif severity == 'medium':
                        self.results['summary']['medium_severity'] += 1
                    else:
                        self.results['summary']['low_severity'] += 1
                    break
        
        # Add TLS issues
        self.results['tls_issues'] = tls_results.get('issues', [])
        for issue in self.results['tls_issues']:
            severity = issue.get('severity', 'low')
            if severity == 'high':
                self.results['summary']['high_severity'] += 1
            elif severity == 'medium':
                self.results['summary']['medium_severity'] += 1
            else:
                self.results['summary']['low_severity'] += 1

