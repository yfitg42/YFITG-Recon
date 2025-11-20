"""
Local LLM Summarizer - Generates executive summaries using on-device LLM.
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Try to import llama-cpp-python
try:
    from llama_cpp import Llama
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    logger.warning("llama-cpp-python not available, will use fallback API")


class LLMSummarizer:
    """Generates executive summaries using local LLM."""
    
    def __init__(self, config: dict):
        self.config = config
        self.model_path = config.get('model_path')
        self.threads = config.get('threads', 4)
        self.fallback_api = config.get('fallback_api')
        
        self.model = None
        if LLAMA_AVAILABLE and self.model_path and Path(self.model_path).exists():
            self._load_model()
    
    def _load_model(self):
        """Load the local LLM model."""
        try:
            logger.info(f"Loading LLM model from {self.model_path}")
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=2048,
                n_threads=self.threads,
                verbose=False
            )
            logger.info("LLM model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load LLM model: {e}")
            self.model = None
    
    def summarize(self, scan_results: dict) -> str:
        """Generate executive summary from scan results."""
        if self.model:
            return self._local_summarize(scan_results)
        elif self.fallback_api:
            return self._api_summarize(scan_results)
        else:
            return self._fallback_summarize(scan_results)
    
    def _local_summarize(self, scan_results: dict) -> str:
        """Generate summary using local LLM."""
        try:
            # Format scan results as context
            context = self._format_context(scan_results)
            
            prompt = f"""You are a cybersecurity consultant writing an executive summary for a network security assessment.

Scan Results:
{context}

Write a concise, business-friendly executive summary (2-3 paragraphs) that:
1. Highlights the most critical security findings
2. Explains the business impact in non-technical terms
3. Provides high-level recommendations

Executive Summary:"""
            
            response = self.model(
                prompt,
                max_tokens=500,
                temperature=0.7,
                stop=["\n\n\n", "Scan Results:"]
            )
            
            summary = response['choices'][0]['text'].strip()
            return summary
        
        except Exception as e:
            logger.error(f"Error generating local summary: {e}")
            return self._fallback_summarize(scan_results)
    
    def _api_summarize(self, scan_results: dict) -> str:
        """Generate summary using fallback API."""
        try:
            import requests
            
            context = self._format_context(scan_results)
            
            response = requests.post(
                self.fallback_api,
                json={
                    'context': context,
                    'type': 'executive_summary'
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('summary', self._fallback_summarize(scan_results))
            else:
                logger.warning(f"API summarization failed: {response.status_code}")
                return self._fallback_summarize(scan_results)
        
        except Exception as e:
            logger.error(f"Error calling summarization API: {e}")
            return self._fallback_summarize(scan_results)
    
    def _fallback_summarize(self, scan_results: dict) -> str:
        """Generate a basic summary without LLM."""
        summary = scan_results.get('summary', {})
        
        text = f"""Network Security Assessment Summary

This assessment identified {summary.get('total_hosts', 0)} active hosts on your network with {summary.get('open_ports', 0)} open ports and services.

Security Findings:
- High Severity Issues: {summary.get('high_severity', 0)}
- Medium Severity Issues: {summary.get('medium_severity', 0)}
- Low Severity Issues: {summary.get('low_severity', 0)}

The most critical findings include exposed services, outdated software versions, and potential configuration weaknesses that could be exploited by attackers. We recommend addressing high-severity issues immediately and implementing a regular security review process."""
        
        return text
    
    def _format_context(self, scan_results: dict) -> str:
        """Format scan results as text context."""
        lines = []
        
        summary = scan_results.get('summary', {})
        lines.append(f"Total Hosts: {summary.get('total_hosts', 0)}")
        lines.append(f"Open Ports: {summary.get('open_ports', 0)}")
        lines.append(f"High Severity: {summary.get('high_severity', 0)}")
        lines.append(f"Medium Severity: {summary.get('medium_severity', 0)}")
        lines.append(f"Low Severity: {summary.get('low_severity', 0)}")
        lines.append("")
        
        # List key findings
        hosts = scan_results.get('hosts', [])[:10]  # Limit to first 10 hosts
        for host in hosts:
            lines.append(f"Host {host.get('ip', 'unknown')}:")
            for port in host.get('ports', [])[:5]:  # Limit to first 5 ports
                service = port.get('service', 'unknown')
                product = port.get('product', '')
                version = port.get('version', '')
                if product or version:
                    lines.append(f"  - Port {port.get('port')} ({service}): {product} {version}")
                else:
                    lines.append(f"  - Port {port.get('port')} ({service})")
        
        # TLS issues
        tls_issues = scan_results.get('tls_issues', [])[:5]
        if tls_issues:
            lines.append("\nTLS/SSL Issues:")
            for issue in tls_issues:
                lines.append(f"  - {issue.get('host')}:{issue.get('port')} - {issue.get('issue')}")
        
        return "\n".join(lines)

