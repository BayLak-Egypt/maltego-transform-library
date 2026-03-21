import tkinter as tk
import math

class ActionButton(tk.Canvas):

    def __init__(self, master, text, command, colors, btn_type='primary', **kwargs):
        if btn_type == 'primary':
            self.accent_color = colors.get('accent', '#0078d7')
        elif btn_type == 'danger':
            self.accent_color = colors.get('danger', '#ff4444')
        else:
            self.accent_color = colors.get(btn_type, '#0078d7')
        self.bg_card = colors.get('bg_card', '#1e1e1e')
        self.text_main = colors.get('text_main', '#ffffff')
        self.width = kwargs.pop('width', 110)
        self.height = kwargs.pop('height', 30)
        self.radius = 10
        super().__init__(master, width=self.width, height=self.height, highlightthickness=0, bg=self.bg_card, cursor='hand2')
        self.text = text
        self.command = command
        self._anim_job = None
        self.current_y = self.height + 15
        self.target_y = self.height + 15
        self.wave_offset = 0
        self.is_hovered = False
        self.loading_mode = False
        self.progress_val = 0
        self.orange_color = '#FF8C00'
        self._setup_ui()
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
        self.bind('<Button-1>', self._on_click)

    def _setup_ui(self):
        self.delete('all')
        r = self.radius
        pts = [r, 0, self.width - r, 0, self.width, 0, self.width, r, self.width, self.height - r, self.width, self.height, self.width - r, self.height, r, self.height, 0, self.height, 0, self.height - r, 0, r, 0, 0]
        self.create_polygon(pts, smooth=True, fill=self.bg_card, tags='bg')
        self.text_id = self.create_text(self.width / 2, self.height / 2, text=self.text, fill=self.accent_color, font=('Consolas', 9, 'bold'), tags='text')
        self.create_polygon(pts, smooth=True, fill='', outline=self.accent_color, width=1.5, tags='border')

    def start_loading(self):
        self.loading_mode = True
        self.is_hovered = True
        self.itemconfig(self.text_id, text='0%', fill='#ffffff')
        self._animate()

    def update_progress(self, val):
        self.progress_val = val
        self.target_y = self.height - self.height * (val / 100)
        self.itemconfig(self.text_id, text=f'{int(val)}%')
        self.itemconfig('border', outline=self.orange_color)
        if self.loading_mode:
            self._animate()

    def _on_click(self, e):
        if not self.loading_mode:
            self.command()

    def _on_enter(self, e):
        if not self.loading_mode:
            self.is_hovered = True
            self.target_y = self.height / 2.5
            self.itemconfig(self.text_id, fill=self.text_main)
            self._animate()

    def _on_leave(self, e):
        if not self.loading_mode:
            self.is_hovered = False
            self.target_y = self.height + 15
            self.itemconfig(self.text_id, fill=self.accent_color)
            self._animate()

    def _animate(self):
        if self._anim_job:
            self.after_cancel(self._anim_job)
        diff = self.target_y - self.current_y
        if not self.is_hovered and (not self.loading_mode) and (abs(diff) < 0.5):
            self.delete('wave')
            return
        self.current_y += diff * 0.15
        self.wave_offset += 0.3
        self.delete('wave')
        wave_pts = []
        for x in range(-10, self.width + 11, 5):
            y = self.current_y + 3 * math.sin(x / 15 + self.wave_offset)
            wave_pts.append(x)
            wave_pts.append(y)
        wave_pts.extend([self.width + 10, self.height + 20, -10, self.height + 20])
        current_fill = self.orange_color if self.loading_mode else self.accent_color
        self.create_polygon(wave_pts, fill=current_fill, tags='wave', smooth=True)
        self.tag_raise('wave', 'bg')
        self.tag_raise('text', 'wave')
        self.tag_raise('border', 'text')
        self._anim_job = self.after(20, self._animate)