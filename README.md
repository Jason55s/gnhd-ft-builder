# Publish your own reusable Docker Hub VLESS/WebSocket image

This project packages Xray-core into a reusable Linux container for Google Cloud Run.
It reproduces a **basic VLESS over WebSocket proxy role**, not the unknown internals
of `ppstechsurf/pps-tech`. Use it only on Cloud projects that allow these workloads.

## Why it is safe to publish the image

There is **no UUID or other credential in the image**. `VLESS_UUID` is required
at runtime. Never bake your UUID into a public Docker Hub image or commit it to git.
The original starter ZIP created `config.json` with the UUID baked into the image;
**do not publish that original image publicly**.

## Publish to Docker Hub from your own PC (Docker Desktop required)

1. Create a Docker Hub account at https://hub.docker.com/.
2. Create a **public** repository named `gnhd-ft` under your account.
3. Extract this ZIP. Open PowerShell in the folder containing `Dockerfile`.
4. Run these commands (replace YOUR_USERNAME with the Docker Hub account name):

```powershell
docker login -u YOUR_USERNAME
docker buildx build --platform linux/amd64 -t YOUR_USERNAME/gnhd-ft:1.0 -t YOUR_USERNAME/gnhd-ft:latest --push .
```

You will have a reusable image at `docker.io/YOUR_USERNAME/gnhd-ft:1.0`.

If Buildx is not available, a simple amd64 build/push can work on an amd64 PC:

```powershell
docker build --platform linux/amd64 -t YOUR_USERNAME/gnhd-ft:1.0 .
docker push YOUR_USERNAME/gnhd-ft:1.0
```

## Deploy from image to your OWN authorized Google Cloud project

Generate a UUID locally with Python 3 (`python -c "import uuid; print(uuid.uuid4())"`),
and save it privately. Use the same UUID for that service's client connections.

From Cloud Shell **in your own project**, run (replace placeholders):

```bash
gcloud run deploy gnhd-ft \
  --image docker.io/YOUR_USERNAME/gnhd-ft:1.0 \
  --region europe-west1 \
  --port 8080 \
  --timeout 3600 \
  --allow-unauthenticated \
  --set-env-vars VLESS_UUID=YOUR_PRIVATE_UUID,WS_PATH=/ws
```

Cloud Run terminates HTTPS/TLS at its frontend, forwarding a plain WebSocket
connection to Xray on port 8080. Your client connects using TLS/WSS on 443
with SNI and Host equal to the *actual* Cloud Run service hostname and path `/ws`.

**For improved secret protection**, use Google Secret Manager to supply `VLESS_UUID`
in production, instead of a plaintext environment variable. The UUID and VLESS
client link are secrets. With `--allow-unauthenticated`, knowing this UUID is the
only application-level authentication protecting your proxy.

Get the service URL:

```bash
gcloud run services describe gnhd-ft --region europe-west1 --format='value(status.url)'
```

Generate a connection link on a trusted computer from this folder:

```bash
python3 client_link.py --url https://ACTUAL-CLOUD-RUN-URL --uuid YOUR_PRIVATE_UUID
```

The `--uuid` argument and generated URL can appear in shell history or terminal logs;
avoid running this on shared computers, and protect your credential.

For each new service you may reuse the same image and choose a new UUID and region.
The Docker Hub image remains available while the repository exists, but the Cloud
Run service depends on its separate project's billing, policies and permissions.

## Local checks

If Docker is installed:

```bash
docker build -t gnhd-ft:local .
docker run --rm -e VLESS_UUID=YOUR_PRIVATE_UUID -p 8080:8080 gnhd-ft:local
```

Run a different terminal to inspect listening port or use a compatible VLESS/WebSocket
client. Browser opening the bare URL is not a valid VLESS test.

You can check the configuration generator without Docker:

```bash
VLESS_UUID=00000000-0000-4000-8000-000000000001 python3 start.py --check
```

## Critical constraints

- A Google Skills/Qwiklabs temporary project can block this custom image via
  `custom.restrictCloudRunRegistries` or other organization policy. **Do not attempt
  to bypass those rules by changing registries or mirrors.** Use your own project
  or a project where its administrator explicitly allows these deployments.
- WebSockets on Cloud Run have a request timeout of up to 60 minutes, so clients
  must reconnect. Long-lived sessions can incur billing.
- Cloud Run is HTTPS/WebSocket, not an unrestricted TCP/UDP VPN endpoint.
- Public Docker Hub images may experience cache/registry availability issues;
  Artifact Registry is recommended by Google for reliable production deployments.
- Uses pinned official Xray-core version `26.10.21`; update and republish after
  assessing upstream security releases.

## Documentation

- https://docs.cloud.google.com/run/docs/deploying
- https://docs.cloud.google.com/run/docs/triggering/websockets
- https://xtls.github.io/en/config/inbounds/vless.html
- https://docs.docker.com/build/building/multi-platform/
