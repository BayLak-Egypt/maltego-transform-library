import tkinter as tk
from PIL import Image, ImageTk
import os
# استيراد الألوان
from lib.styles.styles import COLORS 

class SearchHeader(tk.Frame):
    def __init__(self, parent, colors, on_search_callback):
        # نستخدم COLORS المستوردة كقيمة افتراضية لو متبعتش colors
        self.COLORS = colors if colors else COLORS
        
        super().__init__(parent, bg=self.COLORS.get("bg_dark", "#1e1e1e"))
        self.on_search = on_search_callback
        self._after_id = None 

        # مسار الأيقونة
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "icons", "search.png")

        # --- التصميم الأيسر ---
        self.title_frame = tk.Frame(self, bg=self.COLORS.get("bg_dark", "#1e1e1e"))
        self.title_frame.pack(side="left", fill="y", padx=10)
        
        tk.Label(self.title_frame, text="Github Service", font=("Segoe UI Semibold", 9), 
                 fg=self.COLORS.get("fg_sub", "#888888"), # استخدام لون النص الفرعي
                 bg=self.COLORS.get("bg_dark", "#1e1e1e")).pack(anchor="w")
        
        tk.Label(self.title_frame, text="LIBRARY MANAGER", font=("Segoe UI Bold", 14), 
                 fg=self.COLORS.get("fg_main", "#e0e0e0"), # استخدام لون النص الرئيسي
                 bg=self.COLORS.get("bg_dark", "#1e1e1e")).pack(anchor="w")

        # --- حاوية البحث ---
        # استخدام لون الخلفية الفاتحة قليلاً للحاوية
        self.search_container = tk.Frame(
            self, 
            bg=self.COLORS.get("bg_light", "#2b2b2b"), 
            highlightbackground=self.COLORS.get("border", "#3c3f41"), 
            highlightthickness=1
        )
        self.search_container.pack(side="right", fill="x", expand=True, padx=(40, 10), pady=10)

        # الأيقونة
        try:
            search_img = Image.open(icon_path).resize((22, 22), Image.Resampling.LANCZOS)
            self.search_icon_photo = ImageTk.PhotoImage(search_img)
            tk.Label(self.search_container, image=self.search_icon_photo, 
                     bg=self.COLORS.get("bg_light", "#2b2b2b")).pack(side="left", padx=10)
        except:
            tk.Label(self.search_container, text="🔍", 
                     fg=self.COLORS.get("fg_sub", "#888888"), 
                     bg=self.COLORS.get("bg_light", "#2b2b2b")).pack(side="left", padx=10)

        # حقل الإدخال
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._handle_typing)
        
        self.entry = tk.Entry(
            self.search_container, textvariable=self.search_var,
            bg=self.COLORS.get("bg_light", "#2b2b2b"), 
            fg=self.COLORS.get("fg_main", "#bbbbbb"), 
            insertbackground=self.COLORS.get("accent", "#ef6c00"), # لون المؤشر (البرتقالي مثلاً)
            bd=0, font=("Segoe UI", 11), highlightthickness=0
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8)

        # عرض العناصر لأول مرة
        self.after(100, lambda: self.on_search(""))

    def _handle_typing(self, *args):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(300, self._execute_search)

    def _execute_search(self):
        query = self.search_var.get().strip()
        self.on_search(query)

    def get_query(self):
        return self.search_var.get().lower()
