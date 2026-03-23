import os
import sys
from lib.upgrade import get_remote_files, sync_file
from loading_terminal import run_terminal_loader
from loading_gui import start_gui_loader

def start_loader(tasks, mode='gui'):
    remote_files = get_remote_files()
    updated_files = []
    for item in remote_files:
        if sync_file(item):
            updated_files.append(os.path.basename(item['path']))
    if updated_files:
        final_tasks = [f'Critical Update: {f}' for f in updated_files] + ['Restarting System...']
        if mode == 'gui':
            start_gui_loader(final_tasks)
        else:
            run_terminal_loader(final_tasks)
        print('\n [!] System updated. Restarting process...')
        os.execv(sys.executable, ['python'] + sys.argv)
    else:
        final_tasks = ['System: Up to date'] + tasks
        if mode == 'gui':
            start_gui_loader(final_tasks)
        else:
            run_terminal_loader(final_tasks)
