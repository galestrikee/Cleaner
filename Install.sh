#!/bin/bash

echo "===================================="
echo "  Installing Termux System Cleaner  "
echo "===================================="

echo "[*] Installing GUI dependencies..."
pkg install python-tkinter -y

echo "[*] Setting up app directories..."
mkdir -p ~/.termux-cleaner
mkdir -p ~/.local/share/applications

echo "[*] Downloading app files..."
curl -sL "https://raw.githubusercontent.com/galestrikee/Cleaner/main/gui_cleaner.py" -o ~/.termux-cleaner/gui_cleaner.py
curl -sL "https://raw.githubusercontent.com/galestrikee/Cleaner/main/logo.png" -o ~/.termux-cleaner/logo.png

echo "[*] Adding shortcut to XFCE Start Menu..."
cat <<EOF > ~/.local/share/applications/termux-cleaner.desktop
[Desktop Entry]
Version=1.0
Type=Application
Name=Termux Cleaner
Comment=Clean your system caches
Exec=python /data/data/com.termux/files/home/.termux-cleaner/gui_cleaner.py
Icon=/data/data/com.termux/files/home/.termux-cleaner/logo.png
Categories=System;Utility;
Terminal=false
EOF

echo "[+] Installation Complete! Launch it from your Start Menu."
