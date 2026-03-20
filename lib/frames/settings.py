import tkinter as tk
from tkinter import ttk
import os
import importlib.util

class SettingsFrame(tk.Frame):

    def __init__(self, parent, colors):
        super().__init__(parent, bg=colors['bg_dark'])
        self.COLORS = colors
        self.FRAME_BG = '#1e1e1e'
        self.FRAME_BORDER = '#444444'
        self.ACCENT_COLOR = colors.get('accent', '#00f3ff')
        self.RADIUS = 15
        self.OFFSET = 4
        self.canvas = tk.Canvas(self, bg=self.COLORS['bg_dark'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.COLORS['bg_dark'])
        self.scrollable_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        self.scrollbar.pack(side='right', fill='y')
        self.bind_mouse_wheel(self.canvas)
        self.bind_mouse_wheel(self.scrollable_frame)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.load_sub_frames()

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def bind_mouse_wheel(self, widget):
        widget.bind_all('<MouseWheel>', self._on_mousewheel)
        widget.bind_all('<Button-4>', self._on_mousewheel)
        widget.bind_all('<Button-5>', self._on_mousewheel)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, 'units')
        elif event.num == 5:
            self.canvas.yview_scroll(1, 'units')
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')

    def draw_round_bg(self, canvas, w, h, r, bg, border):
        canvas.delete('bg')
        x1, y1, x2, y2 = (1, 1, w - 1, h - 1)
        canvas.create_arc(x1, y1, x1 + r * 2, y1 + r * 2, start=90, extent=90, fill=bg, outline=border, tags='bg')
        canvas.create_arc(x2 - r * 2, y1, x2, y1 + r * 2, start=0, extent=90, fill=bg, outline=border, tags='bg')
        canvas.create_arc(x1, y2 - r * 2, x1 + r * 2, y2, start=180, extent=90, fill=bg, outline=border, tags='bg')
        canvas.create_arc(x2 - r * 2, y2 - r * 2, x2, y2, start=270, extent=90, fill=bg, outline=border, tags='bg')
        canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=bg, outline='', tags='bg')
        canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=bg, outline='', tags='bg')
        canvas.create_line(x1 + r, y1, x2 - r, y1, fill=border, tags='bg')
        canvas.create_line(x1 + r, y2, x2 - r, y2, fill=border, tags='bg')
        canvas.create_line(x1, y1 + r, x1, y2 - r, fill=border, tags='bg')
        canvas.create_line(x2, y1 + r, x2, y2 - r, fill=border, tags='bg')
        canvas.tag_lower('bg')

    def load_sub_frames(self):
        settings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings')
        if not os.path.exists(settings_dir):
            return
        files = sorted([f for f in os.listdir(settings_dir) if f.endswith('.py') and f != '__init__.py'])
        for file in files:
            module_name = file[:-3]
            try:
                spec = importlib.util.spec_from_file_location(module_name, os.path.join(settings_dir, file))
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                if hasattr(module, 'SettingsFrame'):
                    c = tk.Canvas(self.scrollable_frame, bg=self.COLORS['bg_dark'], highlightthickness=0)
                    c.pack(fill='x', padx=25, pady=10)
                    f = tk.Frame(c, bg=self.FRAME_BG)
                    f_id = c.create_window(self.OFFSET, self.OFFSET, window=f, anchor='nw')

                    def update_res(e, canvas=c, frame=f, frame_id=f_id):
                        frame.update_idletasks()
                        w = e.width
                        h = frame.winfo_reqheight() + self.OFFSET * 2
                        canvas.itemconfig(frame_id, width=w - self.OFFSET * 2)
                        canvas.config(height=h)
                        self.draw_round_bg(canvas, w, h, self.RADIUS, self.FRAME_BG, self.FRAME_BORDER)
                    c.bind('<Configure>', update_res)
                    title = getattr(module, 'SECTION_NAME', module_name.upper())
                    header = tk.Label(f, text=f' {title}', fg=self.ACCENT_COLOR, bg=self.FRAME_BG, font=('Consolas', 10, 'bold'))
                    header.pack(anchor='w', padx=20, pady=(20, 10))
                    sub_f = module.SettingsFrame(f, self.COLORS)
                    sub_f.configure(bg=self.FRAME_BG)
                    sub_f.pack(fill='both', expand=True, padx=20, pady=(0, 20))
            except Exception as e:
                print(f'[X] Error loading {file}: {e}')