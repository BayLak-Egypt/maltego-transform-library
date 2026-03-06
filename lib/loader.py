import os
import importlib.util
import logging

def load_compatible_libraries(library_folder, input_type):
    compatible_libs = []
    if not os.path.exists(library_folder):
        return compatible_libs

    for lib_name in os.listdir(library_folder):
        lib_path = os.path.join(library_folder, lib_name)
        if not os.path.isdir(lib_path): continue
        
        py_files = [f for f in os.listdir(lib_path) if f.endswith(".py") and f != "__init__.py"]
        if not py_files: continue
        
        try:
            # تحميل الملف برمجياً
            spec = importlib.util.spec_from_file_location(lib_name, os.path.join(lib_path, py_files[0]))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # فحص التوافق بناءً على متغير EntityType داخل ملف المكتبة
            if getattr(module, "EntityType", "Phrase") in [input_type, "All"]:
                compatible_libs.append({
                    "folder_name": lib_name, 
                    "display_name": getattr(module, "Name", lib_name), 
                    "module": module
                })
        except Exception as e:
            logging.error(f"Error loading {lib_name}: {e}")
            
    return compatible_libs
