"""
Security utilities for web-all.
Provides input validation, SSRF protection, and security helpers.
"""

import re
import socket
from urllib.parse import urlparse
from typing import Optional, Set
from ipaddress import ip_address, IPv4Address, IPv6Address


# Private IP ranges that should be blocked to prevent SSRF
PRIVATE_IP_PATTERNS = [
    r'^127\.',  # localhost
    r'^10\.',   # Class A private
    r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # Class B private
    r'^192\.168\.',  # Class C private
    r'^169\.254\.',  # Link-local
    r'^0\.0\.0\.0',  # All interfaces
    r'^::1$',  # IPv6 localhost
    r'^fc00:',  # IPv6 unique local
    r'^fe80:',  # IPv6 link-local
]


def is_safe_url(url: str, allowed_schemes: Optional[Set[str]] = None) -> bool:
    """
    Validate URL to prevent SSRF attacks.
    
    Args:
        url: URL to validate
        allowed_schemes: Set of allowed URL schemes (default: http, https)
    
    Returns:
        True if URL is safe, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    if allowed_schemes is None:
        allowed_schemes = {'http', 'https'}
    
    try:
        parsed = urlparse(url.strip())
        
        # Check scheme
        if parsed.scheme.lower() not in allowed_schemes:
            return False
        
        # Check hostname exists
        if not parsed.hostname:
            return False
        
        # Block file:// and other dangerous schemes
        if parsed.scheme.lower() in ('file', 'gopher', 'dict', 'ftp'):
            return False
        
        # Check if hostname is an IP address
        hostname = parsed.hostname
        try:
            # Try to resolve hostname to IP
            ip_addr = ip_address(hostname)
            return not is_private_ip(ip_addr)
        except ValueError:
            # Not an IP, check if it resolves to private IP
            try:
                addresses = socket.getaddrinfo(hostname, None)
                for addr in addresses:
                    ip = addr[4][0]
                    try:
                        if is_private_ip(ip_address(ip)):
                            return False
                    except ValueError:
                        continue
                return True
            except socket.gaierror:
                # Cannot resolve - let the request fail naturally
                return True
                
    except Exception:
        return False


def is_private_ip(ip: IPv4Address | IPv6Address) -> bool:
    """
    Check if IP address is private/internal.
    
    Args:
        ip: IP address object
    
    Returns:
        True if IP is private/internal, False otherwise
    """
    # Check standard private ranges
    if ip.is_private or ip.is_loopback or ip.is_link_local:
        return True
    
    # Additional checks for specific patterns
    ip_str = str(ip)
    for pattern in PRIVATE_IP_PATTERNS:
        if re.match(pattern, ip_str, re.IGNORECASE):
            return True
    
    return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal and other attacks.
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    if not filename:
        return ""
    
    # Remove path separators
    filename = filename.replace('/', '_').replace('\\', '_')
    
    # Remove .. sequences
    while '..' in filename:
        filename = filename.replace('..', '')
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Limit length
    max_length = 255
    if len(filename) > max_length:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        ext = ext[:50] if ext else ''
        name = name[:max_length-len(ext)-1] if ext else filename[:max_length]
        filename = f"{name}.{ext}" if ext else name
    
    # Only allow safe characters
    safe_pattern = re.compile(r'^[\w\-. ]+$')
    if not safe_pattern.match(filename):
        filename = re.sub(r'[^\w\-. ]', '_', filename)
    
    # Prevent hidden files
    if filename.startswith('.'):
        filename = '_' + filename
    
    return filename or 'unnamed'


def validate_api_key_format(api_key: str, provider: str) -> bool:
    """
    Validate API key format based on provider requirements.
    
    Args:
        api_key: API key to validate
        provider: Provider name
    
    Returns:
        True if valid format, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Ollama doesn't need API key
    if provider == 'ollama':
        return True
    
    # Basic length check
    if len(api_key) < 10:
        return False
    
    # Provider-specific validation
    if provider == 'openrouter':
        return api_key.startswith('sk-or-') or len(api_key) >= 32
    elif provider == 'groq':
        return api_key.startswith('gsk_') or len(api_key) >= 32
    elif provider == 'huggingface':
        return api_key.startswith('hf_') or len(api_key) >= 32
    
    # Generic check
    return len(api_key) >= 10


def mask_api_key(api_key: str) -> str:
    """
    Mask API key for safe logging/display.
    
    Args:
        api_key: API key to mask
    
    Returns:
        Masked API key
    """
    if not api_key or len(api_key) <= 8:
        return "****"
    
    return f"{api_key[:4]}...{api_key[-4:]}"
