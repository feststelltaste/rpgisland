# Start with Python 3.10
FROM mcr.microsoft.com/devcontainers/python:3.14-bookworm

# 1. Install System Dependencies
RUN apt-get update && apt-get install -y \
    iptables ipset dnsutils jq curl git sudo \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Node.js & Claude Code
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g @anthropic-ai/claude-code

# 3. Setup Setup Scripts
COPY --chmod=0755 .devcontainer/init-firewall.sh /usr/local/bin/init-firewall.sh

# 4. Setup User
RUN echo "vscode ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# --- NEW SECTION: Install Requirements ---
# We copy requirements.txt from the context (project root) into the image
COPY requirements.txt /tmp/pip-tmp/

# Install them immediately
RUN pip install --no-cache-dir -r /tmp/pip-tmp/requirements.txt \
    && rm -rf /tmp/pip-tmp

WORKDIR /workspace