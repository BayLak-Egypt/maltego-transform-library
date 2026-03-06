#!/usr/bin/env python3
import sys
import os
import logging
import warnings

# إضافة المسار الحالي للمشروع
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

warnings.filterwarnings("ignore", module='bs4')

try:
    from maltego_trx.maltego import MaltegoTransform
    from lib.utils import detect_input_type
    from lib.loader import load_compatible_libraries
    from lib.processor import process_result_item
    from lib.menu import LibraryMenu
    from lib.loading import start_loader
except ImportError as e:
    print(f"Error: Missing dependencies. {e}")
    sys.exit(1)

logging.basicConfig(
    filename="transform.log", 
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LIBRARY_FOLDER = os.path.join(BASE_DIR, "library")

def run_transform():
    # 1. التحقق من وجود مدخلات (من ملتيجو أو تشغيل يدوي)
    input_value = sys.argv[1] if len(sys.argv) > 1 else None
    response = MaltegoTransform()

    # 2. تحديد نوع الإدخال
    # إذا كان التشغيل يدوياً (input_value is None)، نرسل نوعاً خاصاً للمنيو واللودر
    if input_value:
        input_type = detect_input_type(input_value)
        loading_msg = f"Scanning for {input_type} tools..."
    else:
        input_type = "All"  # أو "None" حسب ما يفضله الـ loader عندك
        loading_msg = "Opening Library Manager..."

    # --- المرحلة الأولى: التحميل (Loading Screen) ---
    start_loader(["Initializing System", loading_msg])
    
    # تحميل المكتبات المتوافقة
    # ملاحظة: تأكد أن load_compatible_libraries ترجع كل المكتبات إذا كان النوع "All"
    compatible_libs = load_compatible_libraries(LIBRARY_FOLDER, input_type)

    # 3. تشغيل الواجهة الرسومية (Menu)
    # المنيو الآن ستستقبل input_type وتعرف هل تفتح صفحة Library Info أم Transforms
    ui = LibraryMenu(compatible_libs, input_type=input_type)
    selected_names = ui.show()

    # 4. منطق ما بعد إغلاق المنيو
    
    # حالة التشغيل اليدوي (بدون مدخلات)
    if not input_value:
        # البرنامج ينتهي هنا بهدوء بعد إغلاق نافذة المعلومات
        return

    # حالة التشغيل من ملتيجو ولكن المستخدم لم يختار شيئاً أو أغلق النافذة
    if not selected_names:
        print(response.returnOutput())
        return

    # 5. تنفيذ المهام المختارة (فقط في حالة وجود input_value)
    for lib_data in compatible_libs:
        if lib_data['folder_name'] in selected_names:
            try:
                module = lib_data['module']
                # البحث عن الدالة الأساسية في المكتبة
                func = next((getattr(module, a) for a in dir(module) 
                             if callable(getattr(module, a)) and not a.startswith("__")), None)
                
                if func:
                    result = func(input_value)
                    if not result: continue
                    
                    results_list = result if isinstance(result, list) else [result]
                    for item in results_list:
                        process_result_item(response, item, lib_data, input_value, input_type)
                
            except Exception as e:
                logging.error(f"Execution Error in [{lib_data['folder_name']}]: {e}")

    # 6. إرسال النتائج النهائية لملتيجو
    print(response.returnOutput())

if __name__ == "__main__":
    try:
        run_transform()
    except Exception as e:
        logging.critical(f"Critical System Failure: {e}")
