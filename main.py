import sys
import os
import logging
import warnings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
warnings.filterwarnings('ignore', module='bs4')
try:
    from maltego_trx.maltego import MaltegoTransform
    from lib.utils import detect_input_type
    from lib.loader import load_compatible_libraries
    from lib.processor import process_result_item
    from lib.menu import LibraryMenu
    from lib.loading import start_loader
except ImportError as e:
    print(f'Error: Missing dependencies. {e}')
    sys.exit(1)
logging.basicConfig(filename='transform.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIBRARY_FOLDER = os.path.join(BASE_DIR, 'library')

def run_transform():
    input_value = sys.argv[1] if len(sys.argv) > 1 else None
    response = MaltegoTransform()
    if input_value:
        input_type = detect_input_type(input_value)
        loading_msg = f'Scanning for {input_type} tools...'
    else:
        input_type = 'All'
        loading_msg = 'Opening Library Manager...'
    start_loader(['Initializing System', loading_msg])
    compatible_libs = load_compatible_libraries(LIBRARY_FOLDER, input_type)
    ui = LibraryMenu(compatible_libs, input_type=input_type)
    selected_names = ui.show()
    if not input_value:
        return
    if not selected_names:
        print(response.returnOutput())
        return
    for lib_data in compatible_libs:
        if lib_data['folder_name'] in selected_names:
            try:
                module = lib_data['module']
                func = next((getattr(module, a) for a in dir(module) if callable(getattr(module, a)) and (not a.startswith('__'))), None)
                if func:
                    result = func(input_value)
                    if not result:
                        continue
                    results_list = result if isinstance(result, list) else [result]
                    for item in results_list:
                        process_result_item(response, item, lib_data, input_value, input_type)
            except Exception as e:
                logging.error(f'Execution Error in [{lib_data['folder_name']}]: {e}')
    print(response.returnOutput())
if __name__ == '__main__':
    try:
        run_transform()
    except Exception as e:
        logging.critical(f'Critical System Failure: {e}')