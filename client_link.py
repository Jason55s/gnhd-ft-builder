#!/usr/bin/env python3
"""Generate a private VLESS import link after Cloud Run deployment."""
import argparse
import uuid
from urllib.parse import urlencode, urlsplit

parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True, help='Exact HTTPS URL from Cloud Run')
parser.add_argument('--uuid', required=True, help='Same UUID supplied as VLESS_UUID on Cloud Run')
parser.add_argument('--path', default='/ws', help='Same WS_PATH supplied to Cloud Run')
args = parser.parse_args()
parsed = urlsplit(args.url)
if parsed.scheme != 'https' or not parsed.hostname:
    parser.error('Use the actual HTTPS Cloud Run service URL')
try:
    user = str(uuid.UUID(args.uuid))
except ValueError:
    parser.error('Invalid UUID')
if not args.path.startswith('/'):
    parser.error('WebSocket path must start with /')
qs = urlencode(dict(encryption='none', security='tls', type='ws', sni=parsed.hostname,
                    host=parsed.hostname, path=args.path))
print(f'vless://{user}@{parsed.hostname}:443?{qs}#gnhd-ft')
print('Keep this connection link private. The Host and SNI must match the actual Cloud Run URL.')
