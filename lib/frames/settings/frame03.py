import tkinter as tk
from tkinter import ttk, messagebox
import os
SECTION_NAME = 'NETWORK CONFIGURATION'

class SettingsFrame(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors['bg_dark'], pady=10)
        self.COLORS = colors
        self.links_file = 'links.txt'
        if not os.path.exists(self.links_file):
            self._save_to_disk([])
        self.setup_ui()
        self.load_links_into_list()

    def setup_ui(self):
        header = tk.Label(self, text='● SERVER LINKS (AUTO-SAVE)', font=('Consolas', 11, 'bold'), fg=self.COLORS['accent'], bg=self.COLORS['bg_dark'])
        header.pack(anchor='w', padx=10)
        input_fm = tk.Frame(self, bg=self.COLORS['bg_dark'])
        input_fm.pack(fill='x', padx=10, pady=10)
        self.name_ent = tk.Entry(input_fm, bg=self.COLORS['bg_card'], fg='white', borderwidth=0)
        self.name_ent.pack(side='left', fill='x', expand=True, ipady=5, padx=2)
        add_btn = tk.Button(input_fm, text='＋', command=self.add_and_save, bg='#28a745', fg='white', bd=0, padx=15)
        add_btn.pack(side='right', padx=2)
        self.listbox = tk.Listbox(self, bg=self.COLORS['bg_card'], fg='white', bd=0, height=4)
        self.listbox.pack(fill='x', padx=10, pady=5)
        del_btn = tk.Button(self, text='DELETE SELECTED', command=self.delete_and_save, bg='#dc3545', fg='white', bd=0, font=('Segoe UI', 8))
        del_btn.pack(anchor='e', padx=10)

    def _save_to_disk(self, lines):
        with open(self.links_file, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    def load_links_into_list(self):
        self.listbox.delete(0, tk.END)
        if os.path.exists(self.links_file):
            with open(self.links_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        self.listbox.insert(tk.END, line.strip())

    def add_and_save(self):
        data = self.name_ent.get().strip()
        if data:
            with open(self.links_file, 'a', encoding='utf-8') as f:
                f.write(data + '\n')
            self.name_ent.delete(0, tk.END)
            self.load_links_into_list()
            print(f'[Auto-Save] Added: {data}')

    def delete_and_save(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        with open(self.links_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if 0 <= index < len(lines):
            removed = lines.pop(index)
            self._save_to_disk(lines)
            self.load_links_into_list()
            print(f'[Auto-Save] Removed: {removed.strip()}')