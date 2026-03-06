import tkinter as tk

class ActionButton(tk.Button):
    """كلاس لإنشاء أزرار احترافية مع دعم الـ Hover وتخصيص كامل للمظهر"""
    def __init__(self, master, text, command, colors, btn_type="primary", **kwargs):
        self.colors = colors
        self.btn_type = btn_type
        
        # جلب الألوان من القاموس بناءً على النوع، مع قيم افتراضية (Fallback)
        # إذا لم يتم تمرير لون للنوع، سيستخدم الرمادي
        self.accent_color = colors.get(btn_type, "#808080")
        self.bg_color = colors.get("sidebar", "#2b2b2b")
        
        # إعدادات الـ Hover
        self.hover_bg = self.accent_color
        self.hover_fg = "white"

        super().__init__(
            master,
            text=text,
            command=command,
            font=("Segoe UI", 9, "bold"),
            bg=self.bg_color,
            fg=self.accent_color, # النص يأخذ لون النوع (أحمر للـ danger، أخضر للـ success..)
            activebackground=self.hover_bg,
            activeforeground=self.hover_fg,
            bd=0,
            padx=20,
            pady=8,
            cursor="hand2",
            relief="flat",
            **kwargs
        )

        # ربط أحداث الماوس
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        self.configure(bg=self.hover_bg, fg=self.hover_fg)

    def _on_leave(self, event):
        self.configure(bg=self.bg_color, fg=self.accent_color)

# --- مثال على التشغيل الفعلي ---
if __name__ == "__main__":
    app = tk.Tk()
    app.geometry("400x300")
    app.configure(bg="#1e1e1e") # خلفية داكنة احترافية

    # قاموس الألوان الموحد لتطبيقك
    theme_colors = {
        "sidebar": "#252526",
        "danger": "#f44336",
        "success": "#4caf50",
        "primary": "#007acc",
        "warning": "#ff9800"
    }

    # إنشاء أزرار بأنواع مختلفة بسهولة
    btn1 = ActionButton(app, "حذف السجل", lambda: print("Delete"), theme_colors, "danger")
    btn1.pack(pady=10)

    btn2 = ActionButton(app, "حفظ التغييرات", lambda: print("Save"), theme_colors, "success")
    btn2.pack(pady=10)

    btn3 = ActionButton(app, "إضافة جديد", lambda: print("Add"), theme_colors, "primary")
    btn3.pack(pady=10)

    app.mainloop()
