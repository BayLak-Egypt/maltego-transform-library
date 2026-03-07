import tkinter as tk
from tkinter import ttk
import os
from PIL import Image, ImageTk
from lib.styles.styles import COLORS
from lib.searchiconlibrary import IconManager
from lib.styles.search import SearchHeader
try:
    from .frames.library import LibraryInfoFrame
except ImportError:

    class LibraryInfoFrame(tk.Frame):

        def __init__(self, parent, lib_dir, libs):
            super().__init__(parent, bg=COLORS['bg_dark'])
            tk.Label(self, text='[ SYSTEM INVENTORY PAGE ]', font=('Consolas', 14), fg=COLORS['accent'], bg=COLORS['bg_dark']).pack(expand=True)
try:
    from .frames.settings import SettingsFrame
except ImportError:

    class SettingsFrame(tk.Frame):

        def __init__(self, parent, colors):
            super().__init__(parent, bg=colors['bg_dark'])
            tk.Label(self, text='[ SETTINGS PAGE NOT FOUND ]', font=('Consolas', 14), fg='red', bg=colors['bg_dark']).pack(expand=True)
try:
    from .frames.about import AboutFrame
except ImportError:

    class AboutFrame(tk.Frame):

        def __init__(self, parent, colors=COLORS):
            super().__init__(parent, bg=colors['bg_dark'])
            tk.Label(self, text='[ ABOUT PAGE NOT FOUND ]', font=('Consolas', 14), fg='red', bg=colors['bg_dark']).pack(expand=True)

class LibraryMenu:

    def __init__(self, filtered_libs, input_type='None', standalone_mode=False):
        self.is_standalone = input_type in ['All', 'None'] or standalone_mode
        self.selected_libs = []
        self.filtered_libs = filtered_libs
        self.COLORS = COLORS
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.dirname(current_dir) if os.path.basename(current_dir) == 'lib' else current_dir
        self.lib_dir = os.path.join(self.base_dir, 'library')
        self.sidebar_logo_path = os.path.join(self.base_dir, 'lib', 'styles', 'icons', 'logo.png')
        self.icon_manager = IconManager(self.lib_dir)
        self.lib_icons = {}
        self.root = tk.Tk()
        self.root.title('Maltego Transforms Library')
        self.root.geometry('1100x750')
        self.root.configure(bg=self.COLORS['bg_dark'])
        self.vars = {lib['folder_name']: tk.BooleanVar(value=True) for lib in self.filtered_libs}
        self.logo_angle = 0
        self.logo_direction = 1
        self.max_rotation = 15
        self.rotation_speed = 0.5
        self.animation_delay = 20
        self.pil_logo_base = None
        self.logo_label_ref = None
        self.setup_ui()
        if self.pil_logo_base:
            self.animate_logo()
        self.update_list()

    def setup_ui(self):
        self.sidebar = tk.Frame(self.root, bg=self.COLORS['sidebar'], width=230)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)
        self.setup_sidebar_logo()
        tk.Label(self.sidebar, text='Maltego Transforms', font=('Segoe UI Black', 12), fg=self.COLORS['accent'], bg=self.COLORS['sidebar'], pady=10).pack()
        btn_style = {'bg': self.COLORS['sidebar'], 'fg': self.COLORS['text_main'], 'font': ('Segoe UI', 10, 'bold'), 'bd': 0, 'cursor': 'hand2', 'anchor': 'w', 'padx': 25, 'pady': 15, 'activebackground': self.COLORS['accent'], 'activeforeground': 'black'}
        if not self.is_standalone:
            tk.Button(self.sidebar, text='TRANSFORMS', command=lambda: self.show_frame('main'), **btn_style).pack(fill='x')
        tk.Button(self.sidebar, text='INVENTORY', command=lambda: self.show_frame('library'), **btn_style).pack(fill='x')
        tk.Button(self.sidebar, text='SETTINGS', command=lambda: self.show_frame('settings'), **btn_style).pack(fill='x')
        tk.Button(self.sidebar, text='ABOUT', command=lambda: self.show_frame('about'), **btn_style).pack(fill='x')
        try:
            import addmylibrary
            self.bottom_container = tk.Frame(self.sidebar, bg=self.COLORS['sidebar'])
            self.bottom_container.pack(side='bottom', fill='x', pady=20)
            self.my_custom_widget = addmylibrary.create_box(self.bottom_container)
            self.my_custom_widget.pack(padx=10)
        except Exception as e:
            print(f'Error loading addmylibrary: {e}')
        self.container = tk.Frame(self.root, bg=self.COLORS['bg_dark'])
        self.container.pack(side='right', fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        self.create_main_page()
        self.frames['library'] = LibraryInfoFrame(self.container, self.lib_dir, self.filtered_libs)
        self.frames['library'].grid(row=0, column=0, sticky='nsew')
        self.frames['settings'] = SettingsFrame(self.container, self.COLORS)
        self.frames['settings'].grid(row=0, column=0, sticky='nsew')
        self.frames['about'] = AboutFrame(self.container, self.COLORS)
        self.frames['about'].grid(row=0, column=0, sticky='nsew')
        self.show_frame('library' if self.is_standalone else 'main')

    def setup_sidebar_logo(self):
        try:
            if os.path.exists(self.sidebar_logo_path):
                self.pil_logo_base = Image.open(self.sidebar_logo_path).convert('RGBA')
                self.pil_logo_base = self.pil_logo_base.resize((80, 80), Image.Resampling.LANCZOS)
                initial_photo = ImageTk.PhotoImage(self.pil_logo_base)
                self.sidebar_photo_ref = initial_photo
                self.logo_label_ref = tk.Label(self.sidebar, image=initial_photo, bg=self.COLORS['sidebar'])
                self.logo_label_ref.pack(pady=(30, 0))
        except:
            pass

    def animate_logo(self):
        try:
            self.logo_angle += self.rotation_speed * self.logo_direction
            if abs(self.logo_angle) >= self.max_rotation:
                self.logo_direction *= -1
            rotated_pil_img = self.pil_logo_base.rotate(self.logo_angle, resample=Image.BICUBIC)
            self.sidebar_photo_ref = ImageTk.PhotoImage(rotated_pil_img)
            if self.logo_label_ref and self.logo_label_ref.winfo_exists():
                self.logo_label_ref.config(image=self.sidebar_photo_ref)
                self.root.after(self.animation_delay, self.animate_logo)
        except:
            pass

    def show_frame(self, name):
        if name in self.frames:
            self.frames[name].tkraise()

    def create_main_page(self):
        frame = tk.Frame(self.container, bg=self.COLORS['bg_dark'])
        self.frames['main'] = frame
        frame.grid(row=0, column=0, sticky='nsew')
        self.main_header = SearchHeader(frame, self.COLORS, on_search_callback=lambda q: self.update_list())
        self.main_header.pack(fill='x', padx=30, pady=20)
        canvas_box = tk.Frame(frame, bg=self.COLORS['bg_dark'])
        canvas_box.pack(fill='both', expand=True, padx=30)
        self.canvas = tk.Canvas(canvas_box, bg=self.COLORS['bg_dark'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_box, orient='vertical', command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg=self.COLORS['bg_dark'])
        self.scroll_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox('all')))
        self.canvas_win = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_win, width=e.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.counter_label = tk.Label(frame, text='', font=('Consolas', 10), fg=self.COLORS['accent'], bg=self.COLORS['bg_dark'])
        self.counter_label.pack(pady=5)
        tk.Button(frame, text='EXECUTE SELECTED TRANSFORMS', command=self.on_confirm, bg=self.COLORS['accent'], fg='black', font=('Segoe UI', 11, 'bold'), bd=0, height=2, cursor='hand2').pack(fill='x', padx=30, pady=20)

    def update_list(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()
        search = self.main_header.get_query().lower()
        self.lib_icons.clear()
        for lib in self.filtered_libs:
            name = lib.get('display_name', lib['folder_name'])
            folder = lib['folder_name']
            if search in name.lower():
                card = tk.Frame(self.scroll_frame, bg=self.COLORS['bg_card'], pady=8, padx=15)
                card.pack(fill='x', pady=4, padx=5)
                tk.Frame(card, bg=self.COLORS['accent'], width=3).pack(side='left', fill='y')
                icon_img = self.icon_manager.get_lib_icon(folder)
                if icon_img:
                    self.lib_icons[folder] = icon_img
                    tk.Label(card, image=icon_img, bg=self.COLORS['bg_card']).pack(side='left', padx=(10, 5))
                else:
                    tk.Label(card, text='📁', bg=self.COLORS['bg_card'], fg=self.COLORS['text_dim']).pack(side='left', padx=(10, 5))
                tk.Label(card, text=name.upper(), font=('Segoe UI', 10, 'bold'), fg=self.COLORS['text_main'], bg=self.COLORS['bg_card'], anchor='w').pack(side='left', padx=10)
                chk = tk.Checkbutton(card, variable=self.vars[folder], bg=self.COLORS['bg_card'], activebackground=self.COLORS['bg_card'], selectcolor='black', fg=self.COLORS['accent'], command=self.update_counter)
                chk.pack(side='right')
        self.update_counter()

    def update_counter(self):
        selected = sum((1 for v in self.vars.values() if v.get()))
        self.counter_label.config(text=f'SELECTED: {selected}  |  TOTAL: {len(self.filtered_libs)}')

    def on_confirm(self):
        self.selected_libs = [n for n, v in self.vars.items() if v.get()]
        self.root.destroy()

    def show(self):
        self.root.mainloop()
        return self.selected_libs