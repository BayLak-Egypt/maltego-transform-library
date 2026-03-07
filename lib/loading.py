from loading_terminal import run_terminal_loader
from loading_gui import start_gui_loader

def start_loader(tasks, mode='gui'):
    if mode == 'gui':
        start_gui_loader(tasks)
    else:
        run_terminal_loader(tasks)
if __name__ == '__main__':
    my_tasks = ['Database', 'Modules', 'API Keys', 'Finalizing']
    start_loader(my_tasks, mode='gui')