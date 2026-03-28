import gi
import os
import sys
import shutil
import subprocess
import math

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gdk, GLib

# --- Core Paths ---
APT_DIR = "/data/data/com.termux/files/usr/var/cache/apt/archives"
CACHE_DIR = os.path.expanduser("~/.cache")

def get_folder_size(path):
    total = 0
    if not os.path.exists(path): return 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                try: total += os.path.getsize(fp)
                except: pass
    return total

def format_size(size_bytes):
    if size_bytes >= (1024**3): return f"{size_bytes / (1024**3):.2f} GB"
    elif size_bytes >= (1024**2): return f"{size_bytes / (1024**2):.1f} MB"
    else: return f"{size_bytes / 1024:.0f} KB"

class TermuxHubApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id="com.galestrike.hub", **kwargs)
        self.check_map = {}
        self.total_found_bytes = 0
        self.selected_bytes = 0

    def do_activate(self):
        # 1. Main Window
        self.win = Adw.ApplicationWindow(application=self, title="CleanIt Hub")
        self.win.set_default_size(450, 750)
        
        # 2. Styling (Removed Dark Mode override to fix glitches)
        css = Gtk.CssProvider()
        css.load_from_data(b"""
            .reddit-orange { background-color: #FF4500; color: white; font-weight: bold; font-size: 16px; padding: 12px; }
            .reddit-orange:hover { background-color: #FF5722; }
            .big-text { font-size: 46px; font-weight: bold; }
        """)
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_USER)

        # 3. Toast Overlay & Nav View
        self.toast_overlay = Adw.ToastOverlay()
        self.win.set_content(self.toast_overlay)

        self.nav_view = Adw.NavigationView()
        self.toast_overlay.set_child(self.nav_view)

        # --- BUILD PAGES ---
        self.build_home_page()
        self.build_cleaner_page()
        
        self.win.present()

    # ==========================================
    # PAGE 1: THE HOME DASHBOARD
    # ==========================================
    def build_home_page(self):
        page = Adw.NavigationPage(title="System Hub", tag="home")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page.set_child(box)

        header = Adw.HeaderBar()
        box.append(header)

        # Dashboard Circle
        dashboard = Gtk.Overlay()
        dashboard.set_margin_top(40)
        dashboard.set_margin_bottom(40)
        box.append(dashboard)

        self.canvas_home = Gtk.DrawingArea()
        self.canvas_home.set_size_request(220, 220)
        self.canvas_home.set_draw_func(self.draw_home_circle, None)
        dashboard.set_child(self.canvas_home)

        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, halign=Gtk.Align.CENTER, valign=Gtk.Align.CENTER)
        total, used, free = shutil.disk_usage("/")
        self.sys_used = used
        self.sys_total = total
        
        usage_label = Gtk.Label(label=format_size(used))
        usage_label.add_css_class("big-text")
        text_box.append(usage_label)
        dashboard.add_overlay(text_box)

        # The Lean Menu (Just 2 Options)
        menu_list = Gtk.ListBox()
        menu_list.add_css_class("boxed-list")
        menu_list.set_margin_start(20)
        menu_list.set_margin_end(20)
        menu_list.connect("row-activated", self.on_menu_clicked)
        box.append(menu_list)

        self.add_menu_item(menu_list, "Cache Cleaner", "Deep clean system cache", "user-trash-symbolic", "cleaner")
        self.add_menu_item(menu_list, "Update CleanIt", "Fetch latest version from GitHub", "browser-download-symbolic", "update_app")

        self.nav_view.add(page)

    def add_menu_item(self, listbox, title, subtitle, icon, action_tag):
        row = Adw.ActionRow(title=title, subtitle=subtitle)
        row.add_prefix(Gtk.Image.new_from_icon_name(icon))
        row.set_name(action_tag) 
        row.set_activatable(True)
        listbox.append(row)

    def draw_home_circle(self, area, cr, width, height, user_data):
        x, y = width / 2.0, height / 2.0
        radius = min(width, height) / 2.0 - 15
        cr.set_source_rgba(1.0, 0.27, 0.0, 1.0) # Reddit Orangered
        cr.set_line_width(16)
        cr.arc(x, y, radius, 0, 2 * math.pi)
        cr.stroke()

    def on_menu_clicked(self, listbox, row):
        action = row.get_name()
        if action == "cleaner":
            self.scan_and_populate() 
            self.nav_view.push_by_tag("cleaner")
        elif action == "update_app":
            self.update_cleanit_app()

    # ==========================================
    # PAGE 2: CACHE CLEANER
    # ==========================================
    def build_cleaner_page(self):
        page = Adw.NavigationPage(title="Cache Cleaner", tag="cleaner")
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        page.set_child(box)

        header = Adw.HeaderBar()
        box.append(header)
        
        select_all_btn = Gtk.ToggleButton(label="Select All")
        select_all_btn.set_active(True)
        select_all_btn.connect("toggled", self.on_select_all_toggled)
        header.pack_end(select_all_btn)

        self.status_page = Adw.StatusPage(title="0 MB", description="Trash Selected", icon_name="user-trash-symbolic")
        box.append(self.status_page)

        scroller = Gtk.ScrolledWindow()
        scroller.set_vexpand(True)
        box.append(scroller)

        self.list_box = Gtk.ListBox()
        self.list_box.set_margin_start(20)
        self.list_box.set_margin_end(20)
        self.list_box.set_margin_bottom(20)
        self.list_box.add_css_class("boxed-list")
        scroller.set_child(self.list_box)

        self.clean_btn = Gtk.Button(label="Clean System")
        self.clean_btn.set_margin_start(40)
        self.clean_btn.set_margin_end(40)
        self.clean_btn.set_margin_bottom(30)
        self.clean_btn.add_css_class("pill")
        self.clean_btn.add_css_class("reddit-orange") 
        self.clean_btn.connect("clicked", self.on_clean_clicked)
        box.append(self.clean_btn)
        self.nav_view.add(page)

    def scan_and_populate(self):
        while child := self.list_box.get_first_child(): self.list_box.remove(child)
        self.check_map.clear()
        
        self.add_row("APT Packages", APT_DIR, get_folder_size(APT_DIR), True)
        if os.path.exists(CACHE_DIR):
            folders = [(i, os.path.join(CACHE_DIR, i), get_folder_size(os.path.join(CACHE_DIR, i))) for i in os.listdir(CACHE_DIR) if os.path.isdir(os.path.join(CACHE_DIR, i)) and get_folder_size(os.path.join(CACHE_DIR, i)) > 0]
            for n, p, s in sorted(folders, key=lambda x: x[2], reverse=True)[:5]:
                self.add_row(n.capitalize() + " Cache", p, s, False)
        self.update_total()

    def add_row(self, name, path, size, is_apt):
        row = Adw.ActionRow(title=name, subtitle=format_size(size))
        check = Gtk.CheckButton()
        check.set_active(True)
        check.set_valign(Gtk.Align.CENTER)
        check.connect("toggled", lambda x: self.update_total())
        row.add_prefix(check)
        self.list_box.append(row)
        self.check_map[check] = {"path": path, "size": size, "is_apt": is_apt}

    def on_select_all_toggled(self, btn):
        for check in self.check_map.keys(): check.set_active(btn.get_active())
        self.update_total()

    def update_total(self):
        total = sum(d["size"] for c, d in self.check_map.items() if c.get_active())
        formatted = format_size(total)
        self.status_page.set_title(formatted)
        self.clean_btn.set_label(f"Wipe {formatted}")

    def on_clean_clicked(self, btn):
        cleaned = False
        for c, d in self.check_map.items():
            if c.get_active() and d["size"] > 0:
                try:
                    if d["is_apt"]: subprocess.run(["pkg", "clean"], check=True)
                    else: shutil.rmtree(d["path"])
                    cleaned = True
                except: pass
        if cleaned:
            self.show_toast("🚀 Caches Wiped!")
            self.nav_view.pop()

    # ==========================================
    # SELF-UPDATER ENGINE
    # ==========================================
    def update_cleanit_app(self):
        self.show_toast("⬇️ Fetching latest CleanIt version from GitHub...")
        
        # NOTE: Make sure this link perfectly matches your Raw GitHub file!
        github_url = "https://raw.githubusercontent.com/galestrikee/Cleaner/main/cleanit.py"
        current_file = os.path.abspath(__file__)

        try:
            # Download new code and overwrite this file
            subprocess.run(["curl", "-sL", github_url, "-o", current_file], check=True)
            self.show_toast("✅ Update Successful! Restarting app...")
            # Restart the app automatically after 2 seconds
            GLib.timeout_add_seconds(2, lambda: os.execv(sys.executable, ['python'] + sys.argv))
        except Exception as e:
            self.show_toast("❌ Update failed. Check internet connection.")

    # --- TOAST NOTIFICATION HELPER ---
    def show_toast(self, message):
        toast = Adw.Toast.new(message)
        toast.set_timeout(3)
        self.toast_overlay.add_toast(toast)

if __name__ == "__main__":
    app = TermuxHubApp()
    app.run(None)
