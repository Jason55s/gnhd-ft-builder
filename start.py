#!/usr/bin/env python3
"""Generate a private Xray config from runtime environment variables, then start Xray.

VLESS_UUID is required and intentionally NOT baked into the public Docker image.
"""
import json
import os
import sys
import uuid
from pathlib import Path


def configuration(env):
    token = env.get("VLESS_UUID", "").strip()
    try:
        credential = str(uuid.UUID(token))
    except (ValueError, AttributeError) as exc:
        raise ValueError("Set VLESS_UUID to a valid private UUID in the deployment environment") from exc

    raw_port = env.get("PORT", "8080")
    try:
        port = int(raw_port)
        if not 1 <= port <= 65535:
            raise ValueError()
    except ValueError as exc:
        raise ValueError("PORT must be a valid TCP port") from exc

    path = env.get("WS_PATH", "/ws")
    if (not path.startswith("/") or len(path) > 200
            or "?" in path or "#" in path or any(ord(c) < 33 for c in path)):
        raise ValueError("WS_PATH must start with / and have no whitespace, query or fragment")

    return {
        "log": {"loglevel": "warning"},
        "inbounds": [{
            "tag": "vless-ws",
            "listen": "0.0.0.0",
            "port": port,
            "protocol": "vless",
            "settings": {"users": [{"id": credential, "level": 0}], "decryption": "none"},
            "streamSettings": {
                "network": "ws",
                # External HTTPS is terminated by Cloud Run. Incoming container traffic is HTTP/WebSocket.
                "security": "none",
                "wsSettings": {"path": path},
            },
        }],
        "outbounds": [
            {"tag": "direct", "protocol": "freedom"},
            {"tag": "block", "protocol": "blackhole"},
        ],
        "routing": {
            "domainStrategy": "IPIfNonMatch",
            "rules": [
                {"type": "field", "ip": ["geoip:private", "169.254.169.254/32"], "outboundTag": "block"},
                {"type": "field", "domain": ["full:metadata.google.internal"], "outboundTag": "block"},
            ],
        },
    }


def main():
    try:
        data = configuration(os.environ)
    except ValueError as error:
        print(f"Configuration error: {error}", file=sys.stderr)
        return 2
    path = Path("/tmp/xray/config.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    path.chmod(0o600)
    if "--check" in sys.argv:
        print("Configuration generated and validated structurally (Xray binary not executed).")
        return 0
    print(f"Starting Xray VLESS/WebSocket on port {data['inbounds'][0]['port']}", flush=True)
    os.execv("/usr/local/bin/xray", ["xray", "run", "-c", str(path)])


if __name__ == "__main__":
    raise SystemExit(main())
