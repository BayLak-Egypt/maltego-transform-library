import os
from PIL import Image, ImageTk, ImageDraw, ImageStat

class IconManager:

    def __init__(self, lib_dir):
        self.lib_dir = lib_dir
        self.supported_formats = ('.png', '.jpg', '.jpeg', '.ico')
        self._cache = {}

    def _get_contrast_color(self, img, bg_color):
        stat = ImageStat.Stat(img)
        avg_rgb = stat.median[:3]
        dist = sum(((a - b) ** 2 for a, b in zip(avg_rgb, bg_color[:3]))) ** 0.5
        if dist < 60:
            new_rgb = tuple((255 - c for c in bg_color[:3]))
            return new_rgb + (bg_color[3],)
        return bg_color

    def get_lib_icon(self, folder_name, size=(35, 35), border_width=2, border_color=(100, 100, 100, 255), corner_radius=10):
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
                            img = img.convert('RGBA').resize(size, Image.Resampling.LANCZOS)
                            final_border_color = self._get_contrast_color(img, border_color)
                            img_mask = Image.new('L', size, 0)
                            draw_img_mask = ImageDraw.Draw(img_mask)
                            draw_img_mask.rounded_rectangle([0, 0, size[0], size[1]], radius=corner_radius, fill=255)
                            rounded_img = Image.new('RGBA', size, (0, 0, 0, 0))
                            rounded_img.paste(img, (0, 0), mask=img_mask)
                            if border_width > 0:
                                full_size = (size[0] + 2 * border_width, size[1] + 2 * border_width)
                                border_mask = Image.new('L', full_size, 0)
                                draw_border = ImageDraw.Draw(border_mask)
                                draw_border.rounded_rectangle([0, 0, full_size[0], full_size[1]], radius=corner_radius + border_width, fill=255)
                                cased_img = Image.new('RGBA', full_size, final_border_color)
                                cased_img.putalpha(border_mask)
                                cased_img.paste(rounded_img, (border_width, border_width), rounded_img)
                                img = cased_img
                            else:
                                img = rounded_img
                            icon = ImageTk.PhotoImage(img)
                            self._cache[cache_key] = icon
                            return icon
        except Exception as e:
            print(f'Error processing icon for {folder_name}: {e}')
        return None