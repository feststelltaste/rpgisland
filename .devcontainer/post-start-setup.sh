#!/bin/bash

# 1. Setup Git and Force Submodule Clone (Shallow & Fresh)

git config user.email "ai@markusharrer.de"
git config user.name "DeepSeek"

echo "📦 initializing submodules..."

# A. Trust the directory (Critical for Docker volumes)
git config --global --add safe.directory /workspace

# B. The "Do Everything" Command
# --init: Registers the submodule in .git/config (Fixes "missing" error)
# --recursive: Handles nested submodules
# --depth 1: Fetches only the latest snapshot (Fast)
git submodule update --init --recursive --depth 1


# 2. Fix Permissions
echo "🔑 Fixing permissions..."
sudo chown -R vscode:vscode /workspace


# 3. Configure Claude CLI Settings
# This creates the config file automatically so you don't have to set it up manually.
echo "🤖 Configuring Claude CLI..."
mkdir -p ~/.config/claude

# WRITE YOUR SETTINGS HERE:
# (You can add "theme": "dark", "editor": "vim", etc.)
cat > ~/.config/claude/config.json <<EOF
{
  "theme": "dark",
  "verbose": false,
  "preferred_editor": "nano"
}
EOF


# 4. Configure Jupyter Defaults
echo "🪐 Configuring Jupyter..."
mkdir -p ~/.jupyter

# Generate the config file
cat > ~/.jupyter/jupyter_notebook_config.py <<EOF
# 1. Listen on all internal interfaces (Required for Docker forwarding)
c.ServerApp.ip = '0.0.0.0'

# 2. Do not try to open a browser window (It fails in containers anyway)
c.ServerApp.open_browser = False

# 3. Allow running as root (if needed)
c.ServerApp.allow_root = True

# 4. Security: We keep the token enabled by default!
# (Do NOT add c.ServerApp.token = '' unless you want zero security)
EOF

echo "✅ Jupyter config updated."


# 5. Start Firewall (Last step)
echo "🛡️ Starting firewall..."
sudo /usr/local/bin/init-firewall.sh