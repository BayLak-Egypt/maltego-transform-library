import sys
from PyQt6.QtWidgets import QApplication
from processor import MaltegoGUILoader, run_terminal_loader
my_tasks = ['Initializing Transform Engine...', 'Connecting to Maltego Graph Server...', 'Fetching WHOIS Data...', 'Finalizing Graph View...']
mode = 'gui'
if mode == 'gui':
    app = QApplication(sys.argv)
    loader = MaltegoGUILoader(tasks=my_tasks)
    loader.show()
    sys.exit(app.exec())
else:
    run_terminal_loader(tasks=my_tasks)