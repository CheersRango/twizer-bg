#!/usr/bin/env bash
set -euo pipefail

# Tek komutla Twizer BG API'yi kurup ayağa kaldıran script
# Varsayılanları değiştirmek için environment değişkenleri kullanın:
#   REPO_URL, APP_DIR, BRANCH, SERVICE_NAME, DOMAIN, EMAIL, ENABLE_SSL,
#   GUNICORN_HOST, GUNICORN_PORT, PYTHON_BIN

if [[ $EUID -ne 0 ]]; then
  echo "[HATA] Bu script root olarak çalıştırılmalı." >&2
  exit 1
fi

REPO_URL="${REPO_URL:-https://github.com/your-org/twizer-bg.git}"
APP_DIR="${APP_DIR:-/opt/twizer-bg}"
BRANCH="${BRANCH:-main}"
SERVICE_NAME="${SERVICE_NAME:-twizer-bg}"
DOMAIN="${DOMAIN:-api.twizer.xyz}"
EMAIL="${EMAIL:-admin@example.com}"
ENABLE_SSL="${ENABLE_SSL:-true}"
GUNICORN_HOST="${GUNICORN_HOST:-127.0.0.1}"
GUNICORN_PORT="${GUNICORN_PORT:-5000}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

log() {
  echo "[INFO] $1"
}

step() {
  echo "\n==== $1 ===="
}

step "Gerekli paketler kuruluyor"
apt-get update -y
apt-get install -y git nginx certbot python3-certbot-nginx "$PYTHON_BIN" "$PYTHON_BIN"-venv "$PYTHON_BIN"-pip

step "Uygulama kodu hazırlanıyor ($APP_DIR)"
if [[ ! -d "$APP_DIR/.git" ]]; then
  log "Repo klonlanıyor: $REPO_URL -> $APP_DIR"
  git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
else
  log "Var olan repo bulundu, güncelleniyor"
  git -C "$APP_DIR" fetch --all --prune
  git -C "$APP_DIR" checkout "$BRANCH"
  git -C "$APP_DIR" pull --ff-only origin "$BRANCH" || true
fi

step "Python ortamı hazırlanıyor"
cd "$APP_DIR"
if [[ ! -d "venv" ]]; then
  "$PYTHON_BIN" -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

deactivate

step "Systemd servisi yazılıyor: /etc/systemd/system/${SERVICE_NAME}.service"
cat <<SERVICE >/etc/systemd/system/${SERVICE_NAME}.service
[Unit]
Description=Twizer Background Removal API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=${APP_DIR}
Environment="PATH=${APP_DIR}/venv/bin"
ExecStart=${APP_DIR}/venv/bin/gunicorn --workers 2 --bind ${GUNICORN_HOST}:${GUNICORN_PORT} app:app
Restart=always

[Install]
WantedBy=multi-user.target
SERVICE

step "Systemd servisleri güncelleniyor"
systemctl daemon-reload
systemctl enable --now "${SERVICE_NAME}.service"

step "Nginx yapılandırması yazılıyor: /etc/nginx/sites-available/${SERVICE_NAME}"
cat <<NGINX >/etc/nginx/sites-available/${SERVICE_NAME}
server {
    listen 80;
    server_name ${DOMAIN};

    location / {
        proxy_pass http://${GUNICORN_HOST}:${GUNICORN_PORT};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    access_log /var/log/nginx/${SERVICE_NAME}_access.log;
    error_log  /var/log/nginx/${SERVICE_NAME}_error.log;
}
NGINX

ln -sf "/etc/nginx/sites-available/${SERVICE_NAME}" "/etc/nginx/sites-enabled/${SERVICE_NAME}"
rm -f /etc/nginx/sites-enabled/default

log "Nginx testi çalıştırılıyor"
nginx -t
systemctl reload nginx

if [[ "$ENABLE_SSL" == "true" ]]; then
  if [[ -n "$DOMAIN" && "$EMAIL" != "admin@example.com" ]]; then
    step "Let's Encrypt sertifikası alınıyor"
    certbot --nginx --non-interactive --agree-tos -m "$EMAIL" -d "$DOMAIN" --redirect || log "Certbot isteğe bağlı, hata aldı"
    systemctl reload nginx
  else
    log "SSL atlandı: DOMAIN veya EMAIL ayarlanmadı."
  fi
else
  log "SSL atlandı (ENABLE_SSL=false)"
fi

step "Servis yeniden başlatılıyor"
systemctl restart "${SERVICE_NAME}.service"

log "Deployment tamamlandı. API http${ENABLE_SSL:+s}://${DOMAIN} adresinde çalışıyor."

