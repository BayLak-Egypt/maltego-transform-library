import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
try:
    from library.googleweb import BaylakBrowserEngine
    from library.encrypt import encrypt_chunk
    from library.decrypt import decrypt_line
except ImportError:
    print('[-] Error: Make sure library/ folder contains googleweb.py, encrypt.py, and decrypt.py')
BASE_DIR = os.path.join(os.getcwd(), 'sessions')
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)
CHUNK_SIZE = 1024 * 512

class BaylakEmulator:

    def __init__(self, root):
        self.root = root
        self.root.title('Baylak Sessions Manager - Pro Edition')
        self.root.geometry('1100x650')
        self.root.configure(bg='#2c3e50')
        self.current_session_path = None
        self.web_engine = BaylakBrowserEngine()
        self.init_ui()
        self.create_context_menu()
        self.refresh_session_list()

    def init_ui(self):
        self.sidebar = tk.Frame(self.root, width=220, bg='#34495e', padx=10, pady=10)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        tk.Label(self.sidebar, text='BAYLAK SYSTEM', fg='#1abc9c', bg='#34495e', font=('Arial', 14, 'bold')).pack(pady=15)
        tk.Button(self.sidebar, text='🌐 View All Files', command=self.view_all_combined, bg='#2980b9', fg='white', bd=0, pady=8, font=('Arial', 9, 'bold'), cursor='hand2').pack(fill=tk.X, pady=5)
        tk.Label(self.sidebar, text='STORAGE VAULTS', fg='#bdc3c7', bg='#34495e', font=('Arial', 8)).pack(anchor=tk.W, pady=(15, 0))
        self.session_listbox = tk.Listbox(self.sidebar, bg='#2c3e50', fg='#ecf0f1', bd=0, highlightthickness=0, font=('Arial', 10), selectbackground='#1abc9c')
        self.session_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.session_listbox.bind('<<ListboxSelect>>', self.on_session_select)
        tk.Button(self.sidebar, text='+ New Vault', command=self.create_vault, bg='#27ae60', fg='white', bd=0, font=('Arial', 9, 'bold'), pady=6).pack(fill=tk.X, pady=5)
        self.main_area = tk.Frame(self.root, bg='#ecf0f1')
        self.main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.toolbar = tk.Frame(self.main_area, bg='#bdc3c7', pady=8, padx=15)
        self.toolbar.pack(fill=tk.X)
        self.btn_add_file = tk.Button(self.toolbar, text='➕ Add Local File', command=self.add_files, state=tk.DISABLED, bg='#34495e', fg='white', bd=0, padx=12, pady=4)
        self.btn_add_file.pack(side=tk.LEFT, padx=2)
        self.btn_add_google = tk.Button(self.toolbar, text='🔑 Add Google Account', command=self.add_google_account_ui, state=tk.DISABLED, bg='#ea4335', fg='white', bd=0, padx=12, pady=4)
        self.btn_add_google.pack(side=tk.LEFT, padx=5)
        self.vault_label = tk.Label(self.toolbar, text='Select a vault', bg='#bdc3c7', font=('Arial', 10, 'bold'))
        self.vault_label.pack(side=tk.RIGHT)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', background='white', fieldbackground='white', rowheight=25, font=('Arial', 10))
        cols = ('Email/Name', 'Size', 'Vault Source')
        self.tree = ttk.Treeview(self.main_area, columns=cols, show='headings')
        for col in cols:
            self.tree.heading(col, text=col)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        self.tree.bind('<Button-3>', self.show_popup)
        self.tree.tag_configure('none', foreground='#95a5a6')
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.main_area, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=20, pady=5)
        self.status_label = tk.Label(self.main_area, text='Ready', bg='#ecf0f1', fg='#7f8c8d', anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=5)

    def add_google_account_ui(self):
        v_name = os.path.basename(self.current_session_path)
        self.status_label.config(text='Browser active... Please login.')
        self.root.update()
        success = self.web_engine.capture_new_session(v_name, 'Detect_Email')
        if success:
            messagebox.showinfo('Success', 'Account session captured successfully!')
            self.load_data()
        self.status_label.config(text='Ready')

    def create_context_menu(self):
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label='🚀 Run Account (Google)', command=self.run_google_account_ui)
        self.menu.add_separator()
        self.menu.add_command(label='📦 Unpack Accounts', command=self.unpack_action)
        self.menu.add_command(label='🗑 Delete', command=self.delete_action, foreground='red')

    def show_popup(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            val = str(self.tree.item(item)['values'][0])
            if ',' in val:
                self.menu.entryconfig(2, state='normal')
            else:
                self.menu.entryconfig(2, state='disabled')
            if 'None' in val:
                self.menu.entryconfig(3, label='🗑 Delete (Useless File)')
            else:
                self.menu.entryconfig(3, label='🗑 Delete')
            self.menu.post(event.x_root, event.y_root)

    def load_data(self, path=None, label=None):
        if not path:
            self.tree.delete(*self.tree.get_children())
            path = self.current_session_path
            label = os.path.basename(path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                header = f.readline()
                if header.startswith('INDEX:'):
                    idx = json.loads(header.replace('INDEX:', ''))
                    for item in idx:
                        name = item['name']
                        tag = 'none' if 'Detect_Email' in name or '@' not in name else ''
                        display_name = name if '@' in name else 'None (Useless Session)'
                        self.tree.insert('', tk.END, values=(display_name, f'{item['size'] // 1024} KB', label), tags=(tag,))
        except:
            pass

    def unpack_action(self):
        messagebox.showinfo('Unpack', 'Feature: Splitting multi-account session...')

    def refresh_session_list(self):
        self.session_listbox.delete(0, tk.END)
        for f in os.listdir(BASE_DIR):
            if f.endswith('.sessions'):
                self.session_listbox.insert(tk.END, f)

    def on_session_select(self, event):
        selection = self.session_listbox.curselection()
        if selection:
            filename = self.session_listbox.get(selection[0])
            self.current_session_path = os.path.join(BASE_DIR, filename)
            self.vault_label.config(text=f'📂 Vault: {filename}')
            self.btn_add_file.config(state=tk.NORMAL)
            self.btn_add_google.config(state=tk.NORMAL)
            self.load_data()

    def create_vault(self):
        name = simpledialog.askstring('New', 'Vault Name:')
        if name:
            if not name.endswith('.sessions'):
                name += '.sessions'
            with open(os.path.join(BASE_DIR, name), 'w', encoding='utf-8') as f:
                f.write('INDEX:[]\n')
            self.refresh_session_list()

    def add_files(self):
        fpaths = filedialog.askopenfilenames()
        if not fpaths:
            return
        with open(self.current_session_path, 'r', encoding='utf-8') as f:
            idx = json.loads(f.readline().replace('INDEX:', ''))
        for p in fpaths:
            n = os.path.basename(p)
            s = os.path.getsize(p)
            with open(self.current_session_path, 'a', encoding='utf-8') as arc:
                arc.write(f'\nBLOCK_START:{n}\n')
                with open(p, 'rb') as f:
                    while (chunk := f.read(CHUNK_SIZE)):
                        arc.write(f'D:{encrypt_chunk(chunk)}\n')
                arc.write(f'BLOCK_END:{n}\n')
                idx.append({'name': n, 'size': s})
        with open(self.current_session_path, 'r', encoding='utf-8') as f:
            body = f.readlines()[1:]
        with open(self.current_session_path, 'w', encoding='utf-8') as f:
            f.write('INDEX:' + json.dumps(idx) + '\n')
            f.writelines(body)
        self.load_data()

    def view_all_combined(self):
        self.tree.delete(*self.tree.get_children())
        for f in os.listdir(BASE_DIR):
            if f.endswith('.sessions'):
                self.load_data(os.path.join(BASE_DIR, f), f)

    def run_google_account_ui(self):
        sel = self.tree.selection()
        if not sel:
            return
        acc_name, _, v_name = self.tree.item(sel[0])['values']
        self.status_label.config(text=f'Launching {acc_name}...')
        self.root.update()
        driver, t_path = self.web_engine.run_decrypted_session(v_name, acc_name)
        if driver:
            messagebox.showinfo('Browser Running', f'Close browser or click OK to wipe session data.')
            self.web_engine.cleanup(driver, t_path)
            self.status_label.config(text='Session Wiped.')
        else:
            messagebox.showerror('Error', 'Could not start session.')

    def delete_action(self):
        sel = self.tree.selection()
        if not sel:
            return
        fn, _, vn = self.tree.item(sel[0])['values']
        v_path = os.path.join(BASE_DIR, vn)
        if messagebox.askyesno('Confirm', f'Delete {fn}?'):
            with open(v_path, 'r', encoding='utf-8') as f:
                idx = json.loads(f.readline().replace('INDEX:', ''))
                new_idx = [i for i in idx if i['name'] != fn]
            temp = v_path + '.tmp'
            with open(v_path, 'r', encoding='utf-8') as old, open(temp, 'w', encoding='utf-8') as new:
                new.write('INDEX:' + json.dumps(new_idx) + '\n')
                skip = False
                next(old)
                for line in old:
                    if line.startswith(f'BLOCK_START:{fn}'):
                        skip = True
                    if not skip:
                        new.write(line)
                    if line.startswith(f'BLOCK_END:{fn}'):
                        skip = False
            os.replace(temp, v_path)
            self.load_data()
if __name__ == '__main__':
    root = tk.Tk()
    app = BaylakEmulator(root)
    root.mainloop()