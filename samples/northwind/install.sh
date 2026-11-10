#!/usr/bin/env bash
# Northwind log forwarder installer (nw-forwarder 2.4.1)
set -euo pipefail

VERSION="2.4.1"
SHA256="9f2c4a1e7b3d5f60a8c9e1b2d3f4a5b6c7d8e9f0a1b2c3d4e5f60718293a4b5c"

curl -fsSLo /tmp/nw-forwarder.tar.gz "https://downloads.northwind-insights.example/nw-forwarder-${VERSION}-linux-amd64.tar.gz"
echo "${SHA256}  /tmp/nw-forwarder.tar.gz" | sha256sum -c -

useradd --system --no-create-home --shell /usr/sbin/nologin nwfwd || true
install -d -o nwfwd -g nwfwd /opt/nw-forwarder /etc/nw-forwarder
tar -xzf /tmp/nw-forwarder.tar.gz -C /opt/nw-forwarder --strip-components=1

cat > /etc/nw-forwarder/config.yaml <<CFG
inputs:
  - path: /var/log/contoso-app/*.log
output:
  url: https://ingest.northwind-insights.example/v1/logs
CFG

cp /opt/nw-forwarder/nw-forwarder.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now nw-forwarder
