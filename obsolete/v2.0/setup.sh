#!/bin/bash

set -euo pipefail

echo "[*] Installing PastebinSearch"

if ! command -v curl &> /dev/null; then
    echo "[*] Installing dependencies..."
    sudo apt-get update && sudo apt-get install -y curl
fi

echo "[*] Downloading latest version..."
sudo curl -sSL https://raw.githubusercontent.com/byFranke/PastebinSearch/main/pastebinsearch \
    -o /usr/bin/pastebinsearch

echo "[*] Setting permissions..."
sudo chmod 755 /usr/bin/pastebinsearch

echo "[+] Installation complete!"
echo "  - Run 'pastebinsearch --help' for usage instructions"
echo "  - Use 'pastebinsearch --update' to update later"
