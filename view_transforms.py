# view_transforms.py

from math import degrees, radians, cos, sin, ceil, floor, log10

class ViewTransform:
    """Управляет масштабом, смещением и вращением для преобразования координат."""

    def __init__(self, canvas_ref, scene_ref, base_scale=20.0):
        self.canvas = canvas_ref
        self.scene = scene_ref
        self.BASE_SCALE = base_scale
        self.offset_x, self.offset_y = 0.0, 0.0
        self.scale = self.BASE_SCALE
        self.rotation_angle = 0.0 # в радианах

    # --- ПРЕОБРАЗОВАНИЯ КООРДИНАТ ---

    def world_to_canvas(self, wx, wy):
        """Мировые координаты -> Координаты холста."""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w / 2.0, h / 2.0
        tx, ty = wx - self.offset_x, wy - self.offset_y
        ca, sa = cos(self.rotation_angle), sin(self.rotation_angle)
        return cx + (tx * ca + ty * sa) * self.scale, cy - (-tx * sa + ty * ca) * self.scale

    def canvas_to_world(self, cx, cy):
        """Координаты холста -> Мировые координаты."""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        rx, ry = (cx - w / 2.0) / self.scale, (h / 2.0 - cy) / self.scale
        ca, sa = cos(-self.rotation_angle), sin(-self.rotation_angle)
        return rx * ca + ry * sa + self.offset_x, -rx * sa + ry * ca + self.offset_y

    def get_visible_bounds(self):
        """Возвращает мировые границы видимой области."""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        pts = [self.canvas_to_world(0, 0), self.canvas_to_world(w, 0),
               self.canvas_to_world(w, h), self.canvas_to_world(0, h)]
        return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)

    def grid_step(self):
        """Вычисляет подходящий шаг сетки для текущего масштаба."""
        target = 100 / self.scale
        p10 = 10 ** floor(log10(target) if target > 0 else 0)
        m = target / p10
        return (1 * p10) if m < 2 else (2 * p10) if m < 5 else (5 * p10)

    # --- МЕТОДЫ УПРАВЛЕНИЯ ВИДОМ ---

    def pan(self, dx, dy):
        """
        Смещает начало мировых координат.
        dx, dy — это смещение курсора на холсте.
        Мы вычисляем, насколько эти dx, dy соответствуют мировым координатам,
        и обновляем смещение.

        Чтобы сцена двигалась вправо (увеличение x курсора), offset_x должен уменьшаться.
        """

        # Переводим смещение на холсте (dx, dy) в смещение в мировых координатах.
        # Для этого нужно перевести две точки холста (0, 0) и (dx, dy) в мир
        # и найти разницу между ними.
        w1 = self.canvas_to_world(0, 0)
        w2 = self.canvas_to_world(dx, dy)

        dx_world = w2[0] - w1[0]
        dy_world = w2[1] - w1[1]

        # Для панорамирования мы должны переместить начало координат (offset)
        # в направлении, ПРОТИВОПОЛОЖНОМ движению мыши.
        # Если мышь движется вправо (dx > 0), объекты должны двигаться вправо,
        # что означает, что мировое начало (offset_x) должно сместиться влево (уменьшиться).
        self.offset_x -= dx_world
        self.offset_y -= dy_world

    def zoom_at_point(self, zoom_factor, cx, cy):
        """Масштабирование относительно точки на холсте (cx, cy)."""
        w1 = self.canvas_to_world(cx, cy)
        self.scale = max(0.01, min(self.scale * zoom_factor, 10000.0))
        w2 = self.canvas_to_world(cx, cy)
        self.offset_x += (w1[0] - w2[0])
        self.offset_y += (w1[1] - w2[1])

    def zoom_extents(self):
        """Подгонка масштаба под всю сцену."""
        if not self.scene.segments:
            self.offset_x, self.offset_y, self.scale = 0, 0, self.BASE_SCALE
        else:
            xs = [s.x1 for s in self.scene.segments] + [s.x2 for s in self.scene.segments]
            ys = [s.y1 for s in self.scene.segments] + [s.y2 for s in self.scene.segments]
            mx, Mx, my, My = min(xs), max(xs), min(ys), max(ys)
            w, h = Mx - mx, My - my

            if w == 0 and h == 0:
                w, h = 10, 10
                mx, my = mx - 5, my - 5
                Mx, My = Mx + 5, My + 5

            canvas_w = self.canvas.winfo_width() or 1200
            canvas_h = self.canvas.winfo_height() or 700

            scale_x = canvas_w / (w * 1.2)
            scale_y = canvas_h / (h * 1.2)

            self.scale = min(scale_x, scale_y)
            self.offset_x, self.offset_y = (mx + Mx) / 2, (my + My) / 2

    def rotate_view(self, angle_degrees):
        """Поворот вида."""
        self.rotation_angle += radians(angle_degrees)