import tkinter as tk
import math

class ToastNotification:

    def __init__(self, root, message, color=None, duration=3000, font=('Segoe UI', 10, 'bold')):
        self.root = root
        self.message = message
        self.duration = duration
        self.bg_color = color if color else '#333333'
        self.text_color = '#FFFFFF'
        self.width = 350
        self.height = 50
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg=root.cget('bg'), highlightthickness=0)
        self.root.update_idletasks()
        self.root_width = self.root.winfo_width()
        self.root_height = self.root.winfo_height()
        self.start_x = (self.root_width - self.width) // 2
        self.start_y = self.root_height + 20
        self.target_y = self.root_height - 80
        self.current_y = self.start_y
        self._draw_toast(font)
        self.canvas.place(x=self.start_x, y=self.current_y)
        self._animate_in()

    def _draw_toast(self, font):
        r = 15
        pts = [r, 0, self.width - r, 0, self.width, 0, self.width, r, self.width, self.height - r, self.width, self.height, self.width - r, self.height, r, self.height, 0, self.height, 0, self.height - r, 0, r, 0, 0]
        self.canvas.create_polygon(pts, fill=self.bg_color, smooth=True, tags='rect')
        self.canvas.create_text(self.width / 2, self.height / 2, text=self.message, fill=self.text_color, font=font, width=self.width - 40, justify='center')
        self.canvas.bind('<Button-1>', lambda e: self._animate_out())

    def _animate_in(self):
        diff = self.target_y - self.current_y
        if abs(diff) > 1:
            self.current_y += diff * 0.15
            self.canvas.place(y=self.current_y)
            self.root.after(10, self._animate_in)
        else:
            self.canvas.place(y=self.target_y)
            self.root.after(self.duration, self._animate_out)

    def _animate_out(self):
        diff = self.root_height + 20 - self.current_y
        if abs(diff) > 1:
            self.current_y += diff * 0.15
            self.canvas.place(y=self.current_y)
            self.root.after(10, self._animate_out)
        else:
            self.canvas.destroy()

def show_msg(root, text, type='info', duration=3000):
    colors = {'info': '#2196F3', 'error': '#F44336', 'success': '#4CAF50', 'warning': '#FF9800', 'dark': '#1E1E1E'}
    color = colors.get(type, '#333333')
    ToastNotification(root, text, color=color, duration=duration)