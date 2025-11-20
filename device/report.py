"""
Report Generator - Creates YFITG-branded PDF reports.
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict

import jinja2
import markdown
from weasyprint import HTML, CSS

from llm_summarizer import LLMSummarizer

logger = logging.getLogger(__name__)

# YFITG Brand Colors
YFITG_COLORS = {
    'primary': '#011c40',
    'secondary': '#1e3877',
    'accent': '#2675a6',
    'text': '#333333',
    'background': '#ffffff'
}


class ReportGenerator:
    """Generates branded PDF reports from scan results."""
    
    def __init__(self):
        self.template_dir = Path("/opt/yfitg-scout/templates")
        self.output_dir = Path("/opt/yfitg-scout/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.llm = None  # Will be initialized with config if needed
    
    def generate(self, results: dict, device_id: str, consent_id: str = None) -> Path:
        """Generate PDF report from scan results."""
        logger.info("Generating PDF report...")
        
        # Initialize LLM if not already done
        if not self.llm:
            # Load config for LLM
            try:
                import json
                with open("/opt/yfitg-scout/.config.json", 'r') as f:
                    config = json.load(f)
                    self.llm = LLMSummarizer(config.get('llm', {}))
            except:
                self.llm = LLMSummarizer({})
        
        # Generate executive summary
        executive_summary = self.llm.summarize(results)
        results['executive_summary'] = executive_summary
        
        # Generate HTML from template
        html_content = self._render_html(results, device_id, consent_id)
        
        # Convert HTML to PDF
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"report_{device_id}_{timestamp}.pdf"
        pdf_path = self.output_dir / pdf_filename
        
        try:
            HTML(string=html_content).write_pdf(
                pdf_path,
                stylesheets=[CSS(string=self._get_css())]
            )
            logger.info(f"PDF report generated: {pdf_path}")
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise
        
        # Save JSON metadata
        json_filename = f"report_{device_id}_{timestamp}.json"
        json_path = self.output_dir / json_filename
        
        metadata = {
            'device_id': device_id,
            'consent_id': consent_id,
            'timestamp': timestamp,
            'summary': results.get('summary', {}),
            'report_hash': self._calculate_hash(pdf_path)
        }
        
        with open(json_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return pdf_path
    
    def _render_html(self, results: dict, device_id: str, consent_id: str) -> str:
        """Render HTML from template."""
        template_path = self.template_dir / "report.html.j2"
        
        if not template_path.exists():
            # Use default template
            return self._default_template(results, device_id, consent_id)
        
        try:
            with open(template_path, 'r') as f:
                template_str = f.read()
            
            template = jinja2.Template(template_str)
            return template.render(
                results=results,
                device_id=device_id,
                consent_id=consent_id,
                colors=YFITG_COLORS,
                timestamp=datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")
            )
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return self._default_template(results, device_id, consent_id)
    
    def _default_template(self, results: dict, device_id: str, consent_id: str) -> str:
        """Generate default HTML template."""
        summary = results.get('summary', {})
        executive_summary = results.get('executive_summary', 'No summary available.')
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>YFITG Network Security Assessment</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 40px; color: {YFITG_COLORS['text']};">
    <div style="background: {YFITG_COLORS['primary']}; color: white; padding: 20px; margin-bottom: 30px;">
        <h1 style="margin: 0;">YFITG Network Security Assessment</h1>
        <p style="margin: 5px 0 0 0;">Device ID: {device_id} | Report Generated: {datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")}</p>
    </div>
    
    <h2 style="color: {YFITG_COLORS['secondary']}; border-bottom: 2px solid {YFITG_COLORS['accent']}; padding-bottom: 10px;">Executive Summary</h2>
    <div style="background: #f5f5f5; padding: 20px; margin: 20px 0; border-left: 4px solid {YFITG_COLORS['accent']};">
        {markdown.markdown(executive_summary)}
    </div>
    
    <h2 style="color: {YFITG_COLORS['secondary']}; border-bottom: 2px solid {YFITG_COLORS['accent']}; padding-bottom: 10px;">Severity Overview</h2>
    <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
        <tr style="background: {YFITG_COLORS['primary']}; color: white;">
            <th style="padding: 12px; text-align: left;">Metric</th>
            <th style="padding: 12px; text-align: right;">Count</th>
        </tr>
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">Total Hosts Discovered</td>
            <td style="padding: 10px; text-align: right;">{summary.get('total_hosts', 0)}</td>
        </tr>
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">Open Ports</td>
            <td style="padding: 10px; text-align: right;">{summary.get('open_ports', 0)}</td>
        </tr>
        <tr style="border-bottom: 1px solid #ddd; background: #ffebee;">
            <td style="padding: 10px;"><strong>High Severity Issues</strong></td>
            <td style="padding: 10px; text-align: right;"><strong>{summary.get('high_severity', 0)}</strong></td>
        </tr>
        <tr style="border-bottom: 1px solid #ddd; background: #fff3e0;">
            <td style="padding: 10px;">Medium Severity Issues</td>
            <td style="padding: 10px; text-align: right;">{summary.get('medium_severity', 0)}</td>
        </tr>
        <tr style="border-bottom: 1px solid #ddd;">
            <td style="padding: 10px;">Low Severity Issues</td>
            <td style="padding: 10px; text-align: right;">{summary.get('low_severity', 0)}</td>
        </tr>
    </table>
    
    <h2 style="color: {YFITG_COLORS['secondary']}; border-bottom: 2px solid {YFITG_COLORS['accent']}; padding-bottom: 10px;">Findings by Host</h2>
"""
        
        # Add host findings
        for host in results.get('hosts', [])[:20]:  # Limit to first 20 hosts
            html += f"""
    <div style="margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
        <h3 style="color: {YFITG_COLORS['accent']}; margin-top: 0;">{host.get('ip', 'Unknown')} {f"({host.get('hostname', '')})" if host.get('hostname') else ""}</h3>
        <p><strong>State:</strong> {host.get('state', 'unknown')}</p>
        <h4>Open Ports & Services:</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr style="background: #f5f5f5;">
                <th style="padding: 8px; text-align: left;">Port</th>
                <th style="padding: 8px; text-align: left;">Service</th>
                <th style="padding: 8px; text-align: left;">Product/Version</th>
            </tr>
"""
            for port in host.get('ports', []):
                product = f"{port.get('product', '')} {port.get('version', '')}".strip()
                html += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 8px;">{port.get('port', '')}/{port.get('protocol', '')}</td>
                <td style="padding: 8px;">{port.get('service', 'unknown')}</td>
                <td style="padding: 8px;">{product if product else 'N/A'}</td>
            </tr>
"""
            
            # Web findings
            if host.get('web_findings'):
                html += """
        </table>
        <h4>Web Server Findings:</h4>
        <ul>
"""
                for finding in host.get('web_findings', [])[:5]:
                    html += f"<li>{finding.get('description', 'N/A')}</li>"
                html += "</ul>"
            else:
                html += "</table>"
            
            html += "</div>"
        
        # TLS Issues
        tls_issues = results.get('tls_issues', [])
        if tls_issues:
            html += f"""
    <h2 style="color: {YFITG_COLORS['secondary']}; border-bottom: 2px solid {YFITG_COLORS['accent']}; padding-bottom: 10px;">TLS/SSL Certificate Issues</h2>
    <ul>
"""
            for issue in tls_issues[:10]:
                html += f"<li><strong>{issue.get('host')}:{issue.get('port')}</strong> - {issue.get('issue')}: {issue.get('details', '')}</li>"
            html += "</ul>"
        
        # Footer
        html += f"""
    <div style="margin-top: 40px; padding-top: 20px; border-top: 2px solid {YFITG_COLORS['accent']}; color: #666; font-size: 12px;">
        <p><strong>Disclaimer:</strong> This assessment was performed using non-intrusive scanning techniques. No exploitation, password attempts, or network disruption occurred during this scan.</p>
        <p>© {datetime.utcnow().year} YFITG. All rights reserved. Confidential - For authorized use only.</p>
    </div>
</body>
</html>
"""
        return html
    
    def _get_css(self) -> str:
        """Get CSS styles for PDF."""
        return """
        @page {
            size: letter;
            margin: 1in;
        }
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
        }
        table {
            page-break-inside: avoid;
        }
        h2 {
            page-break-after: avoid;
        }
    """
    
    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of report file."""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

