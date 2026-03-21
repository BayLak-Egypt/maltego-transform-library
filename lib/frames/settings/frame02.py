import tkinter as tk
from tkinter import messagebox
import json
import os
SECTION_NAME = '● NETWORK & PROXY CONFIG'

class SettingsFrame(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors['bg_dark'], pady=10)
        self.COLORS = colors
        self.settings_file = 'settings.json'
        if not os.path.exists(self.settings_file):
            self.save_to_json(False, '127.0.0.1', '9050')
        self.setup_ui()
        self.load_from_json()

    def setup_ui(self):
        proxy_fm = tk.Frame(self, bg=self.COLORS['bg_card'], padx=15, pady=15)
        proxy_fm.pack(fill='x', padx=10)
        tk.Label(proxy_fm, text='SOCKS5 IP:', font=('Consolas', 9), fg='white', bg=self.COLORS['bg_card']).grid(row=0, column=0, sticky='w')
        self.ip_ent = tk.Entry(proxy_fm, bg=self.COLORS['bg_dark'], fg='white', borderwidth=0, insertbackground='white')
        self.ip_ent.grid(row=0, column=1, padx=10, pady=5, ipady=3, sticky='ew')
        tk.Label(proxy_fm, text='PORT:', font=('Consolas', 9), fg='white', bg=self.COLORS['bg_card']).grid(row=1, column=0, sticky='w')
        self.port_ent = tk.Entry(proxy_fm, bg=self.COLORS['bg_dark'], fg='white', borderwidth=0, insertbackground='white', width=10)
        self.port_ent.grid(row=1, column=1, padx=10, pady=5, ipady=3, sticky='w')
        self.proxy_enabled = tk.BooleanVar()
        self.toggle_cb = tk.Checkbutton(proxy_fm, text='ENABLE SOCKS5', variable=self.proxy_enabled, bg=self.COLORS['bg_card'], fg=self.COLORS['accent'], selectcolor=self.COLORS['bg_dark'], font=('Consolas', 9, 'bold'))
        self.toggle_cb.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky='w')
        save_btn = tk.Button(self, text='APPLY & SAVE SETTINGS', command=self.handle_save, bg=self.COLORS['accent'], fg=self.COLORS['bg_dark'], bd=0, font=('Consolas', 9, 'bold'), pady=8)
        save_btn.pack(fill='x', padx=10, pady=15)

    def save_to_json(self, enabled, ip, port):
        settings = {'proxy': {'enabled': enabled, 'ip': ip, 'port': port}, 'last_updated': '2026-03-21'}
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)

    def load_from_json(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    data = json.load(f)
                    p = data.get('proxy', {})
                    self.proxy_enabled.set(p.get('enabled', False))
                    self.ip_ent.insert(0, p.get('ip', '127.0.0.1'))
                    self.port_ent.insert(0, p.get('port', '9050'))
            except:
                pass

    def handle_save(self):
        self.save_to_json(self.proxy_enabled.get(), self.ip_ent.get(), self.port_ent.get())
        messagebox.showinfo('Success', 'Settings saved to settings.json')