import tkinter as tk
from tkinter import ttk

class SettingsFrame(tk.Frame):
    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors["bg_dark"])
        self.COLORS = colors
        self.setup_ui()

    def setup_ui(self):
        # الحاوية الرئيسية مع هوامش
        main_container = tk.Frame(self, bg=self.COLORS["bg_dark"], padx=40, pady=40)
        main_container.pack(fill="both", expand=True)

        # العنوان
        tk.Label(main_container, text="[ SYSTEM CONFIGURATION ]", 
                 font=("Consolas", 16, "bold"), fg=self.COLORS["accent"], 
                 bg=self.COLORS["bg_dark"]).pack(anchor="w", pady=(0, 30))

        # --- قسم الإعدادات 1: API Keys ---
        self.create_section_label(main_container, "API KEYS & AUTHENTICATION")
        
        # حقل إدخال مثال (VirusTotal)
        self.vt_entry = self.create_labeled_entry(main_container, "VirusTotal API Key:", "Enter key here...")

        # --- قسم الإعدادات 2: تفضيلات النظام ---
        self.create_section_label(main_container, "SYSTEM PREFERENCES")
        
        self.auto_save = tk.BooleanVar(value=True)
        tk.Checkbutton(main_container, text="Auto-save logs on exit", 
                       variable=self.auto_save, bg=self.COLORS["bg_dark"], 
                       fg=self.COLORS["text_main"], selectcolor="black",
                       activebackground=self.COLORS["bg_dark"],
                       font=("Segoe UI", 10)).pack(anchor="w", pady=5)

        # --- أزرار التحكم ---
        btn_frame = tk.Frame(main_container, bg=self.COLORS["bg_dark"], pady=30)
        btn_frame.pack(fill="x")

        tk.Button(btn_frame, text="SAVE SETTINGS", command=self.save_logic,
                  bg=self.COLORS["accent"], fg="black", font=("Segoe UI", 10, "bold"),
                  bd=0, padx=25, pady=10, cursor="hand2").pack(side="left", padx=(0, 10))

    def create_section_label(self, parent, text):
        lbl = tk.Label(parent, text=text, font=("Segoe UI", 10, "bold"),
                       fg=self.COLORS["text_dim"], bg=self.COLORS["bg_dark"])
        lbl.pack(anchor="w", pady=(20, 10))
        # خط فاصل بسيط
        tk.Frame(parent, bg=self.COLORS["bg_card"], height=1).pack(fill="x", pady=(0, 15))

    def create_labeled_entry(self, parent, label_text, placeholder):
        tk.Label(parent, text=label_text, fg=self.COLORS["text_main"], 
                 bg=self.COLORS["bg_dark"], font=("Segoe UI", 9)).pack(anchor="w")
        ent = tk.Entry(parent, bg=self.COLORS["bg_card"], fg="white", 
                       insertbackground="white", bd=0, font=("Segoe UI", 11))
        ent.insert(0, placeholder)
        ent.pack(fill="x", ipady=8, pady=(5, 15))
        return ent

    def save_logic(self):
        # هنا تضع كود الحفظ (مثلاً في ملف JSON)
        print("[+] Settings Saved Successfully!")
