import tkinter as tk
from tkinter import simpledialog, colorchooser, messagebox
from math import sqrt, atan2, degrees, radians, cos, sin, ceil, floor, log10
import sys


# ==============================================================================
# ЗАГЛУШКА ЯДРА (MOCK CORE)
# ==============================================================================
class Segment:
    _id_counter = 1

    def __init__(self, x1, y1, x2, y2, color="#ff0000"):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.color = color
        self.uid = Segment._id_counter
        Segment._id_counter += 1

    def length(self):
        # ИСПРАВЛЕНИЕ ОШИБКИ: Теперь используется self.x1 и self.y1
        return sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

    def angle(self, in_degrees=True):
        ang = atan2(self.y2 - self.y1, self.x2 - self.x1)
        return degrees(ang) if in_degrees else ang


def polar_to_cartesian(r, theta, degrees_mode=True):
    if degrees_mode: theta = radians(theta)
    return r * cos(theta), r * sin(theta)


class Scene:
    def __init__(self):
        self.segments = []

    def add_segment(self, x1, y1, x2, y2, color="#ff0000"):
        self.segments.append(Segment(x1, y1, x2, y2, color))

    def add_segment_polar(self, x1, y1, r, theta, color="#ff0000", degrees_mode=True):
        dx, dy = polar_to_cartesian(r, theta, degrees_mode)
        self.segments.append(Segment(x1, y1, x1 + dx, y1 + dy, color))

    def clear(self):
        self.segments.clear()

    def describe(self, degrees_mode=True):
        if not self.segments:
            return "Сцена пуста."
        info = ""
        for seg in self.segments:
            # ИСПРАВЛЕНИЕ: Исправлена опечатка в имени переменной seg2.y2 на seg.y2
            info += (f"➤ Отрезок [{seg.uid}]\n"
                     f"   ({seg.x1:.1f}, {seg.y1:.1f}) → ({seg.x2:.1f}, {seg.y2:.1f})\n"
                     f"   L={seg.length():.2f}, ∠={seg.angle(degrees_mode):.1f}°\n\n")
        return info


# ==============================================================================
# ГЛАВНОЕ ПРИЛОЖЕНИЕ (MAIN APPLICATION)
# ==============================================================================

def distance_point_to_segment(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0: return sqrt((px - x1) ** 2 + (py - y1) ** 2)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    return sqrt((px - (x1 + t * dx)) ** 2 + (py - (y1 + t * dy)) ** 2)


class SceneCADApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniCAD Modern Dark Refined")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1e1e1e")

        self.scene = Scene()

        # Параметры Вида
        self.BASE_SCALE = 20.0  # Уменьшенный масштаб по умолчанию
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.scale = self.BASE_SCALE
        self.rotation_angle = 0.0

        # Настройки
        self.coord_system = tk.StringVar(value="cartesian")
        self.angle_unit = tk.StringVar(value="degrees")
        self.tool = tk.StringVar(value="segment")
        self.snap_enabled = tk.BooleanVar(value=False)
        self.segment_color = "#66ccff"
        self.bg_color = "#121212"
        self.grid_color = "#333333"

        # Состояние
        self.temp_point = None
        self.drag_start = None
        self.last_mouse_world = (0, 0)

        self._setup_ui()
        self._bind_events()
        self.draw()
        self.update_status_bar()

    def _create_styled_button(self, parent, text, command, bg="#3a3a3a", fg="white", activebackground="#555555",
                              font_size=9, **kwargs):
        """Создает кнопку со скругленным (за счет padding) плоским стилем."""
        return tk.Button(parent, text=text, command=command,
                         bg=bg, fg=fg,
                         activebackground=activebackground,
                         activeforeground="white",
                         relief="flat", bd=0, highlightthickness=0,
                         font=("Segoe UI", font_size, "bold"),
                         padx=12, pady=7,  # Увеличенный отступ для "скругленного" эффекта
                         **kwargs)

    def _setup_ui(self):
        # --- ВЕРХНЯЯ ПАНЕЛЬ (Top Bar) ---
        top = tk.Frame(self.root, bg="#2b2b2b", height=40, bd=0, relief="flat")
        top.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Радио-кнопки
        for text, var, val in [("Декартовы", self.coord_system, "cartesian"),
                               ("Полярные", self.coord_system, "polar"),
                               ("Градусы (°)", self.angle_unit, "degrees"),
                               ("Радианы (rad)", self.angle_unit, "radians")]:
            tk.Radiobutton(top, text=text, variable=var, value=val,
                           bg="#3a3a3a", fg="#cccccc",
                           selectcolor="#4477aa",
                           activebackground="#555555",
                           activeforeground="white",
                           font=("Segoe UI", 9, "bold"),
                           indicatoron=0,
                           relief="flat", bd=0, highlightthickness=0,
                           padx=12, pady=7).pack(side=tk.LEFT, padx=3)

        tk.Label(top, text="•", bg="#2b2b2b", fg="#555").pack(side=tk.LEFT, padx=10)

        # Кнопки Управления Видом
        self._create_styled_button(top, text="Подогнать Вид [Ctrl+0]", command=self.zoom_extents,
                                   bg="#444444").pack(side=tk.LEFT, padx=3)

        # --- Кнопка Поворот Против часовой (↺) ---
        # Кнопка всегда поворачивает на 15 градусов
        self._create_styled_button(top, text="↺ 15° [L]",
                                   command=lambda: self.rotate_view(15),
                                   bg="#444444").pack(side=tk.LEFT, padx=3)

        # --- Кнопка Поворот По часовой (↻) ---
        # Кнопка всегда поворачивает на -15 градусов
        self._create_styled_button(top, text="↻ 15° [R]",
                                   command=lambda: self.rotate_view(-15),
                                   bg="#444444").pack(side=tk.LEFT, padx=3)

        self._create_styled_button(top, text="Сброс Вида", command=self.reset_view).pack(side=tk.LEFT, padx=3)

        # --- СТРОКА СОСТОЯНИЯ (Status Bar) ---
        self.status_bar = tk.Label(self.root, text="", bd=0, relief=tk.FLAT, anchor=tk.W,
                                   bg="#3a3a3a", fg="#cccccc", font=("Segoe UI", 9), padx=10, pady=2)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- БОКОВАЯ ПАНЕЛЬ (Sidebar) ---
        sidebar = tk.Frame(self.root, bg="#2b2b2b", width=180, bd=0, relief="flat")
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        sidebar.pack_propagate(False)

        # Кнопки Инструментов
        self.tool_buttons = {}
        for tool_name, text, key in [("segment", "✏️ Отрезок [S]", "s"),
                                     ("pan", "🖐 Панорама [P]", "p"),
                                     ("delete", "🗑 Удалить Объект [D]", "d")]:
            btn = self._create_styled_button(sidebar, text=text, command=lambda t=tool_name: self.set_tool(t),
                                             bg="#3a3a3a", font_size=10, height=1)
            btn.pack(fill=tk.X, pady=4, padx=8)
            self.tool_buttons[tool_name] = btn
        self.update_tool_buttons()

        # Настройки цвета
        self._create_styled_button(sidebar, text="🎨 Цвет фигуры", command=self.choose_segment_color,
                                   bg="#444444").pack(fill=tk.X, pady=(15, 4), padx=8)
        self._create_styled_button(sidebar, text="🌄 Цвет Фона", command=self.choose_bg_color,
                                   bg="#444444").pack(fill=tk.X, pady=4, padx=8)

        # Привязка к Сетке
        self.snap_check = tk.Checkbutton(sidebar, text="Привязка к Сетке [G]", variable=self.snap_enabled,
                                         bg="#2b2b2b", fg="white",
                                         selectcolor="#4477aa",
                                         activebackground="#2b2b2b",
                                         font=("Segoe UI", 10),
                                         bd=0, highlightthickness=0,
                                         padx=8, pady=5,
                                         anchor="w")
        self.snap_check.pack(fill=tk.X, pady=(10, 5), padx=8)

        # Кнопка Очистки (Красная, акцентная)
        self._create_styled_button(sidebar, text="ОЧИСТИТЬ ВСЕ [Ctrl+W]", command=self.clear_scene,
                                   bg="#993333", activebackground="#aa5555", fg="white", font_size=10).pack(fill=tk.X,
                                                                                                            pady=(10,
                                                                                                                  20),
                                                                                                            padx=8)

        # --- ХОЛСТ (Canvas) ---
        self.canvas = tk.Canvas(self.root, bg=self.bg_color, highlightthickness=0, bd=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- ПАНЕЛЬ ИНФОРМАЦИИ (Inspector Panel) ---
        info_frame = tk.Frame(self.root, bg="#252526", width=250, bd=0, relief="flat")
        info_frame.pack(side=tk.RIGHT, fill=tk.Y)
        info_frame.pack_propagate(False)

        tk.Label(info_frame, text="ИНСПЕКТОР ОБЪЕКТОВ", bg="#333333", fg="#cccccc", font=("Segoe UI", 9, "bold"),
                 anchor="w", padx=10, pady=5).pack(fill=tk.X)

        self.info_text = tk.Text(info_frame, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 9),
                                 bd=0, highlightthickness=0, wrap=tk.WORD, state=tk.DISABLED)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)

        sb = tk.Scrollbar(info_frame, command=self.info_text.yview, bg="#252526", troughcolor="#1e1e1e", borderwidth=0)
        sb.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        self.info_text.config(yscrollcommand=sb.set)

    def _bind_events(self):
        self.canvas.bind("<Configure>", lambda e: self.draw())
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.pan_drag)
        self.canvas.bind("<ButtonRelease-2>", self.end_pan)
        self.canvas.bind("<MouseWheel>", self.on_wheel)
        self.canvas.bind("<Button-4>", lambda e: self.on_wheel(e, 120))
        self.canvas.bind("<Button-5>", lambda e: self.on_wheel(e, -120))

        # --- КЛАВИШИ (Остаются без изменений: 15° и Shift+90°) ---
        self.root.bind("<Control-0>", lambda e: self.zoom_extents())
        self.root.bind("<Escape>", self.cancel_operation)
        self.root.bind("<Key-s>", lambda e: self.set_tool("segment"))
        self.root.bind("<Key-p>", lambda e: self.set_tool("pan"))
        self.root.bind("<Key-d>", lambda e: self.set_tool("delete"))
        self.root.bind("<Key-g>", lambda e: self.toggle_snap())
        self.root.bind("<Control-w>", lambda e: self.clear_scene())

        # 15 градусов (R и L)
        self.root.bind("<Key-l>", lambda e: self.rotate_view(15))
        self.root.bind("<Key-r>", lambda e: self.rotate_view(-15))

        # 90 градусов (Shift + R и Shift + L)
        self.root.bind("<Shift-L>", lambda e: self.rotate_view(90))
        self.root.bind("<Shift-R>", lambda e: self.rotate_view(-90))

    # ==========================================================================
    # ТРАНСФОРМАЦИИ И ДЕЙСТВИЯ НАД ОБЪЕКТАМИ
    # ==========================================================================

    def world_to_canvas(self, wx, wy):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = w / 2.0, h / 2.0
        tx, ty = wx - self.offset_x, wy - self.offset_y
        ca, sa = cos(self.rotation_angle), sin(self.rotation_angle)
        return cx + (tx * ca + ty * sa) * self.scale, cy - (-tx * sa + ty * ca) * self.scale

    def canvas_to_world(self, cx, cy):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        rx, ry = (cx - w / 2.0) / self.scale, (h / 2.0 - cy) / self.scale
        ca, sa = cos(-self.rotation_angle), sin(-self.rotation_angle)
        return rx * ca + ry * sa + self.offset_x, -rx * sa + ry * ca + self.offset_y

    def get_visible_bounds(self):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        pts = [self.canvas_to_world(0, 0), self.canvas_to_world(w, 0),
               self.canvas_to_world(w, h), self.canvas_to_world(0, h)]
        return min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)

    def draw(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_axes()
        self.draw_labels()
        for s in self.scene.segments:
            p1, p2 = self.world_to_canvas(s.x1, s.y1), self.world_to_canvas(s.x2, s.y2)
            self.canvas.create_line(p1, p2, fill=s.color, width=3, smooth=True, caps=tk.ROUND, tags="segment")
        self.update_info()

    def draw_grid(self):
        step = self.grid_step()
        wx1, wy1, wx2, wy2 = self.get_visible_bounds()
        sx, ex = floor(wx1 / step) * step, ceil(wx2 / step) * step
        sy, ey = floor(wy1 / step) * step, ceil(wy2 / step) * step
        for x in range(int(sx / step), int(ex / step) + 1):
            p1, p2 = self.world_to_canvas(x * step, sy), self.world_to_canvas(x * step, ey)
            self.canvas.create_line(p1, p2, fill=self.grid_color, tags="grid")
        for y in range(int(sy / step), int(ey / step) + 1):
            p1, p2 = self.world_to_canvas(sx, y * step), self.world_to_canvas(ex, y * step)
            self.canvas.create_line(p1, p2, fill=self.grid_color, tags="grid")

    def draw_axes(self):
        b = self.get_visible_bounds()
        inf = max(abs(x) for x in b) * 2 + 1000
        self.canvas.create_line(self.world_to_canvas(-inf, 0), self.world_to_canvas(inf, 0), fill="#774444", width=2)
        self.canvas.create_line(self.world_to_canvas(0, -inf), self.world_to_canvas(0, inf), fill="#447744", width=2)
        o = self.world_to_canvas(0, 0)
        self.canvas.create_text(o[0] + 5, o[1] + 5, text="0", fill="#666", anchor="nw")

    def draw_labels(self):
        step = self.grid_step()
        b = self.get_visible_bounds()
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        fmt = lambda v: f"{int(round(v))}" if abs(v - round(v)) < 1e-9 else f"{v:.2f}".rstrip("0").rstrip(".")

        for x in range(int(floor(b[0] / step)), int(ceil(b[2] / step)) + 1):
            if x == 0: continue
            cx, cy = self.world_to_canvas(x * step, 0)
            if -20 < cx < w + 20 and -20 < cy < h + 20:
                self.canvas.create_text(cx, cy + 15, text=fmt(x * step), fill="#888", font=("Arial", 8))
        for y in range(int(floor(b[1] / step)), int(ceil(b[3] / step)) + 1):
            if y == 0: continue
            cx, cy = self.world_to_canvas(0, y * step)
            if -20 < cx < w + 20 and -20 < cy < h + 20:
                self.canvas.create_text(cx - 25, cy, text=fmt(y * step), fill="#888", font=("Arial", 8), anchor="e")

    def grid_step(self):
        target = 100 / self.scale
        # Использование log10 для определения порядка величины шага
        p10 = 10 ** floor(log10(target) if target > 0 else 0)
        m = target / p10
        return (1 * p10) if m < 2 else (2 * p10) if m < 5 else (5 * p10)

    # ==========================================================================
    # ИНСТРУМЕНТЫ
    # ==========================================================================

    def choose_segment_color(self):
        """Открывает диалог выбора цвета для новых отрезков."""
        color_code = colorchooser.askcolor(title="Выберите цвет фигуры")[1]
        if color_code:
            self.segment_color = color_code

    def choose_bg_color(self):
        """Открывает диалог выбора цвета для фона холста."""
        color_code = colorchooser.askcolor(title="Выберите цвет фона")[1]
        if color_code:
            self.bg_color = color_code
            self.canvas.config(bg=self.bg_color)
            self.draw()

    # ==========================================================================
    # ВЗАИМОДЕЙСТВИЕ
    # ==========================================================================
    def on_mouse_down(self, e):
        self.canvas.focus_set()
        wx, wy = self.canvas_to_world(e.x, e.y)
        if self.tool.get() == "pan":
            self.start_pan(e)
            return
        if self.snap_enabled.get():
            s = self.grid_step()
            wx, wy = round(wx / s) * s, round(wy / s) * s
        if self.tool.get() == "segment":
            if not self.temp_point:
                self.temp_point = (wx, wy)
            else:
                self.scene.add_segment(self.temp_point[0], self.temp_point[1], wx, wy, self.segment_color)
                self.temp_point = None
                self.canvas.delete("preview")
                self.draw()
        elif self.tool.get() == "delete":
            for i in range(len(self.scene.segments) - 1, -1, -1):
                s = self.scene.segments[i]
                if distance_point_to_segment(wx, wy, s.x1, s.y1, s.x2, s.y2) < 8 / self.scale:
                    del self.scene.segments[i]
                    self.draw()
                    break

    def on_mouse_move(self, e):
        wx, wy = self.canvas_to_world(e.x, e.y)
        self.last_mouse_world = (wx, wy)
        self.update_status_bar()

        if self.tool.get() == "segment" and self.temp_point:
            if self.snap_enabled.get():
                s = self.grid_step()
                wx, wy = round(wx / s) * s, round(wy / s) * s
            p1 = self.world_to_canvas(*self.temp_point)
            p2 = self.world_to_canvas(wx, wy)
            self.canvas.delete("preview")
            self.canvas.create_line(p1, p2, fill=self.segment_color, width=3, dash=(8, 4), tags="preview")

    def update_status_bar(self):
        wx, wy = self.last_mouse_world
        scale_pct = int((self.scale / self.BASE_SCALE) * 100)
        angle_deg = degrees(self.rotation_angle) % 360
        tools = {'segment': 'Отрезок', 'pan': 'Панорама', 'delete': 'Удаление'}
        active_tool = tools.get(self.tool.get(), self.tool.get())

        status_text = (f"Курсор (X, Y): {wx:.2f}, {wy:.2f}    |    "
                       f"Масштаб: {scale_pct}%    |    "
                       f"Поворот Вида: {angle_deg:.1f}°    |    "
                       f"Активный Инструмент: {active_tool}")
        self.status_bar.config(text=status_text)

    def on_mouse_up(self, e):
        pass

    def on_mouse_drag(self, e):
        if self.tool.get() == "pan": self.pan_drag(e)

    def start_pan(self, e):
        self.drag_start = (e.x, e.y)
        self.canvas.config(cursor="fleur")

    def pan_drag(self, e):
        if not self.drag_start: return
        w1, w2 = self.canvas_to_world(*self.drag_start), self.canvas_to_world(e.x, e.y)
        self.offset_x -= (w2[0] - w1[0])
        self.offset_y -= (w2[1] - w1[1])
        self.drag_start = (e.x, e.y)
        self.draw()

    def end_pan(self, e):
        self.drag_start = None
        self.canvas.config(cursor="")

    def on_wheel(self, e, delta=None):
        d = delta if delta else e.delta
        w1 = self.canvas_to_world(e.x, e.y)
        self.scale = max(0.01, min(self.scale * (1.1 if d > 0 else 0.9), 10000.0))
        w2 = self.canvas_to_world(e.x, e.y)
        self.offset_x += (w1[0] - w2[0])
        self.offset_y += (w1[1] - w2[1])
        self.draw()
        self.update_status_bar()

    def rotate_view(self, d):
        self.rotation_angle += radians(d)
        self.draw()
        self.update_status_bar()

    def reset_view(self):
        self.rotation_angle = 0
        self.zoom_extents()

    def zoom_extents(self):
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

        self.draw()
        self.update_status_bar()

    def set_tool(self, t):
        self.tool.set(t)
        self.temp_point = None
        self.canvas.delete("preview")
        self.update_tool_buttons()
        self.update_status_bar()

    def toggle_snap(self):
        self.snap_enabled.set(not self.snap_enabled.get())

    def update_tool_buttons(self):
        for n, b in self.tool_buttons.items():
            b.config(bg="#4477aa" if n == self.tool.get() else "#3a3a3a",
                     relief="flat",
                     font=("Segoe UI", 10, "bold" if n == self.tool.get() else "normal"),
                     fg="white" if n == self.tool.get() else "#cccccc")

    def update_info(self):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(tk.END, self.scene.describe(self.angle_unit.get() == "degrees"))
        self.info_text.config(state=tk.DISABLED)

    def clear_scene(self):
        if messagebox.askyesno("Подтверждение", "Очистить все объекты на сцене? (Ctrl+W)"):
            self.scene.clear()
            self.draw()

    def cancel_operation(self, e):
        self.temp_point = None
        self.canvas.delete("preview")
        self.set_tool("segment")
        self.update_status_bar()


def np_log10(v): return log10(v) if v > 0 else 0


if __name__ == "__main__":
    root = tk.Tk()
    app = SceneCADApp(root)
    root.mainloop()