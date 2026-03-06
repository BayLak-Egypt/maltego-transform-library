import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil

# استيراد المكونات الخارجية
from lib.searchiconlibrary import IconManager 
from lib.styles.styles import COLORS
from lib.styles.btnstyle import ActionButton 

# استيراد الهيدر الجديد (العنوان + البحث) من الملف الذي أنشأناه
from lib.styles.search import SearchHeader 

class LibraryInfoFrame(tk.Frame):
    def __init__(self, parent, lib_dir, filtered_libs):
        self.COLORS = COLORS
        # التأكد من وجود لون التنبيه للحذف
        if "danger" not in self.COLORS:
            self.COLORS["danger"] = "#ff4444"
        
        super().__init__(parent, bg=self.COLORS["bg_dark"])
        self.lib_dir = lib_dir
        self.filtered_libs = filtered_libs
        
        # تهيئة مدير الأيقونات والكاش
        self.icon_manager = IconManager(self.lib_dir)
        self.icon_cache = {}  
        
        self.create_widgets()

    def create_widgets(self):
        # --- 1. الهيدر (العنوان وشريط البحث) ---
        # تم نقل كل تفاصيل التصميم الخاصة بالعنوان والبحث إلى ملف search.py
        self.header = SearchHeader(
            self, 
            self.COLORS, 
            on_search_callback=lambda q: self.refresh_data()
        )
        self.header.pack(fill="x", padx=40, pady=(30, 20))

        # --- 2. منطقة المحتوى القابلة للتمرير ---
        container = tk.Frame(self, bg=self.COLORS["bg_dark"])
        container.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        self.canvas = tk.Canvas(container, bg=self.COLORS["bg_dark"], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.COLORS["bg_dark"])

        # ربط التمرير
        self.scrollable_frame.bind(
            "<Configure>", 
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        # جعل عرض الفريم يتبع عرض الكانفاس تلقائياً
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # تفعيل سكرول الماوس
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # تحميل البيانات لأول مرة
        self.refresh_data()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def refresh_data(self):
        """تحديث القائمة بناءً على نص البحث"""
        # مسح العناصر الحالية
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # جلب نص البحث من الهيدر
        query = self.header.get_query()
        
        if not os.path.exists(self.lib_dir): 
            return

        ready_names = [l['folder_name'] for l in self.filtered_libs]

        # قراءة المجلدات وترتيبها
        for d in sorted(os.listdir(self.lib_dir)):
            path = os.path.join(self.lib_dir, d)
            if os.path.isdir(path):
                # فلترة البحث
                if query and query not in d.lower():
                    continue

                is_ready = d in ready_names
                self.create_item_card(d, is_ready)

    def create_item_card(self, name, is_ready):
        """إنشاء كارد لكل مكتبة بتصميم عصري"""
        status_text = "● SYSTEM READY" if is_ready else "○ LOADED / INACTIVE"
        status_color = self.COLORS["accent"] if is_ready else self.COLORS["text_dim"]

        # إطار الكارد الرئيسي
        card = tk.Frame(self.scrollable_frame, bg=self.COLORS["bg_card"], pady=12, padx=15)
        card.pack(fill="x", pady=5, padx=2)
        
        # خط تمييز جانبي ملون
        tk.Frame(card, bg=self.COLORS["accent"], width=4).pack(side="left", fill="y")

        # عرض الأيقونة
        icon_img = self.icon_manager.get_lib_icon(name, size=(40, 40))
        if icon_img:
            self.icon_cache[name] = icon_img
            tk.Label(card, image=icon_img, bg=self.COLORS["bg_card"]).pack(side="left", padx=15)
        else:
            tk.Label(card, text="📁", font=("Segoe UI", 20), 
                     fg=self.COLORS["text_dim"], bg=self.COLORS["bg_card"]).pack(side="left", padx=15)

        # معلومات المكتبة (الاسم والحالة)
        info_frame = tk.Frame(card, bg=self.COLORS["bg_card"])
        info_frame.pack(side="left", fill="both", expand=True)

        tk.Label(info_frame, text=name.upper(), font=("Consolas", 11, "bold"), 
                 fg=self.COLORS["text_main"], bg=self.COLORS["bg_card"], anchor="w").pack(fill="x")
        
        tk.Label(info_frame, text=status_text, font=("Segoe UI", 8, "bold"), 
                 fg=status_color, bg=self.COLORS["bg_card"], anchor="w").pack(fill="x")

        # أزرار التحكم
        actions_frame = tk.Frame(card, bg=self.COLORS["bg_card"])
        actions_frame.pack(side="right")

        btn_del = ActionButton(
            actions_frame, 
            text="UNINSTALL", 
            colors=self.COLORS,
            command=lambda n=name: self.uninstall_lib(n)
        )
        btn_del.pack(side="right", padx=10)

    def uninstall_lib(self, folder_name):
        """حذف المجلد نهائياً"""
        confirm = messagebox.askyesno("Uninstall", f"Delete '{folder_name}' permanently?")
        if confirm:
            try:
                path = os.path.join(self.lib_dir, folder_name)
                shutil.rmtree(path)
                self.refresh_data()
                messagebox.showinfo("Success", "Deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete: {e}")
