#!/usr/bin/env bash
set -euo pipefail

APP_USER="${APP_USER:-root}"
REPO_URL="${REPO_URL:-https://github.com/harit105/SeaGraze_Chatbot.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"
REPO_DIR="${REPO_DIR:-/root/SeaGraze_Chatbot}"
APP_DIR="${APP_DIR:-${REPO_DIR}}"
VENV_DIR="${VENV_DIR:-${APP_DIR}/.venv}"
SERVICE_NAME="${SERVICE_NAME:-seagraze}"
STREAMLIT_PORT="${STREAMLIT_PORT:-8501}"

log() {
  printf "\n==> %s\n" "$1"
}

read_value() {
  local var_name="$1"
  local prompt="$2"
  local default_value="${3:-}"
  local current="${!var_name:-}"

  if [[ -n "$current" ]]; then
    return
  fi

  if [[ -n "$default_value" ]]; then
    read -r -p "$prompt [$default_value]: " input
    export "$var_name"="${input:-$default_value}"
  else
    read -r -p "$prompt: " input
    if [[ -z "$input" ]]; then
      echo "$var_name is required"
      exit 1
    fi
    export "$var_name"="$input"
  fi
}

read_secret() {
  local var_name="$1"
  local prompt="$2"
  local current="${!var_name:-}"

  if [[ -n "$current" ]]; then
    return
  fi

  read -r -s -p "$prompt: " input
  echo
  if [[ -z "$input" ]]; then
    echo "$var_name is required"
    exit 1
  fi
  export "$var_name"="$input"
}

log "Install system packages"
apt update
apt install -y python3-venv python3-pip git nginx curl ufw

log "Fetch source"
if [[ -d "$REPO_DIR/.git" ]]; then
  git -C "$REPO_DIR" fetch origin
  git -C "$REPO_DIR" checkout "$REPO_BRANCH"
  git -C "$REPO_DIR" pull --rebase origin "$REPO_BRANCH"
else
  git clone --branch "$REPO_BRANCH" "$REPO_URL" "$REPO_DIR"
fi

if [[ ! -d "$APP_DIR" ]]; then
  echo "Expected app directory not found: $APP_DIR"
  exit 1
fi

log "Python environment"
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"

log "Collect runtime secrets"
read_secret MONGO_URI "MongoDB URI (e.g., mongodb+srv://...)"
read_secret GEMINI_API_KEY "Gemini API key"

log "Write .env"
cat > "$APP_DIR/.env" <<EOF
MONGO_URI=${MONGO_URI}
GEMINI_API_KEY=${GEMINI_API_KEY}
EOF
chmod 600 "$APP_DIR/.env"

log "Create systemd service"
cat > "/etc/systemd/system/${SERVICE_NAME}.service" <<EOF
[Unit]
Description=SeagrazeBrain Streamlit App
After=network.target

[Service]
User=${APP_USER}
WorkingDirectory=${APP_DIR}
Environment=PATH=${VENV_DIR}/bin
ExecStart=${VENV_DIR}/bin/streamlit run main.py --server.address 127.0.0.1 --server.port ${STREAMLIT_PORT}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable "${SERVICE_NAME}"
systemctl restart "${SERVICE_NAME}"

log "Configure nginx reverse proxy"
cat > /etc/nginx/sites-available/seagraze <<EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:${STREAMLIT_PORT};
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
ln -sf /etc/nginx/sites-available/seagraze /etc/nginx/sites-enabled/seagraze
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

log "Configure UFW"
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

PUBLIC_IP="\$(curl -s https://ifconfig.me || true)"

log "Done"
echo "Open: http://\${PUBLIC_IP:-<droplet-ip>}"
echo "Service status: systemctl status ${SERVICE_NAME}"
echo "Service logs: journalctl -u ${SERVICE_NAME} -f"
echo
echo "IMPORTANT: In MongoDB Atlas Network Access, add \${PUBLIC_IP:-<droplet-ip>}/32 and remove 0.0.0.0/0"
