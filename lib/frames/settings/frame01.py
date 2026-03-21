import tkinter as tk
from tkinter import ttk, messagebox
import os
SECTION_NAME = '● TRANSFORM REPOSITORY MANAGER SERVERS'

class SettingsFrame(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors['bg_dark'], pady=15)
        self.COLORS = colors
        self.links_file = 'links.txt'
        self.servers_dir = 'servers'
        if not os.path.exists(self.links_file):
            with open(self.links_file, 'w', encoding='utf-8') as f:
                pass
        if not os.path.exists(self.servers_dir):
            os.makedirs(self.servers_dir)
        self.setup_ui()
        self.load_links_to_table()

    def get_available_servers(self):
        servers = []
        try:
            for file in os.listdir(self.servers_dir):
                if file.endswith('.py') and file != '__init__.py':
                    servers.append(file.replace('.py', ''))
        except Exception as e:
            print(f'Error scanning servers: {e}')
        return servers if servers else ['None']

    def setup_ui(self):
        header_fm = tk.Frame(self, bg=self.COLORS['bg_dark'])
        header_fm.pack(fill='x', padx=20, pady=(0, 10))
        input_fm = tk.Frame(self, bg=self.COLORS['bg_card'], padx=15, pady=15)
        input_fm.pack(fill='x', padx=20, pady=5)
        grid_fm = tk.Frame(input_fm, bg=self.COLORS['bg_card'])
        grid_fm.pack(fill='x', side='left', expand=True)
        tk.Label(grid_fm, text='NAME', fg='#666', bg=self.COLORS['bg_card'], font=('Consolas', 8)).grid(row=0, column=0, sticky='w')
        self.name_ent = tk.Entry(grid_fm, bg='#2d2d2d', fg='white', bd=0, font=('Segoe UI', 10))
        self.name_ent.grid(row=1, column=0, padx=5, pady=2, sticky='ew', ipady=3)
        tk.Label(grid_fm, text='SERVER TYPE', fg='#666', bg=self.COLORS['bg_card'], font=('Consolas', 8)).grid(row=0, column=1, sticky='w')
        available_srv = self.get_available_servers()
        self.server_combo = ttk.Combobox(grid_fm, values=available_srv, state='readonly', width=12)
        if available_srv:
            self.server_combo.current(0)
        self.server_combo.grid(row=1, column=1, padx=5, pady=2, ipady=1)
        tk.Label(grid_fm, text='URL / ENDPOINT', fg='#666', bg=self.COLORS['bg_card'], font=('Consolas', 8)).grid(row=0, column=2, sticky='w')
        self.link_ent = tk.Entry(grid_fm, bg='#2d2d2d', fg='white', bd=0, font=('Segoe UI', 10))
        self.link_ent.grid(row=1, column=2, padx=5, pady=2, sticky='ew', ipady=3)
        grid_fm.columnconfigure(0, weight=1)
        grid_fm.columnconfigure(2, weight=2)
        add_btn = tk.Button(input_fm, text='＋ ADD', command=self.add_and_save, bg=self.COLORS['accent'], fg='black', font=('Segoe UI', 9, 'bold'), bd=0, padx=20, cursor='hand2')
        add_btn.pack(side='right', padx=(10, 0))
        table_fm = tk.Frame(self, bg=self.COLORS['bg_dark'])
        table_fm.pack(fill='both', expand=True, padx=20, pady=10)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background='#1a1a1a', foreground='#ccc', fieldbackground='#1a1a1a', rowheight=30, borderwidth=0)
        style.configure('Treeview.Heading', background='#2d2d2d', foreground=self.COLORS['accent'], font=('Segoe UI', 9, 'bold'))
        style.map('Treeview', background=[('selected', self.COLORS['accent'])], foreground=[('selected', 'black')])
        self.tree = ttk.Treeview(table_fm, columns=('name', 'server', 'link'), show='headings')
        self.tree.heading('name', text=' NAME')
        self.tree.heading('server', text=' SERVER TYPE')
        self.tree.heading('link', text=' LINK / API URL')
        self.tree.column('name', width=130)
        self.tree.column('server', width=100, anchor='center')
        self.tree.column('link', width=350)
        self.tree.pack(side='left', fill='both', expand=True)
        sb = ttk.Scrollbar(table_fm, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side='right', fill='y')
        tk.Button(self, text='DELETE SELECTED', command=self.delete_and_save, bg='#333', fg='#ff5555', bd=0, font=('Segoe UI', 8, 'bold'), padx=15, pady=5, cursor='hand2').pack(anchor='e', padx=20)

    def load_links_to_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        if os.path.exists(self.links_file):
            with open(self.links_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '|' in line:
                        parts = line.strip().split('|')
                        if len(parts) == 3:
                            self.tree.insert('', tk.END, values=(parts[0], parts[1], parts[2]))

    def add_and_save(self):
        name = self.name_ent.get().strip()
        srv = self.server_combo.get()
        link = self.link_ent.get().strip()
        if name and srv and link:
            with open(self.links_file, 'a', encoding='utf-8') as f:
                f.write(f'{name}|{srv}|{link}\n')
            self.load_links_to_table()
            self.name_ent.delete(0, tk.END)
            self.link_ent.delete(0, tk.END)
        else:
            messagebox.showwarning('Incomplete', 'Please fill Name and Link fields.')

    def delete_and_save(self):
        selected = self.tree.selection()
        if not selected:
            return
        index = self.tree.index(selected[0])
        with open(self.links_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if 0 <= index < len(lines):
            lines.pop(index)
            with open(self.links_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            self.load_links_to_table()