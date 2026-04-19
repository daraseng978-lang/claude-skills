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

# pre-create HWM state file, root-owned, daemon will append updates via a helper
if [[ ! -f /etc/hwm_state.json ]]; then
  echo '{"version":1,"high_water_mark":0.0,"last_equity":0.0,"last_equity_ts":0,"net_deposits":0.0}' \
    > /etc/hwm_state.json
  chown risk:risk /etc/hwm_state.json  # the risk user (daemon) can update; nobody else
  chmod 640 /etc/hwm_state.json
fi

# FastAPI wrapper — /risk/check + /hwm/equity + /hwm/deposit + /hwm/state
cat > /opt/risk/risk_service.py <<'PYEOF'
import json, os, subprocess, tempfile, threading
from fastapi import FastAPI, HTTPException, Header

app = FastAPI()
POLICY = "/etc/risk_policy.json"
HWM = "/etc/hwm_state.json"
TOKEN = os.environ.get("RISK_TOKEN", "")
_hwm_lock = threading.Lock()


def _require_auth(authorization: str) -> None:
    if not TOKEN or authorization != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="unauthorized")


def _load_hwm() -> dict:
    with open(HWM, "r") as f:
        return json.load(f)


def _save_hwm(state: dict) -> None:
    tmp = HWM + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)
    os.replace(tmp, HWM)


def _load_policy() -> dict:
    with open(POLICY, "r") as f:
        return json.load(f)


@app.post("/risk/check")
def check(payload: dict, authorization: str = Header(default="")):
    _require_auth(authorization)
    order = payload["order"]
    state = payload.get("state", {})

    # Inject drawdown-from-HWM into the state before enforcement
    with _hwm_lock:
        hwm = _load_hwm()
    last_equity = float(hwm.get("last_equity", 0.0))
    high_water = float(hwm.get("high_water_mark", 0.0))
    if high_water > 0:
        dd = max(0.0, (high_water - last_equity) / high_water)
        state.setdefault("drawdown_from_hwm", dd)

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


@app.post("/hwm/equity")
def hwm_equity(payload: dict, authorization: str = Header(default="")):
    """Record a new equity snapshot. HWM updates only when equity
    EXCLUDING deposits exceeds the previous peak.
    """
    _require_auth(authorization)
    equity = float(payload["equity"])
    ts = int(payload.get("ts", 0))
    with _hwm_lock:
        state = _load_hwm()
        net_deposits = float(state.get("net_deposits", 0.0))
        equity_ex_deposits = equity - net_deposits
        prev_hwm = float(state.get("high_water_mark", 0.0))
        if equity_ex_deposits > prev_hwm:
            state["high_water_mark"] = equity_ex_deposits
        state["last_equity"] = equity
        state["last_equity_ts"] = ts
        _save_hwm(state)
        return {
            "ok": True,
            "high_water_mark": state["high_water_mark"],
            "last_equity": state["last_equity"],
            "drawdown_from_hwm": (
                max(0.0, (state["high_water_mark"] - equity_ex_deposits) / state["high_water_mark"])
                if state["high_water_mark"] > 0 else 0.0
            ),
        }


@app.post("/hwm/deposit")
def hwm_deposit(payload: dict, authorization: str = Header(default="")):
    """Record a deposit or withdrawal so HWM denominator ignores it.
    Positive = deposit, negative = withdrawal.
    """
    _require_auth(authorization)
    amount = float(payload["amount"])
    with _hwm_lock:
        state = _load_hwm()
        state["net_deposits"] = float(state.get("net_deposits", 0.0)) + amount
        _save_hwm(state)
        return {"ok": True, "net_deposits": state["net_deposits"]}


@app.get("/hwm/state")
def hwm_state(authorization: str = Header(default="")):
    _require_auth(authorization)
    with _hwm_lock:
        state = _load_hwm()
    high_water = float(state.get("high_water_mark", 0.0))
    last_equity = float(state.get("last_equity", 0.0))
    net_deposits = float(state.get("net_deposits", 0.0))
    equity_ex_deposits = last_equity - net_deposits
    dd = (max(0.0, (high_water - equity_ex_deposits) / high_water)
          if high_water > 0 else 0.0)
    return {
        "high_water_mark": high_water,
        "last_equity": last_equity,
        "last_equity_ts": state.get("last_equity_ts", 0),
        "net_deposits": net_deposits,
        "drawdown_from_hwm": dd,
    }


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
ReadWritePaths=/etc/hwm_state.json

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
