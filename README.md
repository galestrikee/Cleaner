# 🧹 Termux GUI System Cleaner
A lightweight, native graphical system cleaner built specifically for **Termux-X11**. 

I got tired of typing `pkg clean` and manually deleting hidden `.cache` folders in the terminal, so I built a Python/Tkinter GUI to do it with a single click directly from the XFCE Start Menu.

### ✨ Features
* **1-Click APT Cleanup:** Instantly scan and wipe leftover `.deb` package downloads.
* **Deep Cache Sweep:** Clears out the hidden `~/.cache` folder where XFCE and browsers dump gigabytes of junk.
* **Native Desktop Integration:** Automatically creates a `.desktop` shortcut in your Start Menu/Rofi launcher.

### 🚀 How to Install
Run this single command in your Termux terminal to automatically download the app, install dependencies, and create the Start Menu shortcut:

curl -sL https://raw.githubusercontent.com/galestrikee/Cleaner/main/Install.sh | bash

### TO UNINSTALL TYPE THIS IN TERMINAL 



curl -sL https://raw.githubusercontent.com/galestrikee/Cleaner/main/Uninstall.sh | bash
