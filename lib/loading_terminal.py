import sys
import time

def run_terminal_loader(tasks):
    print('\n' + '=' * 50)
    print(' [!] BAYLAK OSINT SYSTEM - INITIALIZING ')
    print('=' * 50 + '\n')
    total = len(tasks)
    if total == 0:
        print('[!] No tasks to load.')
        return
    for i, task in enumerate(tasks):
        percent = int((i + 1) / total * 100)
        bar_length = 30
        filled_length = int(bar_length * (i + 1) // total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f'\r    Progress: |{bar}| {percent}% Processing: {task}')
        sys.stdout.flush()
        time.sleep(0.15)
    print(f'\n\n[+] Setup Complete. Launching Maltego Transform...\n')