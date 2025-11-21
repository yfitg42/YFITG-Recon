#!/usr/bin/env python3
"""
YFITG Network Scout - Main Orchestrator
Handles MQTT communication, scan coordination, and report generation.
"""

import json
import logging
import os
import signal
import sys
import time
from pathlib import Path
from typing import Optional

import paho.mqtt.client as mqtt

from scanner import ScanOrchestrator
from display import DisplayController
from button import ButtonHandler
from report import ReportGenerator
from uploader import ReportUploader


def get_base_dir() -> Path:
    """Get the base directory for YFITG Scout files.
    
    Checks in order:
    1. YFITG_SCOUT_BASE_DIR environment variable
    2. /opt/yfitg-scout (Linux production)
    3. Current directory (development)
    """
    # Check environment variable first
    env_dir = os.environ.get('YFITG_SCOUT_BASE_DIR')
    if env_dir:
        return Path(env_dir)
    
    # Check Linux production path
    linux_path = Path('/opt/yfitg-scout')
    if linux_path.exists():
        return linux_path
    
    # Fall back to current directory for development
    return Path(__file__).parent.absolute()


BASE_DIR = get_base_dir()
logger = logging.getLogger(__name__)

# Configure logging
log_dir = BASE_DIR / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / 'scout.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)


class ScoutDevice:
    """Main device orchestrator."""
    
    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = str(BASE_DIR / '.config.json')
        self.config = self._load_config(config_path)
        self.running = True
        self.current_scan: Optional[ScanOrchestrator] = None
        self.display = DisplayController(self.config.get('display', {}))
        self.button = ButtonHandler(
            self.config.get('button', {}),
            on_short_press=self._handle_short_press,
            on_long_press=self._handle_long_press
        )
        self.uploader = ReportUploader(self.config.get('collector', {}))
        self.report_gen = ReportGenerator()
        
        # MQTT client setup
        self.mqtt_client = mqtt.Client(
            client_id=f"scout-{self.config['device_id']}",
            protocol=mqtt.MQTTv5
        )
        self._setup_mqtt()
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config: {e}")
            sys.exit(1)
    
    def _setup_mqtt(self):
        """Configure MQTT client with TLS."""
        mqtt_config = self.config.get('mqtt', {})
        
        # TLS configuration
        if mqtt_config.get('ca_cert'):
            self.mqtt_client.tls_set(
                ca_certs=mqtt_config['ca_cert'],
                certfile=mqtt_config.get('client_cert'),
                keyfile=mqtt_config.get('client_key'),
                tls_version=2  # TLS 1.2
            )
        
        self.mqtt_client.username_pw_set(
            mqtt_config.get('username'),
            mqtt_config.get('password')
        )
        
        self.mqtt_client.on_connect = self._on_mqtt_connect
        self.mqtt_client.on_message = self._on_mqtt_message
        self.mqtt_client.on_disconnect = self._on_mqtt_disconnect
    
    def _on_mqtt_connect(self, client, userdata, flags, rc, properties=None):
        """Handle MQTT connection."""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            topic = f"device/{self.config['device_id']}/start"
            client.subscribe(topic)
            logger.info(f"Subscribed to {topic}")
            self.display.show_idle()
        else:
            logger.error(f"MQTT connection failed with code {rc}")
            self.display.show_error("MQTT Connection Failed")
    
    def _on_mqtt_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        try:
            payload = json.loads(msg.payload.decode())
            logger.info(f"Received start command: {payload}")
            self._start_scan(payload)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in MQTT message: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def _on_mqtt_disconnect(self, client, userdata, rc, properties=None):
        """Handle MQTT disconnection."""
        logger.warning("Disconnected from MQTT broker")
    
    def _start_scan(self, payload: dict):
        """Start a new scan based on MQTT payload."""
        if self.current_scan and self.current_scan.is_running():
            logger.warning("Scan already in progress, ignoring start command")
            return
        
        # Validate consent
        consent_id = payload.get('consent_id')
        if not consent_id:
            logger.error("No consent_id in payload")
            return
        
        # Extract scan scope
        scope = payload.get('scope', {})
        cidr_ranges = scope.get('cidr', [])
        http_hosts = scope.get('http_hosts', [])
        
        # Validate ranges are RFC1918
        allowed_ranges = self.config.get('scanning', {}).get('allowed_ranges', [])
        if not self._validate_ranges(cidr_ranges, allowed_ranges):
            logger.error("Invalid CIDR ranges in scope")
            return
        
        logger.info(f"Starting scan with consent_id: {consent_id}")
        self.display.show_scanning()
        
        # Create scan orchestrator
        self.current_scan = ScanOrchestrator(
            cidr_ranges=cidr_ranges,
            http_hosts=http_hosts,
            config=self.config.get('scanning', {}),
            on_progress=self._on_scan_progress,
            on_complete=self._on_scan_complete,
            on_error=self._on_scan_error
        )
        
        # Start scan in background thread
        import threading
        scan_thread = threading.Thread(target=self.current_scan.run, daemon=True)
        scan_thread.start()
    
    def _validate_ranges(self, ranges: list, allowed: list) -> bool:
        """Validate CIDR ranges are within allowed RFC1918 ranges."""
        # Simplified validation - in production, use ipaddress module
        for r in ranges:
            if not any(r.startswith(prefix) for prefix in ['10.', '172.', '192.168.']):
                return False
        return True
    
    def _on_scan_progress(self, phase: str, progress: float):
        """Handle scan progress updates."""
        logger.info(f"Scan progress: {phase} - {progress:.1f}%")
        self.display.update_scan_progress(phase, progress)
    
    def _on_scan_complete(self, results: dict):
        """Handle scan completion."""
        logger.info("Scan completed, generating report...")
        self.display.show_processing()
        
        try:
            # Generate report
            report_path = self.report_gen.generate(
                results=results,
                device_id=self.config['device_id'],
                consent_id=results.get('consent_id')
            )
            
            # Upload report
            logger.info("Uploading report...")
            upload_success = self.uploader.upload(report_path, results.get('consent_id'))
            
            if upload_success:
                self.display.show_complete()
                logger.info("Report uploaded successfully")
            else:
                self.display.show_error("Upload Failed")
                logger.error("Report upload failed")
            
        except Exception as e:
            logger.error(f"Error generating/uploading report: {e}")
            self.display.show_error("Report Generation Failed")
        finally:
            self.current_scan = None
    
    def _on_scan_error(self, error: str):
        """Handle scan errors."""
        logger.error(f"Scan error: {error}")
        self.display.show_error("Scan Error")
        self.current_scan = None
    
    def _handle_short_press(self):
        """Handle short button press - show status."""
        if self.current_scan:
            status = self.current_scan.get_status()
            self.display.show_status(status)
        else:
            self.display.show_idle()
    
    def _handle_long_press(self):
        """Handle long button press - abort scan."""
        if self.current_scan and self.current_scan.is_running():
            logger.warning("Aborting scan due to long button press")
            self.current_scan.abort()
            self.display.show_error("Scan Aborted")
            self.current_scan = None
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        if self.current_scan:
            self.current_scan.abort()
        self.mqtt_client.disconnect()
        sys.exit(0)
    
    def run(self):
        """Main run loop."""
        logger.info("Starting YFITG Network Scout...")
        
        # Connect to MQTT broker
        mqtt_config = self.config.get('mqtt', {})
        try:
            self.mqtt_client.connect(
                mqtt_config['broker'],
                mqtt_config.get('port', 8883),
                60
            )
            self.mqtt_client.loop_start()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            sys.exit(1)
        
        # Start button handler
        self.button.start()
        
        # Main loop
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            logger.info("Shutdown complete")


if __name__ == "__main__":
    # Log directory already created in logging setup
    logger.info(f"Using base directory: {BASE_DIR}")
    
    scout = ScoutDevice()
    scout.run()

