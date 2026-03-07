import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import shutil
import math
from lib.msg import show_msg
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from searchiconlibrary import IconManager
from styles.styles import COLORS
from styles.btnstyle import ActionButton
from styles.search import SearchHeader

class LibraryInfoFrame(tk.Frame):

    def __init__(self, parent, lib_dir, filtered_libs):
        self.COLORS = COLORS
        if 'danger' not in self.COLORS:
            self.COLORS['danger'] = '#ff4444'
        super().__init__(parent, bg=self.COLORS['bg_dark'])
        self.lib_dir = lib_dir
        self.filtered_libs = filtered_libs
        self.icon_manager = IconManager(self.lib_dir)
        self.icon_cache = {}
        self.create_widgets()

    def create_widgets(self):
        self.header = SearchHeader(self, self.COLORS, on_search_callback=lambda q: self.refresh_data())
        self.header.pack(fill='x', padx=40, pady=(30, 20))
        container = tk.Frame(self, bg=self.COLORS['bg_dark'])
        container.pack(fill='both', expand=True, padx=40, pady=(0, 20))
        self.canvas = tk.Canvas(container, bg=self.COLORS['bg_dark'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.COLORS['bg_dark'])
        self.scrollable_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.refresh_data()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def refresh_data(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        query = self.header.get_query().lower() if self.header.get_query() else ''
        if not os.path.exists(self.lib_dir):
            return
        ready_names = [l['folder_name'] for l in self.filtered_libs]
        for d in sorted(os.listdir(self.lib_dir)):
            path = os.path.join(self.lib_dir, d)
            if os.path.isdir(path):
                if query and query not in d.lower():
                    continue
                is_ready = d in ready_names
                self.create_item_card(d, is_ready)

    def create_item_card(self, name, is_ready):
        status_text = '● SYSTEM READY' if is_ready else '○ LOADED / INACTIVE'
        status_color = self.COLORS['accent'] if is_ready else self.COLORS['text_dim']
        card = tk.Frame(self.scrollable_frame, bg=self.COLORS['bg_card'], pady=12, padx=15)
        card.pack(fill='x', pady=5, padx=2)
        tk.Frame(card, bg=self.COLORS['accent'], width=4).pack(side='left', fill='y')
        icon_img = self.icon_manager.get_lib_icon(name, size=(40, 40))
        if icon_img:
            self.icon_cache[name] = icon_img
            tk.Label(card, image=icon_img, bg=self.COLORS['bg_card']).pack(side='left', padx=15)
        else:
            tk.Label(card, text='📁', font=('Segoe UI', 20), fg=self.COLORS['text_dim'], bg=self.COLORS['bg_card']).pack(side='left', padx=15)
        info_frame = tk.Frame(card, bg=self.COLORS['bg_card'])
        info_frame.pack(side='left', fill='both', expand=True)
        tk.Label(info_frame, text=name.upper(), font=('Consolas', 11, 'bold'), fg=self.COLORS['text_main'], bg=self.COLORS['bg_card'], anchor='w').pack(fill='x')
        tk.Label(info_frame, text=status_text, font=('Segoe UI', 8, 'bold'), fg=status_color, bg=self.COLORS['bg_card'], anchor='w').pack(fill='x')
        actions_frame = tk.Frame(card, bg=self.COLORS['bg_card'])
        actions_frame.pack(side='right', padx=5)
        btn_del = ActionButton(actions_frame, text='UNINSTALL', colors=self.COLORS, btn_type='danger', width=100, height=30, command=lambda n=name: self.uninstall_lib(n))
        btn_del.pack(side='right', padx=5)

    def uninstall_lib(self, folder_name):
        confirm = messagebox.askyesno('Uninstall', f"Delete '{folder_name}' permanently?")
        if confirm:
            try:
                path = os.path.join(self.lib_dir, folder_name)
                if os.path.exists(path):
                    shutil.rmtree(path)
                    self.refresh_data()
                    show_msg(self.winfo_toplevel(), f'Deleted successfully. {folder_name} Success', type='success')
            except Exception as e:
                show_msg(self.winfo_toplevel(), f'Could not delete: {e}  Error', type='error')