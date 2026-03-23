import tkinter as tk
from tkinter import messagebox
import json
import os

class SettingsFrame(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors['bg_dark'], pady=10)
        self.COLORS = colors
        self.settings_file = 'settings.json'
        self.auto_update = tk.BooleanVar()
        self.full_settings = {}
        self.load_from_json()
        self.setup_ui()

    def setup_ui(self):
        update_group = tk.LabelFrame(self, text=' SYSTEM UPDATES ', font=('Consolas', 10, 'bold'), bg=self.COLORS['bg_card'], fg=self.COLORS['accent'], padx=15, pady=20, bd=1, relief='solid')
        update_group.pack(fill='x', padx=10, pady=10)
        self.update_cb = tk.Checkbutton(update_group, text='ENABLE AUTO-UPDATE ON STARTUP', variable=self.auto_update, bg=self.COLORS['bg_card'], fg='white', selectcolor=self.COLORS['bg_dark'], font=('Consolas', 10), activebackground=self.COLORS['bg_card'])
        self.update_cb.pack(anchor='w')
        info_group = tk.LabelFrame(self, text=' SYSTEM INFO ', font=('Consolas', 10, 'bold'), bg=self.COLORS['bg_card'], fg='#888888', padx=15, pady=15, bd=1, relief='solid')
        info_group.pack(fill='x', padx=10, pady=5)
        last_upd = self.full_settings.get('last_updated', 'Unknown')
        tk.Label(info_group, text=f'LAST SYNC: {last_upd}', font=('Consolas', 8), bg=self.COLORS['bg_card'], fg='#aaaaaa').pack(anchor='w')
        save_btn = tk.Button(self, text='SAVE CONFIGURATION', command=self.handle_save, bg=self.COLORS['accent'], fg=self.COLORS['bg_dark'], bd=0, font=('Consolas', 9, 'bold'), pady=12, cursor='hand2')
        save_btn.pack(fill='x', padx=10, pady=20)

    def load_from_json(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.full_settings = json.load(f)
                    self.auto_update.set(self.full_settings.get('auto_update', False))
            except Exception as e:
                print(f'Error loading settings: {e}')

    def handle_save(self):
        try:
            self.full_settings['auto_update'] = self.auto_update.get()
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.full_settings, f, indent=4)
            messagebox.showinfo('Success', 'Settings updated without affecting other configurations.')
        except Exception as e:
            messagebox.showerror('Error', f'Save failed: {e}')