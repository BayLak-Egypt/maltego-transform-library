import os
import sys
import json
import shutil
from lib.upgrade import get_remote_files, sync_file
from loading_terminal import run_terminal_loader
from loading_gui import start_gui_loader

def start_loader(tasks, mode='gui'):
    auto_update = False
    if os.path.exists('settings.json'):
        try:
            with open('settings.json', 'r') as f:
                auto_update = json.load(f).get('auto_update', False)
        except:
            pass
    if not auto_update:
        return start_gui_loader(tasks) if mode == 'gui' else run_terminal_loader(tasks)
    remote_files = get_remote_files()
    updated_files_names = []
    if remote_files:
        for item in remote_files:
            if sync_file(item):
                file_name = os.path.basename(item['path'])
                updated_files_names.append(f'Updated: {file_name}')
    if updated_files_names:
        final_tasks = updated_files_names + ['Finalizing...', 'Restarting...']
        if mode == 'gui':
            start_gui_loader(final_tasks)
        else:
            run_terminal_loader(final_tasks)
        if os.path.exists('__pycache__'):
            shutil.rmtree('__pycache__', ignore_errors=True)
        print('\n[!] Restarting to apply updates...')
        os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        final_tasks = ['System: Up to date'] + tasks
        if mode == 'gui':
            start_gui_loader(final_tasks)
        else:
            run_terminal_loader(final_tasks)