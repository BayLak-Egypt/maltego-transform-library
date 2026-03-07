import os
import zipfile
import shutil
import threading
import tkinter as tk
from tkinter import ttk
try:
    from lib.msg import show_msg
except ImportError:
    from tkinter import messagebox as msgbox

    def show_msg(parent, msg, type='info', title='Notification', **kwargs):
        if type == 'error':
            msgbox.showerror(title, msg, parent=parent)
        elif type == 'success':
            msgbox.showinfo('Success', msg, parent=parent)
        else:
            msgbox.showinfo(title, msg, parent=parent)

def create_box(parent):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    zip_path = os.path.join(project_root, 'TransformRepositories', 'BayLak-Egypt.MaltegoTransformsLibrary.zip')
    maltego_base = os.path.expanduser('~/.maltego')

    def get_missing_versions():
        if not os.path.exists(maltego_base) or not os.path.exists(zip_path):
            return []
        zip_folders = set()
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                for name in z.namelist():
                    first_part = name.split('/')[0]
                    if first_part and (not first_part.startswith('__')):
                        zip_folders.add(first_part)
        except:
            return []
        all_versions = [d for d in os.listdir(maltego_base) if d.startswith('v') and os.path.isdir(os.path.join(maltego_base, d))]
        missing = []
        for ver in all_versions:
            local_repo = os.path.join(maltego_base, ver, 'config/Maltego/TransformRepositories/Local')
            if not os.path.exists(local_repo) or any((not os.path.exists(os.path.join(local_repo, f)) for f in zip_folders)):
                missing.append(ver)
        return missing
    missing_versions = get_missing_versions()
    if not missing_versions:
        return tk.Frame(parent, height=0, bd=0, highlightthickness=0)
    box = tk.Frame(parent, bg='#2b2b2b', padx=12, pady=10)

    def start_install(selected_vars):
        targets = [v for v, var in selected_vars.items() if var.get()]
        if not targets:
            return
        for widget in box.winfo_children():
            widget.destroy()
        lbl_status = tk.Label(box, text='Installing...', fg='#3498db', bg='#2b2b2b', font=('Segoe UI', 8))
        lbl_status.pack(anchor='w')
        style = ttk.Style()
        style.configure('Small.Horizontal.TProgressbar', thickness=6)
        progress = ttk.Progressbar(box, orient='horizontal', mode='determinate', style='Small.Horizontal.TProgressbar')
        progress.pack(fill='x', pady=(5, 0))

        def process():
            try:
                temp_dir = os.path.join(project_root, 'temp_extract')
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                with zipfile.ZipFile(zip_path, 'r') as z:
                    z.extractall(temp_dir)
                total = len(targets)
                for i, ver in enumerate(targets):
                    dest = os.path.join(maltego_base, ver, 'config/Maltego/TransformRepositories/Local')
                    os.makedirs(dest, exist_ok=True)
                    for item in os.listdir(temp_dir):
                        s, d = (os.path.join(temp_dir, item), os.path.join(dest, item))
                        if os.path.isdir(s):
                            if os.path.exists(d):
                                shutil.rmtree(d)
                            shutil.copytree(s, d)
                        else:
                            shutil.copy2(s, d)
                    val = int((i + 1) / total * 100)
                    box.after(0, lambda v=val: progress.config(value=v))
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

                def finish():
                    show_msg(box.winfo_toplevel(), 'BayLak Transforms Installed successfully. Success', type='success')
                    box.destroy()
                box.after(100, finish)
            except Exception as e:
                box.after(0, lambda: show_msg(box.winfo_toplevel(), f'Error: {str(e)}', type='error'))
        threading.Thread(target=process, daemon=True).start()

    def show_version_selection():
        for widget in box.winfo_children():
            widget.destroy()
        tk.Label(box, text='New Transforms Found:', fg='#3498db', bg='#2b2b2b', font=('Segoe UI', 8, 'bold')).pack(anchor='w')
        selected_vars = {}
        for ver in missing_versions:
            var = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(box, text=f'Maltego {ver}', variable=var, bg='#2b2b2b', fg='#bbb', selectcolor='#1e1e1e', font=('Segoe UI', 8), activebackground='#2b2b2b', activeforeground='white')
            cb.pack(anchor='w', padx=5)
            selected_vars[ver] = var
        btn_frame = tk.Frame(box, bg='#2b2b2b')
        btn_frame.pack(fill='x', pady=(8, 0))
        tk.Button(btn_frame, text='Cancel', bg='#444444', fg='white', relief='flat', font=('Segoe UI', 7), command=setup_initial_ui).pack(side='left')
        tk.Button(btn_frame, text='Install Now', bg='#2ecc71', fg='white', relief='flat', font=('Segoe UI', 7, 'bold'), command=lambda: start_install(selected_vars)).pack(side='right')

    def setup_initial_ui():
        for widget in box.winfo_children():
            widget.destroy()
        tk.Label(box, text='Maltego Transforms Library', fg='white', bg='#2b2b2b', font=('Segoe UI', 9, 'bold')).pack(pady=(0, 5))
        tk.Button(box, text='Quick Install', bg='#3498db', fg='white', font=('Segoe UI', 8, 'bold'), relief='flat', width=18, command=show_version_selection).pack()
    setup_initial_ui()
    return box