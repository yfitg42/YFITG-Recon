"""
YFITG Report Collector API - FastAPI server for receiving scan reports.
"""

import hashlib
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, Security, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="YFITG Report Collector API",
    description="API for receiving and storing network security assessment reports",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Storage configuration
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "/var/yfitg-scout/reports"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# API token (in production, use proper authentication)
API_TOKEN = os.getenv("API_TOKEN", "change-me-in-production")


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """Verify API token."""
    if credentials.credentials != API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid API token")
    return True


class ReportMetadata(BaseModel):
    """Report metadata model."""
    consent_id: Optional[str] = None
    device_id: Optional[str] = None
    filename: Optional[str] = None
    file_hash: Optional[str] = None
    file_size: Optional[int] = None
    timestamp: Optional[str] = None
    summary: Optional[dict] = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "YFITG Report Collector API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/reports")
async def upload_report(
    report: UploadFile = File(...),
    metadata: str = Form(...),
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """
    Upload a scan report PDF with metadata.
    
    Requires Bearer token authentication.
    Accepts multipart/form-data with:
    - report: PDF file
    - metadata: JSON string with report metadata
    """
    # Verify token
    verify_token(credentials)
    
    try:
        # Parse metadata
        try:
            metadata_obj = json.loads(metadata)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid metadata JSON")
        
        # Validate file type
        if not report.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        # Read file content
        content = await report.read()
        file_size = len(content)
        
        # Calculate hash
        file_hash = hashlib.sha256(content).hexdigest()
        
        # Verify hash matches metadata if provided
        if metadata_obj.get('file_hash') and metadata_obj['file_hash'] != file_hash:
            logger.warning(f"Hash mismatch for file {report.filename}")
            # Don't reject, but log warning
        
        # Generate storage filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        consent_id = metadata_obj.get('consent_id', 'unknown')
        device_id = metadata_obj.get('device_id', 'unknown')
        
        filename = f"report_{device_id}_{consent_id}_{timestamp}.pdf"
        file_path = STORAGE_DIR / filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Report saved: {filename} ({file_size} bytes, hash: {file_hash})")
        
        # Save metadata JSON
        metadata_path = file_path.with_suffix('.json')
        metadata_obj.update({
            'received_at': datetime.utcnow().isoformat(),
            'stored_filename': filename,
            'file_hash': file_hash,
            'file_size': file_size
        })
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata_obj, f, indent=2)
        
        # Optionally send notification email
        # send_notification_email(metadata_obj, file_path)
        
        return {
            "success": True,
            "message": "Report received and stored",
            "filename": filename,
            "file_hash": file_hash,
            "file_size": file_size,
            "consent_id": consent_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing report upload: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/reports/{consent_id}")
async def get_report(
    consent_id: str,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """Get report metadata by consent ID."""
    verify_token(credentials)
    
    # Search for report with this consent_id
    for json_file in STORAGE_DIR.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                metadata = json.load(f)
                if metadata.get('consent_id') == consent_id:
                    pdf_file = json_file.with_suffix('.pdf')
                    if pdf_file.exists():
                        return {
                            "consent_id": consent_id,
                            "metadata": metadata,
                            "file_exists": True,
                            "file_path": str(pdf_file)
                        }
        except Exception as e:
            logger.warning(f"Error reading {json_file}: {e}")
    
    raise HTTPException(status_code=404, detail="Report not found")


@app.get("/reports")
async def list_reports(
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Security(security)
):
    """List recent reports."""
    verify_token(credentials)
    
    reports = []
    for json_file in sorted(STORAGE_DIR.glob("*.json"), reverse=True)[:limit]:
        try:
            with open(json_file, 'r') as f:
                metadata = json.load(f)
                pdf_file = json_file.with_suffix('.pdf')
                reports.append({
                    "consent_id": metadata.get('consent_id'),
                    "device_id": metadata.get('device_id'),
                    "received_at": metadata.get('received_at'),
                    "file_exists": pdf_file.exists(),
                    "summary": metadata.get('summary', {})
                })
        except Exception as e:
            logger.warning(f"Error reading {json_file}: {e}")
    
    return {
        "count": len(reports),
        "reports": reports
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

