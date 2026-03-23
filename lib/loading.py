import os
import sys
import json
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
        if mode == 'gui':
            start_gui_loader(tasks)
        else:
            run_terminal_loader(tasks)
        return
    remote_files = get_remote_files()
    updated_files = []
    for item in remote_files:
        if sync_file(item):
            updated_files.append(os.path.basename(item['path']))
    if updated_files:
        final_tasks = [f'Updating: {f}' for f in updated_files] + ['Finalizing & Restarting...']
        if mode == 'gui':
            start_gui_loader(final_tasks)
        else:
            run_terminal_loader(final_tasks)
        print('\n [!] Update found. Restarting process...')
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        final_tasks = ['System: Up to date'] + tasks
        if mode == 'gui':
            start_gui_loader(final_tasks)
        else:
            run_terminal_loader(final_tasks)