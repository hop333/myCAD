from math import degrees, radians, cos, sin, ceil, floor, log10


class ViewTransform:

    def __init__(self, canvas_ref, scene_ref, base_scale=20.0):
        self.canvas = canvas_ref
        self.scene = scene_ref
        self.BASE_SCALE = base_scale
        self.offset_x, self.offset_y = 0.0, 0.0
        self.scale = self.BASE_SCALE
        self.rotation_angle = 0.0  # В радианах

    def world_to_canvas(self, wx, wy):
        """Преобразует мировые координаты (wx, wy) в координаты холста (cx, cy)."""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w / 2.0, h / 2.0

        # 1. Смещение
        tx, ty = wx - self.offset_x, wy - self.offset_y

        # 2. Вращение
        ca, sa = cos(self.rotation_angle), sin(self.rotation_angle)
        rx = tx * ca + ty * sa
        ry = -tx * sa + ty * ca

        # 3. Масштаб и сдвиг
        return cx + rx * self.scale, cy - ry * self.scale

    def canvas_to_world(self, cx, cy):
        """Преобразует координаты холста (cx, cy) в мировые координаты (wx, wy)."""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()

        # 1. Обратный масштаб и сдвиг от центра
        rx, ry = (cx - w / 2.0) / self.scale, (h / 2.0 - cy) / self.scale

        # 2. Обратное вращение
        ca, sa = cos(-self.rotation_angle), sin(-self.rotation_angle)
        tx = rx * ca + ry * sa
        ty = -rx * sa + ry * ca

        # 3. Обратное смещение
        return tx + self.offset_x, ty + self.offset_y

    def get_visible_bounds(self):
        """Возвращает границы видимой мировой области."""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        pts = [self.canvas_to_world(0, 0), self.canvas_to_world(w, 0),
               self.canvas_to_world(w, h), self.canvas_to_world(0, h)]
        return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)

    def grid_step(self):
        """Вычисляет оптимальный шаг сетки."""
        target = 100 / self.scale
        p10 = 10 ** floor(log10(target) if target > 0 else 0)
        m = target / p10
        return (1 * p10) if m < 2 else (2 * p10) if m < 5 else (5 * p10)

    def pan(self, dx_c, dy_c):
        """Перемещает (панорамирует) вид на основе смещения холста."""
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()

        wx_old, wy_old = self.canvas_to_world(w / 2, h / 2)
        wx_new, wy_new = self.canvas_to_world(w / 2 - dx_c, h / 2 - dy_c)

        self.offset_x += wx_new - wx_old
        self.offset_y += wy_new - wy_old

    def zoom_at_point(self, factor, cx, cy):
        """Увеличивает/уменьшает масштаб, центрируя вокруг точки холста (cx, cy)."""
        wx, wy = self.canvas_to_world(cx, cy)

        self.scale *= factor
        if self.scale < 0.1: self.scale = 0.1

        wx_new, wy_new = self.canvas_to_world(cx, cy)

        self.offset_x -= (wx_new - wx)
        self.offset_y -= (wy_new - wy)

    def zoom_extents(self):
        """Масштабирует вид так, чтобы все объекты сцены были видны."""
        if not self.scene.segments:
            self.offset_x, self.offset_y = 0.0, 0.0
            self.scale = self.BASE_SCALE
            return

        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w <= 1 or h <= 1: return

        all_x = [s.x1 for s in self.scene.segments] + [s.x2 for s in self.scene.segments]
        all_y = [s.y1 for s in self.scene.segments] + [s.y2 for s in self.scene.segments]

        if not all_x: return

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        buffer = 5.0
        min_x -= buffer
        max_x += buffer
        min_y -= buffer
        max_y += buffer

        center_x = (min_x + max_x) / 2.0
        center_y = (min_y + max_y) / 2.0

        scene_width = max_x - min_x
        scene_height = max_y - min_y

        scale_x = w / scene_width if scene_width > 0 else self.BASE_SCALE
        scale_y = h / scene_height if scene_height > 0 else self.BASE_SCALE

        new_scale = min(scale_x, scale_y) * 0.9
        if new_scale < 0.1: new_scale = self.BASE_SCALE

        self.scale = new_scale

        self.offset_x = center_x
        self.offset_y = center_y

    def rotate_view(self, angle_deg):
        """Поворачивает вид на заданный угол (в градусах)."""
        self.rotation_angle += radians(angle_deg)
        self.rotation_angle %= (2 * radians(360))