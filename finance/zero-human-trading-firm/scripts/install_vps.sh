#!/bin/bash
# install_vps.sh — Paperclip host bootstrap for the zero-human trading firm.
#
# Run this on a fresh Ubuntu 22.04/24.04 VPS, logged in as root.
# Takes ~5 minutes. Safe to re-run; skips work already done.
#
# Usage:
#   curl -sSL https://raw.githubusercontent.com/daraseng978-lang/claude-skills/main/finance/zero-human-trading-firm/scripts/install_vps.sh | bash -s -- <firm-slug>
# or locally after cloning:
#   bash install_vps.sh <firm-slug>
#
# What it does:
#   1. Installs system packages (git, python3, curl, sudo, ufw)
#   2. Creates an unprivileged 'agent' user with no sudo
#   3. Clones the claude-skills repo to /opt/claude-skills
#   4. Installs Paperclip
#   5. Opens the firewall for 80/443 only
#   6. Scaffolds ~/firms/<firm-slug>/ for the CEO agent to take over
#
# What it does NOT do:
#   - Install IB Gateway (founder does that manually)
#   - Touch the risk host (that's install_risk_host.sh)
#   - Start any trading

set -euo pipefail

FIRM_SLUG="${1:-}"
if [[ -z "$FIRM_SLUG" ]]; then
  echo "usage: bash install_vps.sh <firm-slug>"
  echo "example: bash install_vps.sh lewis-ventures"
  exit 2
fi

if [[ "$EUID" -ne 0 ]]; then
  echo "run as root (or sudo bash install_vps.sh <firm-slug>)"
  exit 2
fi

echo "==> 1/6  updating apt and installing base packages"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq git python3 python3-pip curl sudo ufw

echo "==> 2/6  creating unprivileged 'agent' user"
if ! id -u agent >/dev/null 2>&1; then
  useradd -m -s /bin/bash agent
  # no sudo, no wheel, no docker group — this is the whole point
  echo "agent user created (no sudo, no root escalation path)"
else
  echo "agent user already exists, skipping"
fi

echo "==> 3/6  cloning claude-skills to /opt/claude-skills"
if [[ ! -d /opt/claude-skills ]]; then
  git clone --depth 1 https://github.com/daraseng978-lang/claude-skills /opt/claude-skills
  chown -R agent:agent /opt/claude-skills
else
  echo "/opt/claude-skills already exists, pulling latest"
  (cd /opt/claude-skills && git pull --ff-only origin main)
fi

echo "==> 4/6  installing Paperclip (best-effort; check logs if this fails)"
if ! command -v paperclip >/dev/null 2>&1; then
  curl -sSL https://paperclip.ng/install | bash || {
    echo "WARN: paperclip install script failed. Install it manually from https://paperclip.ng"
  }
else
  echo "paperclip already installed"
fi

echo "==> 5/6  configuring firewall (allow 22 + 80 + 443 only)"
ufw --force reset >/dev/null
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo "==> 6/6  scaffolding firm workspace for 'agent' user"
FIRM_DIR="/home/agent/firms/${FIRM_SLUG}"
if [[ ! -d "$FIRM_DIR" ]]; then
  sudo -u agent mkdir -p "/home/agent/firms"
  # delegate to firm_init.py — the CEO agent will fill in the rest
  sudo -u agent python3 /opt/claude-skills/finance/zero-human-trading-firm/scripts/firm_init.py \
    --name "${FIRM_SLUG}" \
    --venue "equities-us" \
    --out "$FIRM_DIR"
else
  echo "$FIRM_DIR already exists, skipping scaffold"
fi

echo ""
echo "================================================================"
echo "  VPS ready."
echo "================================================================"
echo ""
echo "Next steps for the founder:"
echo "  1. Visit https://<this-vps-ip>/ in a browser to finish Paperclip onboarding"
echo "  2. Run install_risk_host.sh on your SECOND VM"
echo "  3. Fill in CEO_BOOTSTRAP.md placeholders and paste it to a fresh CEO agent"
echo ""
echo "Firm folder:   $FIRM_DIR"
echo "Skill library: /opt/claude-skills"
echo "Agent user:    'agent' (no sudo — this is intentional)"
echo ""
