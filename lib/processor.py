import os
from .utils import get_maltego_type

def process_result_item(response, item, lib_data, input_value, input_type):
    """تحويل نتائج المكتبات إلى كيانات Maltego"""
    res_val = str(item.get("value", input_value))
    
    # تمييز النتيجة لو كانت نفس قيمة المدخل
    final_value = f"{res_val} ({lib_data['display_name']})" if res_val == input_value else res_val
    
    # تحديد النوع
    lib_type = item.get("type")
    if lib_type:
        final_type = f"maltego.{lib_type}" if not lib_type.startswith("maltego.") else lib_type
    else:
        final_type = get_maltego_type(input_type)

    ent = response.addEntity(final_type, final_value)
    
    # إدارة الأيقونات
    icon = item.get("icon")
    if icon:
        if os.path.exists(icon):
            ent.setIconURL(f"file:///{os.path.abspath(icon).replace('\\', '/')}")
        else:
            ent.setIconURL(icon)

    if "notes" in item: ent.setNote(item["notes"])
    if "properties" in item:
        for k, v in item["properties"].items(): 
            ent.addProperty(k, k, "loose", str(v))
    
    ent.addProperty("source", "Source Library", "loose", lib_data['display_name'])
