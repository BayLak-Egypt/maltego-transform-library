import os
from PIL import Image, ImageTk, ImageDraw, ImageStat

class IconManager:
    def __init__(self, lib_dir):
        self.lib_dir = lib_dir
        self.supported_formats = ('.png', '.jpg', '.jpeg', '.ico')
        self._cache = {}

    def _get_contrast_color(self, img, bg_color):
        """
        تحسب متوسط لون الصورة وتتحقق من التباين مع لون الجراب.
        إذا كان اللونان متقاربين، تعكس لون الجراب.
        """
        # حساب متوسط اللون (RGB) للأيقونة
        stat = ImageStat.Stat(img)
        avg_rgb = stat.median[:3] # نستخدم الوسيط (median) لدقة أعلى مع الأيقونات
        
        # حساب المسافة اللونية بين الأيقونة والجراب
        # bg_color هو (R, G, B, A)
        dist = sum((a - b) ** 2 for a, b in zip(avg_rgb, bg_color[:3])) ** 0.5
        
        # إذا كانت المسافة أقل من 60 (الألوان متقاربة جداً)
        if dist < 60:
            # عكس اللون: طرح القيمة من 255 (الأبيض يصبح أسود والعكس)
            new_rgb = tuple(255 - c for c in bg_color[:3])
            return new_rgb + (bg_color[3],) # إعادة القناة الشفافة كما هي
        
        return bg_color

    def get_lib_icon(self, folder_name, size=(35, 35), border_width=2, border_color=(100, 100, 100, 255), corner_radius=10):
        """
        الحصول على أيقونة بجراب مستدير مع ضمان عدم خروج الصورة عن الحواف
        وعكس اللون تلقائياً عند تشابهه مع الأيقونة.
        """
        cache_key = (folder_name, size, border_width, border_color, corner_radius)
        if cache_key in self._cache:
            return self._cache[cache_key]

        path = os.path.join(self.lib_dir, folder_name)
        
        try:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.lower().endswith(self.supported_formats):
                        img_path = os.path.join(path, file)
                        
                        with Image.open(img_path) as img:
                            # 1. تحويل الصورة وتغيير حجمها
                            img = img.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
                            
                            # 2. تحديد لون الجراب بناءً على التباين مع الصورة
                            final_border_color = self._get_contrast_color(img, border_color)
                            
                            # 3. قص الصورة الأصلية لتكون مستديرة الزوايا (Masking)
                            # هذا الجزء يضمن أن الصورة "لا تخرج" عن الجراب
                            img_mask = Image.new("L", size, 0)
                            draw_img_mask = ImageDraw.Draw(img_mask)
                            draw_img_mask.rounded_rectangle([0, 0, size[0], size[1]], radius=corner_radius, fill=255)
                            
                            rounded_img = Image.new("RGBA", size, (0, 0, 0, 0))
                            rounded_img.paste(img, (0, 0), mask=img_mask)

                            # 4. بناء الجراب (الإطار)
                            if border_width > 0:
                                full_size = (size[0] + 2 * border_width, size[1] + 2 * border_width)
                                
                                # إنشاء القناع الخارجي للجراب
                                border_mask = Image.new("L", full_size, 0)
                                draw_border = ImageDraw.Draw(border_mask)
                                # radius+border_width لضمان التناسق في الانحناء
                                draw_border.rounded_rectangle([0, 0, full_size[0], full_size[1]], 
                                                              radius=corner_radius + border_width, fill=255)
                                
                                # إنشاء صورة الجراب باللون النهائي
                                cased_img = Image.new("RGBA", full_size, final_border_color)
                                cased_img.putalpha(border_mask)

                                # 5. لصق الصورة المقصوصة في منتصف الجراب
                                cased_img.paste(rounded_img, (border_width, border_width), rounded_img)
                                img = cased_img
                            else:
                                img = rounded_img

                            # تحويل لـ PhotoImage للـ GUI
                            icon = ImageTk.PhotoImage(img)
                            self._cache[cache_key] = icon
                            return icon
                            
        except Exception as e:
            print(f"Error processing icon for {folder_name}: {e}")
            
        return None

# --- مثال سريع للاستخدام ---
# manager = IconManager("path_to_icons")
# my_icon = manager.get_lib_icon("folder_name", border_color=(30, 30, 30, 255))
