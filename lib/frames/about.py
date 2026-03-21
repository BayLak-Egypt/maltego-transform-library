import tkinter as tk
import requests
import os
import webbrowser
import math
from lib.styles.styles import COLORS

class AboutFrame(tk.Frame):
    SOCIAL_URL = 'https://baylak-egypt.github.io/mysocial.txt'
    ICON_SIZE = 24
    HOVER_SCALE = 1.25

    def __init__(self, parent, colors=COLORS, **kwargs):
        super().__init__(parent, bg=colors['bg_dark'], **kwargs)
        self.colors = colors
        self.img_refs = []
        self.wave_phase = 0
        self.bg_canvas = tk.Canvas(self, bg=colors['bg_dark'], highlightthickness=0)
        self.bg_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.content = tk.Frame(self, bg=colors['bg_dark'])
        self.content.place(relx=0.5, rely=0.45, anchor='center')
        tk.Label(self.content, text='Maltego Transforms Library v1.0', font=('Segoe UI', 18, 'bold'), fg=colors['accent'], bg=colors['bg_dark']).pack()
        tk.Label(self.content, text='Professional OSINT Toolkit', font=('Segoe UI', 10, 'italic'), fg='#888888', bg=colors['bg_dark']).pack(pady=(0, 20))
        self.social_links = self.fetch_social_links()
        self.create_social_hub()
        self.footer = tk.Label(self, text='Made by BayLak', font=('Consolas', 11, 'bold'), fg=colors['accent'], bg=colors['bg_dark'])
        self.footer.pack(side='bottom', pady=30)
        self.animate_waves()

    def create_social_hub(self):
        if not self.social_links:
            return
        num_icons = len(self.social_links)
        padding_x = 25
        hub_height = 60
        hub_width = num_icons * self.ICON_SIZE + (num_icons + 1) * padding_x
        self.hub_canvas = tk.Canvas(self.content, width=hub_width, height=hub_height, bg=self.colors['bg_dark'], highlightthickness=0)
        self.hub_canvas.pack(pady=10)
        self.draw_rounded_rect(self.hub_canvas, 2, 2, hub_width - 2, hub_height - 2, radius=hub_height // 2, fill=self.colors['accent'], outline=self._adjust_color(self.colors['accent'], 0.8), width=2)
        hover_size = int(self.ICON_SIZE * self.HOVER_SCALE)
        current_x = padding_x + self.ICON_SIZE // 2
        for platform, url in self.social_links.items():
            icon_path = os.path.join(os.path.dirname(__file__), '../styles/icons', f'{platform}.png')
            if os.path.exists(icon_path):
                try:
                    full_img = tk.PhotoImage(file=icon_path)
                    factor = max(1, full_img.width() // self.ICON_SIZE)
                    img_normal = full_img.subsample(factor, factor)
                    factor_hover = max(1, full_img.width() // hover_size)
                    img_hover = full_img.subsample(factor_hover, factor_hover)
                    self.img_refs.append(img_normal)
                    self.img_refs.append(img_hover)
                    icon_center_y = hub_height // 2
                    normal_item = self.hub_canvas.create_image(current_x, icon_center_y, image=img_normal, tags=(platform, 'icon'))
                    hover_item = self.hub_canvas.create_image(current_x, icon_center_y, image=img_hover, state='hidden', tags=(platform, 'icon', 'hover'))
                    self.hub_canvas.tag_bind(normal_item, '<Enter>', lambda e, ni=normal_item, hi=hover_item: self._toggle_hover(ni, hi, True))
                    self.hub_canvas.tag_bind(hover_item, '<Leave>', lambda e, ni=normal_item, hi=hover_item: self._toggle_hover(ni, hi, False))
                    self.hub_canvas.tag_bind(normal_item, '<Button-1>', lambda e, l=url: webbrowser.open(l))
                    self.hub_canvas.tag_bind(hover_item, '<Button-1>', lambda e, l=url: webbrowser.open(l))
                    current_x += self.ICON_SIZE + padding_x
                except:
                    continue

    def _toggle_hover(self, normal_item, hover_item, entering):
        if entering:
            self.hub_canvas.itemconfig(normal_item, state='hidden')
            self.hub_canvas.itemconfig(hover_item, state='normal')
            self.hub_canvas.config(cursor='hand2')
        else:
            self.hub_canvas.itemconfig(normal_item, state='normal')
            self.hub_canvas.itemconfig(hover_item, state='hidden')
            self.hub_canvas.config(cursor='')

    def draw_rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [x1 + radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius, x2, y2 - radius, x2, y2, x2 - radius, y2, x1 + radius, y2, x1, y2, x1, y2 - radius, x1, y1 + radius, x1, y1]
        return canvas.create_polygon(points, **kwargs, smooth=True)

    def animate_waves(self):
        self.bg_canvas.delete('wave')
        w = self.winfo_width()
        h = self.winfo_height()
        if w > 1:
            main_color = self.colors['accent']
            wave_colors = [self._adjust_color(main_color, 0.2), self._adjust_color(main_color, 0.4), self._adjust_color(main_color, 0.7), main_color]
            for i, color in enumerate(wave_colors):
                points = []
                amplitude = 12 + i * 6
                frequency = 0.008 + i * 0.002
                y_center = h * 0.65 + i * 15
                for x in range(-10, w + 30, 20):
                    y = y_center + math.sin(x * frequency + self.wave_phase + i * 0.5) * amplitude
                    points.extend([x, y])
                self.bg_canvas.create_line(points, fill=color, smooth=True, width=2, tags='wave')
        self.wave_phase += 0.07
        self.after(40, self.animate_waves)

    def _adjust_color(self, hex_color, factor):
        hex_color = hex_color.lstrip('#')
        rgb = tuple((int(hex_color[i:i + 2], 16) for i in (0, 2, 4)))
        new_rgb = tuple((max(0, min(255, int(c * factor))) for c in rgb))
        return '#{:02x}{:02x}{:02x}'.format(*new_rgb)

    def fetch_social_links(self):
        try:
            resp = requests.get(self.SOCIAL_URL, timeout=3)
            return {line.split('=')[0].strip(): line.split('=')[1].strip() for line in resp.text.splitlines() if '=' in line}
        except:
            return {}