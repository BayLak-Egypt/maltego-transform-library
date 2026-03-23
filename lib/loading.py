import os
from lib.upgrade import get_remote_files, sync_file
from loading_terminal import run_terminal_loader
from loading_gui import start_gui_loader

def start_loader(tasks, mode='gui'):
    remote_files = get_remote_files()
    updated_files_tasks = []
    for item in remote_files:
        if sync_file(item):
            filename = os.path.basename(item['path'])
            updated_files_tasks.append(f'Updated: {filename}')
    if not updated_files_tasks:
        final_tasks = ['System: Already up to date'] + tasks
    else:
        final_tasks = updated_files_tasks + tasks
    if mode == 'gui':
        start_gui_loader(final_tasks)
    else:
        run_terminal_loader(final_tasks)