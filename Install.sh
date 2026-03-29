#!/bin/bash

echo "===================================="
echo "    Installing CleanIt Hub v4.0     "
echo "===================================="

echo "[*] Updating package list..."
pkg update -y

echo "[*] Installing Native GTK4 dependencies..."
# This replaces python-tkinter with the heavy-duty Linux UI packages
pkg install python gtk4 libadwaita -y

echo "[*] Setting up app directories..."
mkdir -p ~/.termux-cleaner
mkdir -p ~/.local/share/applications

echo "[*] Downloading CleanIt Hub..."
# This downloads the file to a hidden folder so it doesn't clutter their home directory
curl -sL "https://raw.githubusercontent.com/galestrikee/Cleaner/main/cleanit.py" -o ~/.termux-cleaner/cleanit.py

echo "[*] Downloading Icon..."
curl -sL "https://raw.githubusercontent.com/galestrikee/Cleaner/main/logo.png" -o ~/.termux-cleaner/logo.png

echo "[*] Adding shortcut to XFCE Start Menu..."
# Creates the slick Start Menu icon just like a real OS
cat <<EOF > ~/.local/share/applications/cleanit-hub.desktop
[Desktop Entry]
Version=4.0
Type=Application
Name=CleanIt Hub
Comment=Termux System Optimizer & Cleaner
Exec=python /data/data/com.termux/files/home/.termux-cleaner/cleanit.py
Icon=/data/data/com.termux/files/home/.termux-cleaner/logo.png
Categories=System;Utility;Settings;
Terminal=false
EOF

echo "===================================="
echo "[+] Installation Complete! 🚀"
echo "[+] Look for 'CleanIt Hub' in your Start Menu."
echo "===================================="
