#!/bin/bash
set -u # Error on undefined vars
# We removed 'set -e' specifically for the network loops to prevent crashes on DNS timeouts.

echo "🛡️  Initializing Container Firewall..."

# 0. PRE-FLIGHT & DEPENDENCIES
if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: This script must be run as root"
    exit 1
fi

# Ensure required tools are installed (Add 'jq' 'ipset' 'dnsutils' to Dockerfile if missing)
if ! command -v ipset &> /dev/null || ! command -v dig &> /dev/null; then
    echo "⚠️  WARNING: 'ipset' or 'dnsutils' (dig) not found. Skipping strict domain filtering."
fi

# 1. CLEANUP & SAFETY RESET
echo "🧹 Clearing old rules..."
# Reset to ACCEPT first so we don't lock ourselves out during the reset
iptables -P INPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -P OUTPUT ACCEPT
iptables -F
iptables -X

# Create IP Set for allowed domains
ipset destroy allowed-domains 2>/dev/null || true
ipset create allowed-domains hash:net

# 2. RESOLVE & POPULATE
echo "🔍 Resolving allowed domains..."

add_ip() {
    local ip="$1"
    # Regex to validate IP (IPv4)
    if [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+(/[0-9]+)?$ ]]; then
        ipset add allowed-domains "$ip" 2>/dev/null || true
    fi
}

# A. GitHub Ranges (Critical)
echo "   -> Fetching GitHub meta..."
gh_json=$(curl -s --connect-timeout 5 https://api.github.com/meta || true)
if [ -n "$gh_json" ] && command -v jq &> /dev/null; then
    # Parse IPs safely
    for range in $(echo "$gh_json" | jq -r '.web[], .api[], .git[]' 2>/dev/null); do
        add_ip "$range"
    done
else
    echo "⚠️  WARNING: Could not fetch GitHub IPs (Curl failed or jq missing)."
fi

# B. Specific Domains
DOMAINS=(
    "pypi.org" "files.pythonhosted.org"       # Python
    "registry.npmjs.org" "registry.yarnpkg.com" # Node
    "api.deepseek.com" "api.anthropic.com"    # AI APIs
    "marketplace.visualstudio.com"            # VS Code
    "graphdatascience.ninja"                  # Neo4j GDS Updates
    "vscode.blob.core.windows.net"
    "update.code.visualstudio.com"
    "deb.debian.org" "security.debian.org"    # OS Updates
)

for domain in "${DOMAINS[@]}"; do
    # '|| true' prevents script crash if grep finds nothing
    for ip in $(dig +short "$domain" | grep '^[0-9]' || true); do
        add_ip "$ip"
    done
done

# 3. APPLY RULES
echo "🔒 Applying iptables rules..."

# A. Loopback (Critical for App <-> Neo4j shared network)
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# B. DNS (UDP/TCP 53)
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT
iptables -A INPUT -p udp --sport 53 -j ACCEPT
iptables -A INPUT -p tcp --sport 53 -j ACCEPT

# C. Application Ports (INPUT from Windows)
echo "🌐 Opening Application Ports..."
# Neo4j (7474/7687) & Jupyter (8888)
# We allow ANY source here because 'docker-compose' handles the port mapping security.
iptables -A INPUT -p tcp --dport 7474 -j ACCEPT
iptables -A INPUT -p tcp --dport 7687 -j ACCEPT
iptables -A INPUT -p tcp --dport 8888 -j ACCEPT

# D. Internal Docker Networks (The Gateway Fix)
# Windows often talks to Docker via 192.168.x.x or 10.x.x.x.
# We must allow OUTPUT to these ranges so the handshake completes.
echo "🔌 Allowing Docker Gateway ranges..."
INTERNAL_RANGES=("172.16.0.0/12" "192.168.0.0/16" "10.0.0.0/8")

for range in "${INTERNAL_RANGES[@]}"; do
    iptables -A INPUT -s "$range" -j ACCEPT
    iptables -A OUTPUT -d "$range" -j ACCEPT
done

# E. Established Connections (Modern Syntax)
# Allows return traffic for connections you started (like curl or npm install)
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# F. Whitelist Traffic (Outbound)
iptables -A OUTPUT -m set --match-set allowed-domains dst -j ACCEPT

# G. DROP Policies (Lockdown)
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

echo "✅ Firewall Active."