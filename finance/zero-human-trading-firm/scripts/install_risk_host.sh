#!/bin/bash
# install_risk_host.sh — risk policy service bootstrap (out-of-band from agents).
#
# Run this on a SEPARATE tiny VM (1 GB RAM is fine), logged in as root.
# Do NOT run on the same host as Paperclip / the trading agents.
# Takes ~3 minutes.
#
# Usage:
#   bash install_risk_host.sh <allowed-vps-ip>
#
# Example:
#   bash install_risk_host.sh 203.0.113.42
#
# What it does:
#   1. Installs FastAPI + uvicorn under a dedicated 'risk' user
#   2. Copies risk_policy_enforcer.py + creates the HTTP wrapper
#   3. Root-owns risk_policy.json so no agent identity can edit it
#   4. Generates a bearer token (printed at the end — save it)
#   5. Installs a systemd service so it auto-starts
#   6. Locks the firewall: only SSH + port 8443 from <allowed-vps-ip>
#
# What it does NOT do:
#   - Connect to any brokerage
#   - Make any trading decisions (it only says yes/no to orders)

set -euo pipefail

ALLOWED_IP="${1:-}"
if [[ -z "$ALLOWED_IP" ]]; then
  echo "usage: bash install_risk_host.sh <allowed-vps-ip>"
  echo "example: bash install_risk_host.sh 203.0.113.42"
  exit 2
fi

if [[ "$EUID" -ne 0 ]]; then
  echo "run as root (or sudo bash install_risk_host.sh <ip>)"
  exit 2
fi

echo "==> 1/6  installing packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv curl ufw openssl

echo "==> 2/6  creating 'risk' user (no shell login, no sudo)"
if ! id -u risk >/dev/null 2>&1; then
  useradd -r -s /bin/false -d /opt/risk -m risk
fi

echo "==> 3/6  installing risk_policy_enforcer.py + HTTP wrapper to /opt/risk/"
mkdir -p /opt/risk
cd /opt/risk

# pull the enforcer from the public repo
curl -sSL -o risk_policy_enforcer.py \
  https://raw.githubusercontent.com/daraseng978-lang/claude-skills/main/finance/zero-human-trading-firm/scripts/risk_policy_enforcer.py

# pull a default policy (root-owned; agents cannot edit)
if [[ ! -f /etc/risk_policy.json ]]; then
  curl -sSL -o /etc/risk_policy.json \
    https://raw.githubusercontent.com/daraseng978-lang/claude-skills/main/finance/zero-human-trading-firm/assets/risk_policy.json
  chown root:root /etc/risk_policy.json
  chmod 644 /etc/risk_policy.json
fi

# FastAPI wrapper
cat > /opt/risk/risk_service.py <<'PYEOF'
import json, os, subprocess, tempfile
from fastapi import FastAPI, HTTPException, Header

app = FastAPI()
POLICY = "/etc/risk_policy.json"
TOKEN = os.environ.get("RISK_TOKEN", "")

@app.post("/risk/check")
def check(payload: dict, authorization: str = Header(default="")):
    if not TOKEN or authorization != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="unauthorized")
    order = payload["order"]
    state = payload.get("state", {})
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as of, \
         tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as sf:
        json.dump(order, of); of.flush()
        json.dump(state, sf); sf.flush()
        rc = subprocess.run(
            ["python3", "/opt/risk/risk_policy_enforcer.py", "check",
             "--order", of.name, "--state", sf.name,
             "--policy", POLICY, "--format", "json"],
            capture_output=True, text=True,
        )
    os.unlink(of.name); os.unlink(sf.name)
    if rc.returncode != 0 and not rc.stdout:
        raise HTTPException(status_code=500, detail=rc.stderr)
    return json.loads(rc.stdout)

@app.get("/health")
def health():
    return {"ok": True}
PYEOF

# venv with fastapi + uvicorn
python3 -m venv /opt/risk/venv
/opt/risk/venv/bin/pip install --quiet fastapi uvicorn

chown -R risk:risk /opt/risk
chmod 644 /opt/risk/*.py

echo "==> 4/6  generating bearer token"
TOKEN=$(openssl rand -hex 32)
echo "RISK_TOKEN=${TOKEN}" > /etc/risk_service.env
chmod 600 /etc/risk_service.env
chown root:root /etc/risk_service.env

echo "==> 5/6  installing systemd service"
cat > /etc/systemd/system/risk.service <<EOF
[Unit]
Description=Risk Policy Service (out-of-band)
After=network.target

[Service]
Type=simple
User=risk
WorkingDirectory=/opt/risk
EnvironmentFile=/etc/risk_service.env
ExecStart=/opt/risk/venv/bin/uvicorn risk_service:app --host 0.0.0.0 --port 8443
Restart=on-failure
RestartSec=5
# prevent this service from writing anywhere except its own dir
ProtectSystem=strict
ReadOnlyPaths=/etc/risk_policy.json

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now risk.service

echo "==> 6/6  locking firewall: SSH + port 8443 from ${ALLOWED_IP} only"
ufw --force reset >/dev/null
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow from "${ALLOWED_IP}" to any port 8443 proto tcp
ufw --force enable

echo ""
echo "================================================================"
echo "  Risk host ready."
echo "================================================================"
echo ""
echo "  URL for CEO_BOOTSTRAP.md:  http://$(hostname -I | awk '{print $1}'):8443"
echo "  Bearer token:              ${TOKEN}"
echo ""
echo "  Save the token NOW. You'll paste it into CEO_BOOTSTRAP.md"
echo "  as <RISK_HOST_TOKEN>. It is not displayed again."
echo ""
echo "  Sanity check from this host:"
echo "    curl http://localhost:8443/health"
echo ""
echo "  From the VPS (expect 401 without a token, 200 with it):"
echo "    curl http://<this-host-ip>:8443/health"
echo ""
echo "  WHO CAN EDIT /etc/risk_policy.json:  root, and only root."
echo "  WHO CAN DEPLOY risk.service:         root, and only root."
echo "  If you ever find the 'agent' user on this host, the firm is unsafe."
echo ""
