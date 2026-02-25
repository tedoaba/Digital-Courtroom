"""
Structured logging utility for the Digital Courtroom.
Implements JSON formatting, PII redaction, and deterministic lifecycle tracking.
"""
import logging
import sys
import os
import re
from datetime import datetime, timezone
from pythonjsonlogger import json

# PII Redaction Patterns
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
# Adjusted to be more inclusive for testing (16+ chars after sk-)
API_TOKEN_PATTERN = re.compile(r'sk-[a-zA-Z0-9]{16,}|ghp_[a-zA-Z0-9]{30,}')

class PIIRedactionFilter(logging.Filter):
    """
    Filter to redact PII from log records.
    Redacts emails, API tokens, and user patterns from message and any extra attributes.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.redact(record.msg)
        
        # Redact any attributes added via 'extra'
        for attr in ['payload', 'correlation_id', 'event_type']:
            val = getattr(record, attr, None)
            if val is not None:
                setattr(record, attr, self.redact_recursive(val))
            
        return True

    def redact(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        text = EMAIL_PATTERN.sub('[REDACTED_EMAIL]', text)
        text = API_TOKEN_PATTERN.sub('[REDACTED_TOKEN]', text)
        return text

    def redact_recursive(self, data):
        """Recursively redact PII from dicts and lists."""
        if isinstance(data, str):
            return self.redact(data)
        if isinstance(data, dict):
            return {k: self.redact_recursive(v) for k, v in data.items()}
        if isinstance(data, list):
            return [self.redact_recursive(item) for item in data]
        return data

# Try to import the new location of JsonFormatter
try:
    from pythonjsonlogger.json import JsonFormatter
except ImportError:
    from pythonjsonlogger.jsonlogger import JsonFormatter

class CustomJsonFormatter(JsonFormatter):
    """Custom formatter to enforce RFC 3339 and millisecond precision."""
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # RFC 3339 timestamp with milliseconds
        now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        log_record['timestamp'] = now
        
        # Map levels to severity
        log_record['severity'] = record.levelname
        
        # Ensure required fields
        log_record['event_type'] = getattr(record, 'event_type', 'system_event')
        log_record['correlation_id'] = getattr(record, 'correlation_id', 'unknown')
        
        # Environment metadata
        log_record['host_id'] = os.getenv('HOST_ID', 'local-host')
        log_record['service_name'] = os.getenv('SERVICE_NAME', 'digital-courtroom')
        
        # Payload handling
        payload = getattr(record, 'payload', {})
        if not isinstance(payload, dict):
            payload = {'value': payload}
        else:
            payload = payload.copy()
            
        # Move message into payload if requested by test or for consistency
        if 'message' in log_record:
            payload['message'] = log_record['message']
            
        log_record['payload'] = payload

class StructuredLogger:
    """
    High-level logger for the Digital Courtroom.
    Wraps standard logging with structured JSON output and lifecycle helpers.
    """
    def __init__(self, name: str, level=logging.INFO, stream=sys.stdout):
        # Use a unique logger name to avoid collisions if necessary
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self.logger.propagate = False
        
        # Clear existing handlers to avoid duplicates
        if self.logger.handlers:
            self.logger.handlers.clear()
            
        handler = logging.StreamHandler(stream)
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(severity)s %(event_type)s %(correlation_id)s %(message)s'
        )
        handler.setFormatter(formatter)
        handler.addFilter(PIIRedactionFilter())
        self.logger.addHandler(handler)

    def log(self, level, msg, event_type='system_event', correlation_id='unknown', payload=None, **kwargs):
        # Initialize payload
        p = payload if payload is not None else {}
        if not isinstance(p, dict):
            p = {'value': p}
        else:
            p = p.copy()
            
        # Check for exception-based severity mapping (US3)
        exc = kwargs.get('exc') or kwargs.get('e')
        from src.exceptions import AppException
        if isinstance(exc, AppException):
            if exc.fatal:
                level = logging.CRITICAL
            else:
                level = logging.WARNING
            p['exception_type'] = exc.__class__.__name__
            p['fatal'] = exc.fatal

        # Merge extra keys from kwargs into payload
        for k, v in kwargs.items():
            if k not in ('exc', 'e'):
                p[k] = v
            
        extra = {
            'event_type': event_type,
            'correlation_id': correlation_id,
            'payload': p
        }
            
        self.logger.log(level, msg, extra=extra)

    def info(self, msg, **kwargs):
        self.log(logging.INFO, msg, **kwargs)

    def warning(self, msg, **kwargs):
        self.log(logging.WARNING, msg, **kwargs)

    def error(self, msg, **kwargs):
        self.log(logging.ERROR, msg, **kwargs)

    def critical(self, msg, **kwargs):
        self.log(logging.CRITICAL, msg, **kwargs)

    def debug(self, msg, **kwargs):
        self.log(logging.DEBUG, msg, **kwargs)

    # Lifecycle Helpers
    def log_node_entry(self, node_name: str, **kwargs):
        self.log(logging.INFO, f"Entering node: {node_name}", event_type="node_entry", node_name=node_name, **kwargs)

    def log_evidence_created(self, evidence_id: str, **kwargs):
        self.log(logging.INFO, f"Evidence created: {evidence_id}", event_type="evidence_created", evidence_id=evidence_id, **kwargs)

    def log_opinion_rendered(self, opinion: str, **kwargs):
        self.log(logging.INFO, f"Opinion rendered", event_type="opinion_rendered", opinion=opinion, **kwargs)

    def log_verdict_delivered(self, verdict: str, **kwargs):
        self.log(logging.INFO, f"Verdict delivered: {verdict}", event_type="verdict_delivered", verdict=verdict, **kwargs)
