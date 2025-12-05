import tkinter as tk
from math import floor, ceil, sin, pi, hypot

from core.view_transforms import ViewTransform
from core.scene import Scene
from core.style_manager import StyleManager


class CADView:

    def __init__(self, canvas_ref: tk.Canvas, transform_ref: ViewTransform, scene_ref: Scene,
                 style_manager_ref: StyleManager, selection_provider=None):
        self.canvas = canvas_ref
        self.trans = transform_ref
        self.scene = scene_ref
        self.style_manager = style_manager_ref
        self.selection_provider = selection_provider or (lambda: set())
        self.bg_color = "#121212"
        self.grid_color = "#333333"
        self.set_bg_color(self.bg_color)

    def set_bg_color(self, color):
        """Устанавливает цвет фона холста."""
        self.bg_color = color
        self.canvas.config(bg=self.bg_color)

    def draw_all(self):
        """Полная перерисовка сцены (сетка, оси, объекты)."""
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_axes()
        self.draw_labels()
        self.draw_segments()

    def draw_segments(self):
        """Рисует отрезки из сцены, используя данные LineStyle."""
        MM_TO_PIXEL = 3.7795  # 1 мм ≈ 3.78 px при 96 dpi [web:89]

        selected_segments = set(self.selection_provider() or [])

        for s in self.scene.segments:
            style = self.style_manager.get_style(s.style_name)
            if not style:
                continue

            p1 = self.trans.world_to_canvas(s.x1, s.y1)
            p2 = self.trans.world_to_canvas(s.x2, s.y2)

            # --- Толщина: строго по ГОСТ (1 мм и 0.5 мм) ---
            # В StyleManager: "Сплошная основная" = 1.0, остальные = 0.5 мм [web:118][web:121]
            line_width = style.thickness_mm * MM_TO_PIXEL
            line_width = max(1.0, line_width)

            # --- Паттерн штриховки, завязанный на шаг сетки ---
            name_lower = style.name.lower()
            step = self.trans.grid_step()  # 1 шаг = 1 мм в world [web:121]

            override_pattern = None

            if "штриховая" in name_lower:
                # ГОСТ: штрих 2–8 мм, пробел 1–2 мм.
                # Берём среднее: штрих 4 мм, пробел 1.5 мм, в шагах сетки. [web:118]
                override_pattern = (4.0 * step, 1.5 * step)

            elif "штрихпунктирная" in name_lower:
                # ГОСТ: штрих 5–30 мм, пробел 3–5 мм, точка 1–2 мм.
                # Типичный набор: 15 мм штрих, 4 мм пробел, 2 мм точка, 4 мм пробел. [web:118]
                override_pattern = (15.0 * step, 4.0 * step, 2.0 * step, 4.0 * step)

            # Если override_pattern None, берётся dash_pattern из LineStyle.dash_pattern (в шагах = мм)
            dash_pattern = style.get_tk_dash_pattern(self.trans.scale, override_pattern=override_pattern)

            is_selected = s in selected_segments
            if is_selected:
                self.canvas.create_line(
                    p1, p2,
                    fill="#ffd54f",
                    width=line_width + 3,
                    dash=(),
                    tags="segment-selected"
                )

            if "волнистая" in name_lower:
                self._draw_wavy_line(p1, p2, style.color, line_width)
            elif "изломами" in name_lower:
                self._draw_zigzag_line(p1, p2, style.color, line_width)
            else:
                self.canvas.create_line(
                    p1, p2,
                    fill=style.color,
                    width=line_width,
                    dash=dash_pattern,
                    tags="segment"
                )

    def draw_grid(self):
        """Рисует сетку."""
        step = self.trans.grid_step()
        wx1, wy1, wx2, wy2 = self.trans.get_visible_bounds()

        sx, ex = floor(wx1 / step) * step, ceil(wx2 / step) * step
        sy, ey = floor(wy1 / step) * step, ceil(wy2 / step) * step

        # Вертикальные линии
        for x in range(int(sx / step), int(ex / step) + 1):
            p1 = self.trans.world_to_canvas(x * step, sy)
            p2 = self.trans.world_to_canvas(x * step, ey)
            self.canvas.create_line(p1, p2, fill=self.grid_color, tags="grid")

        # Горизонтальные линии
        for y in range(int(sy / step), int(ey / step) + 1):
            p1 = self.trans.world_to_canvas(sx, y * step)
            p2 = self.trans.world_to_canvas(ex, y * step)
            self.canvas.create_line(p1, p2, fill=self.grid_color, tags="grid")

    def draw_axes(self):
        """Рисует оси X и Y."""
        # Ось X (Красная)
        self.canvas.create_line(self.trans.world_to_canvas(-100000, 0), self.trans.world_to_canvas(100000, 0),
                                fill="#774444", width=2, tags="axes")
        # Ось Y (Зеленая)
        self.canvas.create_line(self.trans.world_to_canvas(0, -100000), self.trans.world_to_canvas(0, 100000),
                                fill="#447744", width=2, tags="axes")

        # Метка начала координат
        o = self.trans.world_to_canvas(0, 0)
        self.canvas.create_text(o[0] + 5, o[1] + 5, text="0", fill="#666", anchor="nw", tags="axes")

    def draw_labels(self):
        """Рисует подписи координат осей."""
        step = self.trans.grid_step()
        b = self.trans.get_visible_bounds()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()

        fmt = lambda v: f"{int(round(v))}" if abs(v - round(v)) < 1e-9 else f"{v:.2f}".rstrip("0").rstrip(".")

        # Подписи для оси X
        for x in range(int(floor(b[0] / step)), int(ceil(b[2] / step)) + 1):
            if x == 0: continue
            cx, cy = self.trans.world_to_canvas(x * step, 0)
            if -20 < cx < w + 20 and -20 < cy < h + 20:
                self.canvas.create_text(cx, cy + 15, text=fmt(x * step), fill="#888", font=("Arial", 8))

        # Подписи для оси Y
        for y in range(int(floor(b[1] / step)), int(ceil(b[3] / step)) + 1):
            if y == 0: continue
            cx, cy = self.trans.world_to_canvas(0, y * step)
            if -20 < cx < w + 20 and -20 < cy < h + 20:
                self.canvas.create_text(cx - 25, cy, text=fmt(y * step), fill="#888", font=("Arial", 8), anchor="e")

    def draw_preview(self, w1, w2, style_name):
        """Рисует предварительный (пунктирный) отрезок с учетом стиля."""
        style = self.style_manager.get_style(style_name)
        if not style: return

        MM_TO_PIXEL = 3.7795
        line_width = style.thickness_mm * MM_TO_PIXEL

        p1 = self.trans.world_to_canvas(*w1)
        p2 = self.trans.world_to_canvas(*w2)

        # Для предпросмотра используем тонкую пунктирную линию
        dash_pattern = (8, 4)

        self.canvas.delete("preview")
        self.canvas.create_line(p1, p2,
                                fill=style.color,
                                width=line_width,
                                dash=dash_pattern,
                                tags="preview")

    def clear_preview(self):
        """Удаляет предварительный отрезок."""
        self.canvas.delete("preview")

    def _draw_wavy_line(self, p1, p2, color, width):
        step = self.trans.grid_step()  # 1 шаг = 1 мм
        amplitude_mm = 0.3 * step  # высота волны ≈ 0.3 шага (0.3 мм)
        wavelength_mm = 1.5 * step  # длина волны ≈ 1.5 шага (1.5 мм)

        amplitude = max(3.0, amplitude_mm * 3.7795)
        wavelength = max(10.0, wavelength_mm * 3.7795)

        points = self._generate_wave_points(p1, p2, amplitude=amplitude,
                                            wavelength=wavelength, mode="wave")
        if len(points) >= 4:
            self.canvas.create_line(*points, fill=color, width=width,
                                    smooth=True, splinesteps=12, tags="segment")

    def _draw_zigzag_line(self, p1, p2, color, width):
        step = self.trans.grid_step()
        amplitude_mm = 0.3 * step  # зубец по высоте ≈ 0.3 шага
        wavelength_mm = 1.0 * step  # шаг зигзага ≈ 1 шаг сетки

        amplitude = max(3.0, amplitude_mm * 3.7795)
        wavelength = max(10.0, wavelength_mm * 3.7795)

        points = self._generate_wave_points(p1, p2, amplitude=amplitude,
                                            wavelength=wavelength, mode="zigzag")
        if len(points) >= 4:
            self.canvas.create_line(*points, fill=color, width=width,
                                    smooth=False, tags="segment")

    def _generate_wave_points(self, p1, p2, amplitude, wavelength, mode="wave"):
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        length = hypot(dx, dy)
        if length < 1:
            return [x1, y1, x2, y2]

        ux, uy = dx / length, dy / length
        px, py = -uy, ux

        if mode == "wave":
            periods = max(length / wavelength, 1)
            steps_per_period = 16
            steps = max(int(periods * steps_per_period), 8)
            points = []
            for i in range(steps + 1):
                t = i / steps
                dist = t * length
                base_x = x1 + ux * dist
                base_y = y1 + uy * dist
                phase = 2 * pi * dist / wavelength
                offset = sin(phase) * amplitude
                points.extend([base_x + px * offset, base_y + py * offset])
            return points
        else:
            spacing = max(wavelength, 12)
            points = [x1, y1]
            i = 1
            while True:
                dist = i * spacing
                if dist >= length:
                    break
                base_x = x1 + ux * dist
                base_y = y1 + uy * dist
                points.extend([base_x, base_y])

                offset = amplitude if i % 2 else -amplitude
                kink_x = base_x + px * offset
                kink_y = base_y + py * offset
                points.extend([kink_x, kink_y, base_x, base_y])
                i += 1

            points.extend([x2, y2])
            return points