#!/usr/bin/env bash
set -euo pipefail

APP_DIR=/opt/frontier-ai-workbench

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y nginx python3-venv
mkdir -p "$APP_DIR"

python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install -r "$APP_DIR/backend/requirements.txt"

cp "$APP_DIR/deploy/workbench.service" /etc/systemd/system/workbench.service
cp "$APP_DIR/deploy/workbench-daily.service" /etc/systemd/system/workbench-daily.service
cp "$APP_DIR/deploy/workbench-daily.timer" /etc/systemd/system/workbench-daily.timer
cp "$APP_DIR/deploy/nginx-workbench.conf" /etc/nginx/sites-available/wangqizhi-ai-portfolio.conf
rm -f /etc/nginx/sites-enabled/workbench.conf
ln -sfn /etc/nginx/sites-available/wangqizhi-ai-portfolio.conf /etc/nginx/sites-enabled/wangqizhi-ai-portfolio.conf

nginx -t
systemctl daemon-reload
systemctl enable --now workbench.service
systemctl enable --now workbench-daily.timer
systemctl reload nginx
