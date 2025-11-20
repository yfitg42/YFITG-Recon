# YFITG Report Collector API

FastAPI server for receiving and storing network security assessment reports.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
- `API_TOKEN` - Bearer token for authentication
- `STORAGE_DIR` - Directory to store reports (default: `/var/yfitg-scout/reports`)

3. Run server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Or with auto-reload for development:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /reports
Upload a report PDF with metadata.

**Authentication:** Bearer token required

**Content-Type:** multipart/form-data

**Form Fields:**
- `report`: PDF file
- `metadata`: JSON string with metadata

**Response:**
```json
{
  "success": true,
  "message": "Report received and stored",
  "filename": "report_scout-001_consent-id_20231201_120000.pdf",
  "file_hash": "...",
  "file_size": 123456,
  "consent_id": "..."
}
```

### GET /reports/{consent_id}
Get report metadata by consent ID.

**Authentication:** Bearer token required

### GET /reports
List recent reports.

**Authentication:** Bearer token required

**Query Parameters:**
- `limit`: Maximum number of reports to return (default: 50)

## Production Deployment

For production, consider:
- Using a reverse proxy (nginx) with SSL
- Implementing proper database storage instead of filesystem
- Adding email notifications
- Setting up proper logging and monitoring
- Using environment-based configuration

