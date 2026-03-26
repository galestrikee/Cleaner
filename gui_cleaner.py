import os
import tkinter as tk
from tkinter import messagebox

# --- The Brains (Functions) ---
def get_folder_size(folder_path):
    """Scans the folder and returns the size in MB"""
    total_size = 0
    if os.path.exists(folder_path):
        for dirpath, _, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
    return round(total_size / (1024 * 1024), 2)

def clean_apt():
    apt_dir = "/data/data/com.termux/files/usr/var/cache/apt/archives"
    mb = get_folder_size(apt_dir)
    
    # Pop-up confirmation box
    if mb > 0:
        confirm = messagebox.askyesno("Scan Complete", f"Found {mb} MB of package installers.\nDo you want to delete them?")
        if confirm:
            os.system("pkg clean")
            messagebox.showinfo("Success", f"Cleared {mb} MB of storage!")
    else:
        messagebox.showinfo("Clean", "Your package vault is already empty!")

def clean_cache():
    cache_dir = "/data/data/com.termux/files/home/.cache"
    mb = get_folder_size(cache_dir)
    
    if mb > 0:
        confirm = messagebox.askyesno("Scan Complete", f"Found {mb} MB of hidden system caches.\nDo you want to delete them?")
        if confirm:
            os.system(f"rm -rf {cache_dir}/*")
            messagebox.showinfo("Success", f"Cleared {mb} MB of storage!")
    else:
        messagebox.showinfo("Clean", "Your system cache is already empty!")


# --- The Face (GUI Window Design) ---
app = tk.Tk()
app.title("Termux Cleaner")
app.geometry("320x250") # Sets the window size

# Title Label
title_label = tk.Label(app, text="System Cleaner", font=("Arial", 16, "bold"))
title_label.pack(pady=20) # 'pack' places it on the screen, pady adds spacing

# Buttons
btn_apt = tk.Button(app, text="Scan & Clean PKG Cache", command=clean_apt, width=25, height=2)
btn_apt.pack(pady=5)

btn_cache = tk.Button(app, text="Scan & Clean Deep Cache", command=clean_cache, width=25, height=2)
btn_cache.pack(pady=5)

btn_exit = tk.Button(app, text="Exit App", command=app.quit, width=15)
btn_exit.pack(pady=15)

# This tells the app to stay open and wait for you to click something
app.mainloop()
