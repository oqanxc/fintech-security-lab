import ipaddress
import socket
from urllib.parse import urlsplit

import requests
from flask import Blueprint, request, jsonify
from requests.adapters import HTTPAdapter

tools = Blueprint("tools", __name__)

ALLOWED_HOSTS = {"vulnerableapp.com"}   # exact match
ALLOWED_SCHEMES = {"https"}
ALLOWED_PORTS = {443}
TIMEOUT = (3, 5)                        
MAX_BODY = 1_000_000                    


class UnsafeURL(Exception):
    pass


class PinnedHostAdapter(HTTPAdapter):
    

    def __init__(self, hostname, **kwargs):
        self._hostname = hostname
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        pool_kwargs["server_hostname"] = self._hostname
        pool_kwargs["assert_hostname"] = self._hostname
        super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)


def validate_and_resolve(raw_url):
    #  Parse, do not search within the string
    try:
        parts = urlsplit(raw_url)
        port = parts.port or 443
    except ValueError:
        raise UnsafeURL("invalid url")

    #   Schema, userinfo, host, port checks
    if parts.scheme not in ALLOWED_SCHEMES:
        raise UnsafeURL("scheme not allowed")
    if parts.username or parts.password:
        raise UnsafeURL("userinfo not allowed")
    host = parts.hostname
    if host not in ALLOWED_HOSTS:           # not containing, exact match
        raise UnsafeURL("host not allowed")
    if port not in ALLOWED_PORTS:
        raise UnsafeURL("port not allowed")

    #  resolve it and check all IPs
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror:
        raise UnsafeURL("dns failure")

    ips = []
    for info in infos:
        ip = ipaddress.ip_address(info[4][0].split("%")[0])
        if ip.version == 6 and ip.ipv4_mapped:   # ::ffff:127.0.0.1 check
            ip = ip.ipv4_mapped
        if not ip.is_global:                     # loopback, private, link-local etc.
            raise UnsafeURL("resolves to non-public ip")
        ips.append(ip)

    if not ips:
        raise UnsafeURL("no ip")
    return parts, host, port, ips[0]


@tools.route("/fetch", methods=["POST"])
def tools_fetch():
    raw_url = request.form.get("url")
    if not raw_url:
        return jsonify({"status": "fail"}), 400

    try:
        parts, host, port, ip = validate_and_resolve(raw_url)
    except UnsafeURL:
        # Do not provide any details about the failure, just return a generic error
        return jsonify({"status": "fail"}), 400

    # Connect to the resolved IP address, but use the original host in the Host header
    ip_str = f"[{ip}]" if ip.version == 6 else str(ip)
    pinned_url = parts._replace(netloc=f"{ip_str}:{port}").geturl()

    session = requests.Session()
    session.trust_env = False                       
    session.mount("https://", PinnedHostAdapter(host))

    try:
        res = session.get(
            pinned_url,
            headers={"Host": host},
            allow_redirects=False,                  # redirect closed
            timeout=TIMEOUT,
            stream=True,
        )
        if res.is_redirect or res.is_permanent_redirect:
            return jsonify({"status": "fail"}), 400

        body = res.raw.read(MAX_BODY + 1, decode_content=True)
        if len(body) > MAX_BODY:
            return jsonify({"status": "fail"}), 413
    except requests.RequestException:
        return jsonify({"status": "fail"}), 502
    finally:
        session.close()

    return jsonify({"status": "ok", "body": body.decode("utf-8", errors="replace")})



# from flask import Blueprint, request, jsonify

# import requests


# tools = Blueprint("tools", __name__)

# @tools.route("/fetch", methods=['POST'])
# def tools_fetch():
#     url = request.form.get("url")
#     if not url or 'vulnerableapp.com' not in url:
#         return jsonify({'status': 'fail'})
#     res = requests.get(url)
#     return jsonify({'status': 'ok', 'body': res.text})