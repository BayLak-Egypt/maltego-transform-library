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
        self.load_from_json()
        self.setup_ui()

    def setup_ui(self):
        config_group = tk.LabelFrame(self, text=' CONFIGURATION ', font=('Consolas', 10, 'bold'), bg=self.COLORS['bg_card'], fg=self.COLORS['accent'], padx=15, pady=20, bd=1, relief='solid')
        config_group.pack(fill='x', padx=10, pady=10)
        self.update_cb = tk.Checkbutton(config_group, text='CHECK FOR UPDATES ON STARTUP', variable=self.auto_update, bg=self.COLORS['bg_card'], fg='white', selectcolor=self.COLORS['bg_dark'], font=('Consolas', 10), activebackground=self.COLORS['bg_card'])
        self.update_cb.pack(anchor='w')
        save_btn = tk.Button(self, text='SAVE SETTINGS', command=self.handle_save, bg=self.COLORS['accent'], fg=self.COLORS['bg_dark'], bd=0, font=('Consolas', 9, 'bold'), pady=12, cursor='hand2')
        save_btn.pack(fill='x', padx=10, pady=20)

    def load_from_json(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    self.auto_update.set(json.load(f).get('auto_update', False))
            except:
                pass

    def handle_save(self):
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump({'auto_update': self.auto_update.get()}, f, indent=4)
            msg = 'Update ENABLED. Will check on next startup.' if self.auto_update.get() else 'Update DISABLED.'
            messagebox.showinfo('Success', msg)
        except Exception as e:
            messagebox.showerror('Error', f'Save failed: {e}')