import tkinter as tk
from tkinter import messagebox
import json
import os
# الربط مع ملف upgrade.py
import lib.upgrade as upgrade 

class SettingsFrame(tk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors['bg_dark'], pady=10)
        self.COLORS = colors
        self.settings_file = 'settings.json'
        
        self.auto_update = tk.BooleanVar()
        self.load_from_json()
        self.setup_ui()

    def setup_ui(self):
        # جروب CONFIGURATION
        config_group = tk.LabelFrame(
            self, 
            text=" CONFIGURATION ", 
            font=('Consolas', 10, 'bold'),
            bg=self.COLORS['bg_card'], 
            fg=self.COLORS['accent'],
            padx=15, 
            pady=20,
            bd=1,
            relief='solid'
        )
        config_group.pack(fill='x', padx=10, pady=10)

        # الـ Checkbox الوحيد
        self.update_cb = tk.Checkbutton(
            config_group, 
            text='ENABLE AUTOMATIC UPDATES', 
            variable=self.auto_update, 
            bg=self.COLORS['bg_card'], 
            fg='white', 
            selectcolor=self.COLORS['bg_dark'], 
            font=('Consolas', 10),
            activebackground=self.COLORS['bg_card']
        )
        self.update_cb.pack(anchor='w')

        # زر الحفظ والـ Sync
        save_btn = tk.Button(
            self, 
            text='SAVE & CHECK UPDATES', 
            command=self.handle_save, 
            bg=self.COLORS['accent'], 
            fg=self.COLORS['bg_dark'], 
            bd=0, 
            font=('Consolas', 9, 'bold'), 
            pady=12,
            cursor='hand2'
        )
        save_btn.pack(fill='x', padx=10, pady=20)

    def load_from_json(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.auto_update.set(data.get('auto_update', False))
            except:
                pass

    def handle_save(self):
        # 1. حفظ الإعدادات في JSON (بدون بروكسي)
        settings = {'auto_update': self.auto_update.get()}
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4)

        # 2. تشغيل الـ Sync من ملف upgrade
        if self.auto_update.get():
            # المناداة على الدالة من الموديول المستورد
            did_update = upgrade.start_sync() 
            if did_update:
                messagebox.showinfo('Sync', 'System updated successfully! Restarting...')
            else:
                messagebox.showinfo('Status', 'No updates found. System is up to date.')
        else:
            messagebox.showinfo('Success', 'Settings saved (Updates disabled).')
