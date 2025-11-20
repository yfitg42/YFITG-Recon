"""
Report Uploader - Securely uploads reports to collector API.
"""

import hashlib
import json
import logging
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class ReportUploader:
    """Handles secure upload of reports to collector API."""
    
    def __init__(self, config: dict):
        self.api_url = config.get('api_url')
        self.api_token = config.get('api_token')
        self.timeout = 300  # 5 minutes for large uploads
    
    def upload(self, report_path: Path, consent_id: Optional[str] = None) -> bool:
        """Upload report PDF and metadata to collector API."""
        if not self.api_url:
            logger.error("No API URL configured")
            return False
        
        if not report_path.exists():
            logger.error(f"Report file not found: {report_path}")
            return False
        
        try:
            # Calculate file hash
            file_hash = self._calculate_hash(report_path)
            
            # Prepare metadata
            metadata = {
                'consent_id': consent_id,
                'filename': report_path.name,
                'file_hash': file_hash,
                'file_size': report_path.stat().st_size
            }
            
            # Load JSON metadata if exists
            json_path = report_path.with_suffix('.json')
            if json_path.exists():
                with open(json_path, 'r') as f:
                    metadata.update(json.load(f))
            
            # Prepare multipart form data
            with open(report_path, 'rb') as f:
                files = {
                    'report': (report_path.name, f, 'application/pdf')
                }
                data = {
                    'metadata': json.dumps(metadata)
                }
                headers = {
                    'Authorization': f'Bearer {self.api_token}'
                }
                
                logger.info(f"Uploading report to {self.api_url}...")
                response = requests.post(
                    self.api_url,
                    files=files,
                    data=data,
                    headers=headers,
                    timeout=self.timeout,
                    verify=True  # Enforce TLS certificate validation
                )
                
                if response.status_code == 200:
                    logger.info("Report uploaded successfully")
                    
                    # Optionally delete local files after successful upload
                    # report_path.unlink()
                    # json_path.unlink() if json_path.exists() else None
                    
                    return True
                else:
                    logger.error(f"Upload failed with status {response.status_code}: {response.text}")
                    return False
        
        except requests.exceptions.Timeout:
            logger.error("Upload timeout - file may be too large or network slow")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Upload error: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during upload: {e}")
            return False
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

