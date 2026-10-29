# Reusable public VLESS-over-WebSocket image for permitted Cloud Run projects.
# No UUID, password or other deployment secret is embedded in the image.
FROM ghcr.io/xtls/xray-core:26.10.21 AS xray
FROM python:3.12-alpine

COPY --from=xray /usr/local/bin/xray /usr/local/bin/xray
COPY --from=xray /usr/local/share/xray/ /usr/local/share/xray/
WORKDIR /opt/vless
COPY start.py client_link.py ./
RUN addgroup -S proxy && adduser -S -G proxy proxy \
    && mkdir -p /tmp/xray && chown proxy:proxy /tmp/xray
USER proxy
ENV PORT=8080 WS_PATH=/ws XRAY_LOCATION_ASSET=/usr/local/share/xray
EXPOSE 8080
ENTRYPOINT ["python3", "/opt/vless/start.py"]
