"""
crlf_injection.py

Intentionally vulnerable route used to test whether the pipeline
(Bandit, ZAP) catches CRLF Injection / HTTP Response Splitting.

"""
import re
from urllib.parse import unquote, urlparse
from flask import Blueprint, Response, redirect, request

crlf_bp = Blueprint("crlf_injection", __name__)

ALLOWED_PATHS = {"/", "/dashboard", "/login", "/home"}
ALLOWED_HOSTS = {"example.com", "my-domain.com"}
SAFE_REDIRECT_KEYS = {
    "home": "/",
    "dashboard": "/dashboard",
    "login": "/login",
    "welcome": "/home",
}

def go():
    # Select redirect destination by trusted server-side mapping, not raw URL input.
    next_key = request.args.get("next", "home")
    safe_target = SAFE_REDIRECT_KEYS.get(next_key, "/")
    return redirect(safe_target)
    """
    VULNERABLE ENDPOINT.

    The 'url' parameter is passed straight into redirect with no
    validation. If it contains \r\n, an attacker can inject a
    malicious header/cookie into the response.

    Test request:
        http://localhost:5000/go?url=http://example.com%0d%0aSet-Cookie:%20injected=true
    """
    """  target_url = request.args.get("url", "/")

    #  no validation before redirectt
    return redirect(target_url)"""

