import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import shutil
import threading
import importlib.util
import requests
from PIL import Image, ImageTk
from io import BytesIO
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from searchiconlibrary import IconManager
from styles.styles import COLORS
from styles.btnstyle import ActionButton
from lib.msg import show_msg
from lib.serverload import ServerEngine, LinkManager

class LibrarySection(tk.Frame):

    def __init__(self, parent, title, color, colors_dict, icon_manager, on_action, btn_text, btn_type, is_remote=False):
        super().__init__(parent, bg=colors_dict['bg_dark'])
        self.COLORS = colors_dict
        self.icon_manager = icon_manager
        self.on_action = on_action
        self.btn_text = btn_text
        self.btn_type = btn_type
        self.is_remote = is_remote
        self.full_data = []
        self.icon_cache = {}
        self.section_color = color
        self._is_loading = False
        header = tk.Frame(self, bg=self.COLORS['bg_card'])
        header.pack(fill='x', pady=(0, 2))
        tk.Frame(header, bg=color, width=4).pack(side='left', fill='y')
        tk.Label(header, text=title, font=('Consolas', 10, 'bold'), fg=color, bg=self.COLORS['bg_card'], padx=10, pady=8).pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', lambda *args: self.filter_display())
        search_cnt = tk.Frame(header, bg=self.COLORS['bg_dark'], padx=5)
        search_cnt.pack(side='right', padx=10, pady=5)
        tk.Entry(search_cnt, textvariable=self.search_var, bg=self.COLORS['bg_dark'], fg=self.COLORS['text_main'], insertbackground=color, font=('Segoe UI', 9), relief='flat', width=15).pack(side='left', padx=5)
        self.content_wrapper = tk.Frame(self, bg=self.COLORS['bg_dark'])
        self.content_wrapper.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(self.content_wrapper, bg=self.COLORS['bg_dark'], highlightthickness=0, height=180)
        self.scrollbar = ttk.Scrollbar(self.content_wrapper, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.COLORS['bg_dark'])
        self.scrollable_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas_win = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_win, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        self.loading_overlay = tk.Frame(self.content_wrapper, bg=self.COLORS['bg_dark'])
        self.style_name = f'{title.replace(' ', '')}.Horizontal.TProgressbar'
        style = ttk.Style()
        style.theme_use('default')
        style.configure(self.style_name, thickness=2, troughcolor=self.COLORS['bg_dark'], background=color, bordercolor=self.COLORS['bg_dark'])
        self.status_lbl = tk.Label(self.loading_overlay, text='⚡ SYNCING DATA', font=('Consolas', 8, 'bold'), fg=color, bg=self.COLORS['bg_dark'])
        self.status_lbl.place(relx=0.5, rely=0.45, anchor='center')
        self.progress = ttk.Progressbar(self.loading_overlay, orient='horizontal', length=150, mode='indeterminate', style=self.style_name)
        self.progress.place(relx=0.5, rely=0.55, anchor='center')

    def set_loading(self, state=True):
        self._is_loading = state
        if state:
            self.loading_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.loading_overlay.lift()
            self.progress.start(10)
        else:
            self.progress.stop()
            self.loading_overlay.place_forget()
            self.filter_display()

    def update_data(self, data_list):
        self.full_data = data_list if data_list is not None else []
        self.set_loading(False)

    def filter_display(self):
        for w in self.scrollable_frame.winfo_children():
            w.destroy()
        if self._is_loading:
            return
        q = self.search_var.get().lower().strip()
        found_count = 0
        for item in self.full_data:
            if q and q not in item[0].lower():
                continue
            self._create_card(item)
            found_count += 1
        if found_count == 0:
            status_msg = ''
            if self.full_data and len(self.full_data) > 0:
                status_msg = f"🔍 NO RESULTS FOR '{q}'"
            elif self.is_remote:
                status_msg = '❌ NO CONNECTION FOUND'
            else:
                return
            if status_msg:
                msg_container = tk.Frame(self.scrollable_frame, bg=self.COLORS['bg_dark'], pady=60)
                msg_container.pack(fill='both', expand=True)
                tk.Label(msg_container, text=status_msg, font=('Consolas', 10, 'bold'), fg=self.COLORS['text_dim'], bg=self.COLORS['bg_dark']).pack(expand=True)

    def _create_card(self, item):
        name, status = (item[0], item[1])
        icon_url = item[2] if len(item) > 2 else None
        card = tk.Frame(self.scrollable_frame, bg=self.COLORS['bg_card'], pady=6, padx=12)
        card.pack(fill='x', pady=1, padx=2)
        icon_label = tk.Label(card, bg=self.COLORS['bg_card'], width=35)
        icon_label.pack(side='left', padx=(0, 10))
        if not self.is_remote:
            if self.icon_manager:
                img = self.icon_manager.get_lib_icon(name, size=(28, 28))
                if img:
                    icon_label.config(image=img)
                    icon_label.image = img
                else:
                    icon_label.config(text='📁', font=('Segoe UI', 14), fg=self.COLORS['text_dim'])
            else:
                icon_label.config(text='📁', font=('Segoe UI', 14), fg=self.COLORS['text_dim'])
        elif icon_url and str(icon_url).startswith('http'):
            threading.Thread(target=self._load_remote_icon, args=(icon_label, icon_url, name), daemon=True).start()
        else:
            icon_label.config(text='☁️', font=('Segoe UI', 14), fg=self.COLORS['text_dim'])
        info = tk.Frame(card, bg=self.COLORS['bg_card'])
        info.pack(side='left', fill='both', expand=True)
        tk.Label(info, text=name.upper(), font=('Consolas', 9, 'bold'), fg=self.COLORS['text_main'], bg=self.COLORS['bg_card'], anchor='w').pack(fill='x')
        tk.Label(info, text=status, font=('Segoe UI', 7), fg=self.COLORS['text_dim'], bg=self.COLORS['bg_card'], anchor='w').pack(fill='x')
        if 'ActionButton' in globals():
            ActionButton(card, text=self.btn_text, colors=self.COLORS, btn_type=self.btn_type, width=85, height=24, command=lambda n=name: self.on_action(n)).pack(side='right')
        else:
            tk.Button(card, text=self.btn_text, command=lambda n=name: self.on_action(n), bg=self.COLORS['bg_dark'], fg=self.COLORS['text_main'], relief='flat', padx=10).pack(side='right')

    def _load_remote_icon(self, label, url, name):
        try:
            r = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'}, verify=False)
            if r.status_code == 200:
                img = Image.open(BytesIO(r.content)).convert('RGBA').resize((28, 28), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.icon_cache[name] = photo
                if label.winfo_exists():
                    label.after(0, lambda: self._apply_icon(label, photo))
        except:
            if label.winfo_exists():
                label.after(0, lambda: label.config(text='📦'))

    def _apply_icon(self, label, photo):
        label.config(image=photo)
        label.image = photo

class LibraryInfoFrame(tk.Frame):

    def __init__(self, parent, lib_dir, filtered_libs=None):
        self.COLORS = COLORS
        super().__init__(parent, bg=self.COLORS['bg_dark'])
        self.lib_dir = lib_dir
        self.engine = ServerEngine()
        self.link_mgr = LinkManager('links.txt')
        self.icon_manager = IconManager(self.lib_dir) if 'IconManager' in globals() else None
        self.lib_sources = {}
        self.servers_list = {}
        self.create_widgets()

    def create_widgets(self):
        controls = tk.Frame(self, bg=self.COLORS['bg_card'], pady=5)
        controls.pack(fill='x', padx=30, pady=(10, 0))
        tk.Label(controls, text='SELECT SERVER:', font=('Consolas', 8, 'bold'), fg=self.COLORS['accent'], bg=self.COLORS['bg_card']).pack(side='left', padx=10)
        self.server_combo = ttk.Combobox(controls, state='readonly', width=25)
        self.server_combo.pack(side='left', padx=5)
        self.server_combo.bind('<<ComboboxSelected>>', lambda e: self.refresh_cloud())
        self.global_section = LibrarySection(self, 'CLOUD REPOSITORY', self.COLORS['accent'], self.COLORS, self.icon_manager, self.start_install, 'INSTALL', 'accent', is_remote=True)
        self.global_section.pack(fill='both', expand=True, padx=30, pady=10)
        self.local_section = LibrarySection(self, 'LOCAL STORAGE', '#00FF00', self.COLORS, self.icon_manager, self.uninstall_lib, 'UNINSTALL', 'danger')
        self.local_section.pack(fill='both', expand=True, padx=30, pady=(0, 20))
        self.load_links()

    def load_links(self):
        self.servers_list = self.link_mgr.load_all_servers()
        titles = ['ALL SERVERS'] + list(self.servers_list.keys())
        self.server_combo['values'] = titles
        if titles:
            self.server_combo.current(0)
            self.refresh_all()

    def refresh_cloud(self):
        self.global_section.set_loading(True)

        def task():
            selection = self.server_combo.get()
            all_cloud_libs = []
            targets = self.link_mgr.filter_targets(self.servers_list, selection)
            for title, info in targets:
                d_name, url = (info['driver'], info['url'])
                if d_name in self.engine.drivers:
                    try:
                        libs = self.engine.drivers[d_name].fetch_data(url)
                        for item in libs:
                            all_cloud_libs.append(item)
                            self.lib_sources[item[0]] = (d_name, url)
                    except Exception as e:
                        print(f'Error connecting to {title}: {e}')
            local_folders = set()
            if os.path.exists(self.lib_dir):
                local_folders = {d for d in os.listdir(self.lib_dir) if os.path.isdir(os.path.join(self.lib_dir, d))}
            final_list = [x for x in all_cloud_libs if x[0] not in local_folders]
            self.after(0, lambda: self.global_section.update_data(final_list))
        threading.Thread(target=task, daemon=True).start()

    def refresh_local(self):
        self.local_section.set_loading(True)

        def task():
            if not os.path.exists(self.lib_dir):
                os.makedirs(self.lib_dir)
            libs = [(d, 'Ready') for d in os.listdir(self.lib_dir) if os.path.isdir(os.path.join(self.lib_dir, d))]
            self.after(0, lambda: self.local_section.update_data(libs))
        threading.Thread(target=task, daemon=True).start()

    def refresh_all(self):
        self.refresh_cloud()
        self.refresh_local()

    def start_install(self, name):
        if name not in self.lib_sources:
            return
        self.global_section.set_loading(True)
        d_name, url = self.lib_sources[name]

        def download():
            try:
                success = self.engine.drivers[d_name].install_data(name, url, os.path.join(self.lib_dir, name))
                if success:
                    self.after(0, lambda: [show_msg(self.winfo_toplevel(), f'Success: {name}', type='success'), self.refresh_all()])
                else:
                    raise Exception()
            except:
                self.after(0, lambda: self.global_section.set_loading(False))
        threading.Thread(target=download, daemon=True).start()

    def uninstall_lib(self, name):
        if messagebox.askyesno('Confirm', f'Delete {name}?'):
            try:
                shutil.rmtree(os.path.join(self.lib_dir, name))
                self.refresh_all()
            except Exception as e:
                messagebox.showerror('Error', str(e))