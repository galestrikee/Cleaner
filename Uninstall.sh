#!/bin/bash

echo "===================================="
echo " Uninstalling Termux System Cleaner "
echo "===================================="

echo "[*] Removing app folder and code..."
rm -rf ~/.termux-cleaner

echo "[*] Removing XFCE Start Menu shortcut..."
rm -f ~/.local/share/applications/termux-cleaner.desktop

echo "[+] Uninstalled successfully! The app has been wiped from your system."
