import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import shutil

# --- Core Paths ---
APT_DIR = "/data/data/com.termux/files/usr/var/cache/apt/archives"
THUMB_DIR = os.path.expanduser("~/.cache/thumbnails")
CACHE_DIR = os.path.expanduser("~/.cache")

# --- Helper Math Functions ---
def get_folder_size(path):
    total_size = 0
    if not os.path.exists(path): return 0
    if os.path.isfile(path): return os.path.getsize(path)
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                try: total_size += os.path.getsize(fp)
                except: pass
    return total_size

def format_mb(size_in_bytes):
    return f"{size_in_bytes / (1024 * 1024):.2f} MB"

def format_gb(size_in_bytes):
    return f"{size_in_bytes / (1024**3):.2f} GB"

# --- Main App Logic ---
def refresh_ui():
    status_var.set("Status: Scanning system...")
    root.update() 
    
    # Calculate Cache Sizes
    apt_size = get_folder_size(APT_DIR)
    thumb_size = get_folder_size(THUMB_DIR)
    deep_size = max(0, get_folder_size(CACHE_DIR) - thumb_size) 
    
    chk_apt.config(text=f"APT Packages ({format_mb(apt_size)})")
    chk_thumbs.config(text=f"Image Thumbnails ({format_mb(thumb_size)})")
    chk_deep.config(text=f"Deep App Caches ({format_mb(deep_size)})")
    
    # Calculate Device Storage (Scanning the Termux home directory partition)
    total, used, free = shutil.disk_usage(os.path.expanduser("~"))
    storage_lbl.config(text=f"Storage: {format_gb(used)} Used  |  {format_gb(free)} Free")
    
    status_var.set("Status: Ready to clean")

def clean_selected():
    cleaned = False
    status_var.set("Status: Cleaning in progress...")
    root.update()
    
    if var_apt.get():
        try:
            subprocess.run(["pkg", "clean"], check=True)
            cleaned = True
        except: pass
            
    if var_thumbs.get() and os.path.exists(THUMB_DIR):
        try:
            shutil.rmtree(THUMB_DIR)
            cleaned = True
        except: pass

    if var_deep.get() and os.path.exists(CACHE_DIR):
        for item in os.listdir(CACHE_DIR):
            if item == "thumbnails" and not var_thumbs.get(): continue
            item_path = os.path.join(CACHE_DIR, item)
            try:
                if os.path.isfile(item_path): os.remove(item_path)
                elif os.path.isdir(item_path): shutil.rmtree(item_path)
            except: pass
        cleaned = True

    refresh_ui()
    if cleaned:
        messagebox.showinfo("Success", "Selected junk files have been vaporized!")
    else:
        messagebox.showinfo("Info", "Nothing was selected or nothing to clean.")

# --- Dark Mode GUI Setup ---
root = tk.Tk()
root.title("cleanit_v1.2.1")
root.geometry("420x360") # Made taller for the storage bar

# Customizing the Theme
BG_COLOR = "#1e1e2e"
FG_COLOR = "#cdd6f4"
ACCENT_COLOR = "#f38ba8"

root.configure(bg=BG_COLOR)

style = ttk.Style()
style.theme_use('clam') 

style.configure('.', background=BG_COLOR, foreground=FG_COLOR, font=("Arial", 10))
style.configure('TCheckbutton', background=BG_COLOR, foreground=FG_COLOR, focuscolor=BG_COLOR)
style.map('TCheckbutton', background=[('active', BG_COLOR)]) 

# Main Container
frame = tk.Frame(root, bg=BG_COLOR, padx=20, pady=15)
frame.pack(expand=True, fill="both")

# --- NEW: Storage Info Bar ---
storage_lbl = tk.Label(frame, text="Calculating Storage...", font=("Arial", 11, "bold"), bg="#181825", fg="#a6e3a1", pady=8)
storage_lbl.pack(fill="x", pady=(0, 15))

# UI Elements
tk.Label(frame, text="Select areas to clean:", font=("Arial", 12, "bold"), bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", pady=(0, 10))

var_apt = tk.BooleanVar(value=True)
var_thumbs = tk.BooleanVar(value=True)
var_deep = tk.BooleanVar(value=False)

chk_apt = ttk.Checkbutton(frame, text="Calculating...", variable=var_apt)
chk_apt.pack(anchor="w", pady=4)

chk_thumbs = ttk.Checkbutton(frame, text="Calculating...", variable=var_thumbs)
chk_thumbs.pack(anchor="w", pady=4)

chk_deep = ttk.Checkbutton(frame, text="Calculating...", variable=var_deep)
chk_deep.pack(anchor="w", pady=4)

# Warning Text
tk.Label(frame, text="* Deep cache may sign you out of websites.", fg=ACCENT_COLOR, bg=BG_COLOR, font=("Arial", 9, "italic")).pack(anchor="w", pady=(10, 20))

# Clean Button
btn = tk.Button(frame, text="Clean Selected", command=clean_selected, bg=ACCENT_COLOR, fg="#11111b", font=("Arial", 11, "bold"), width=15, pady=6, borderwidth=0, cursor="hand2")
btn.pack()

# Status Bar
status_var = tk.StringVar()
status_var.set("Status: Initializing...")
status_bar = tk.Label(root, textvariable=status_var, bd=1, relief="sunken", anchor="w", bg="#181825", fg="#a6adc8", font=("Arial", 9), padx=10, pady=5)
status_bar.pack(side="bottom", fill="x")

refresh_ui()

root.mainloop()
