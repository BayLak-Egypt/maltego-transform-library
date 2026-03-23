import os
from lib.upgrade import get_remote_files, sync_file
from loading_terminal import run_terminal_loader
from loading_gui import start_gui_loader

def start_loader(tasks, mode='gui'):
    remote_files = get_remote_files()
    sync_tasks_names = [f'Update: {os.path.basename(f['path'])}' for f in remote_files]
    final_tasks = sync_tasks_names + tasks
    for item in remote_files:
        sync_file(item)
    if mode == 'gui':
        start_gui_loader(final_tasks)
    else:
        run_terminal_loader(final_tasks)