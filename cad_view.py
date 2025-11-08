# cad_view.py

from math import floor, ceil

class CADView:
    """Отвечает за отрисовку сетки, осей и объектов на холсте."""

    def __init__(self, canvas_ref, transform_ref, scene_ref):
        self.canvas = canvas_ref
        self.trans = transform_ref
        self.scene = scene_ref
        self.bg_color = "#121212"
        self.grid_color = "#333333"

    def set_bg_color(self, color):
        self.bg_color = color
        self.canvas.config(bg=self.bg_color)

    def draw_all(self):
        """Основная функция перерисовки."""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_axes()
        self.draw_labels()
        self.draw_segments()

    def draw_segments(self):
        """Рисует все отрезки сцены."""
        for s in self.scene.segments:
            p1 = self.trans.world_to_canvas(s.x1, s.y1)
            p2 = self.trans.world_to_canvas(s.x2, s.y2)
            self.canvas.create_line(p1, p2, fill=s.color, width=3, smooth=True, caps="round", tags="segment")

    def draw_grid(self):
        """Рисует адаптивную сетку."""
        step = self.trans.grid_step()
        wx1, wy1, wx2, wy2 = self.trans.get_visible_bounds()
        sx, ex = floor(wx1 / step) * step, ceil(wx2 / step) * step
        sy, ey = floor(wy1 / step) * step, ceil(wy2 / step) * step

        # Рисование вертикальных линий
        for x in range(int(sx / step), int(ex / step) + 1):
            p1 = self.trans.world_to_canvas(x * step, sy)
            p2 = self.trans.world_to_canvas(x * step, ey)
            self.canvas.create_line(p1, p2, fill=self.grid_color, tags="grid")

        # Рисование горизонтальных линий
        for y in range(int(sy / step), int(ey / step) + 1):
            p1 = self.trans.world_to_canvas(sx, y * step)
            p2 = self.trans.world_to_canvas(ex, y * step)
            self.canvas.create_line(p1, p2, fill=self.grid_color, tags="grid")

    def draw_axes(self):
        """Рисует оси X и Y."""
        b = self.trans.get_visible_bounds()
        inf = max(abs(x) for x in b) * 2 + 1000
        self.canvas.create_line(self.trans.world_to_canvas(-inf, 0), self.trans.world_to_canvas(inf, 0), fill="#774444", width=2)
        self.canvas.create_line(self.trans.world_to_canvas(0, -inf), self.trans.world_to_canvas(0, inf), fill="#447744", width=2)
        o = self.trans.world_to_canvas(0, 0)
        self.canvas.create_text(o[0] + 5, o[1] + 5, text="0", fill="#666", anchor="nw")

    def draw_labels(self):
        """Рисует метки координат вдоль осей."""
        step = self.trans.grid_step()
        b = self.trans.get_visible_bounds()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        fmt = lambda v: f"{int(round(v))}" if abs(v - round(v)) < 1e-9 else f"{v:.2f}".rstrip("0").rstrip(".")

        for x in range(int(floor(b[0] / step)), int(ceil(b[2] / step)) + 1):
            if x == 0: continue
            cx, cy = self.trans.world_to_canvas(x * step, 0)
            if -20 < cx < w + 20 and -20 < cy < h + 20:
                self.canvas.create_text(cx, cy + 15, text=fmt(x * step), fill="#888", font=("Arial", 8))
        for y in range(int(floor(b[1] / step)), int(ceil(b[3] / step)) + 1):
            if y == 0: continue
            cx, cy = self.trans.world_to_canvas(0, y * step)
            if -20 < cx < w + 20 and -20 < cy < h + 20:
                self.canvas.create_text(cx - 25, cy, text=fmt(y * step), fill="#888", font=("Arial", 8), anchor="e")

    def draw_preview(self, w1, w2, color):
        """Рисует временный отрезок (предпросмотр)."""
        p1 = self.trans.world_to_canvas(*w1)
        p2 = self.trans.world_to_canvas(*w2)
        self.canvas.delete("preview")
        self.canvas.create_line(p1, p2, fill=color, width=3, dash=(8, 4), tags="preview")

    def clear_preview(self):
        """Удаляет временный отрезок."""
        self.canvas.delete("preview")