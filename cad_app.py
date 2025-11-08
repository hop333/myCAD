# cad_app.py

import tkinter as tk
from tkinter import simpledialog, colorchooser, messagebox
from math import degrees
from geometry_core import Scene, distance_point_to_segment
from view_transforms import ViewTransform
from cad_view import CADView


class SceneCADApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniCAD")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1e1e1e")

        # МОДЕЛЬ/ЯДРО
        self.scene = Scene()

        # Настройки
        self.coord_system = tk.StringVar(value="cartesian")
        self.angle_unit = tk.StringVar(value="degrees")
        self.tool = tk.StringVar(value="segment")
        self.snap_enabled = tk.BooleanVar(value=False)
        self.segment_color = "#66ccff"

        # Состояние
        self.temp_point = None
        self.drag_start = None
        self.last_mouse_world = (0, 0)

        # --- НАСТРОЙКА UI ---
        self._setup_ui()

        # ЛОГИКА ВИДА (Привязка к холсту и сцене)
        self.trans = ViewTransform(self.canvas, self.scene)
        # ВИЗУАЛИЗАЦИЯ (Привязка к холсту, логике вида и сцене)
        self.view = CADView(self.canvas, self.trans, self.scene)

        # --- ЗАПУСК ---
        self._bind_events()
        self.view.draw_all()
        self.update_status_bar()

    # --- МЕТОДЫ UI И КОНТРОЛЛЕРА ---
    # (методы _create_styled_button и _setup_ui остаются в cad_app.py для управления UI)

    def _create_styled_button(self, parent, text, command, bg="#3a3a3a", fg="white", activebackground="#555555",
                              font_size=9, **kwargs):
        """Создает кнопку со стилем."""
        return tk.Button(parent, text=text, command=command,
                         bg=bg, fg=fg, activebackground=activebackground, activeforeground="white",
                         relief="flat", bd=0, highlightthickness=0,
                         font=("Segoe UI", font_size, "bold"),
                         padx=12, pady=7, **kwargs)

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

        self._create_styled_button(top, text="↺ 15° [L]",
                                   command=lambda: self.rotate_view(15),
                                   bg="#444444").pack(side=tk.LEFT, padx=3)

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
        self.canvas = tk.Canvas(self.root, bg="#121212", highlightthickness=0, bd=0)
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
        self.canvas.bind("<Configure>", lambda e: self.view.draw_all())
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.pan_drag)
        self.canvas.bind("<ButtonRelease-2>", self.end_pan)
        self.canvas.bind("<MouseWheel>", self.on_wheel)
        self.canvas.bind("<Button-4>", lambda e: self.on_wheel(e, 120))
        self.canvas.bind("<Button-5>", lambda e: self.on_wheel(e, -120))

        # Привязка клавиатуры
        self.root.bind("<Control-0>", lambda e: self.zoom_extents())
        self.root.bind("<Escape>", self.cancel_operation)
        self.root.bind("<Key-s>", lambda e: self.set_tool("segment"))
        self.root.bind("<Key-p>", lambda e: self.set_tool("pan"))
        self.root.bind("<Key-d>", lambda e: self.set_tool("delete"))
        self.root.bind("<Key-g>", lambda e: self.toggle_snap())
        self.root.bind("<Control-w>", lambda e: self.clear_scene())
        self.root.bind("<Key-l>", lambda e: self.rotate_view(15))
        self.root.bind("<Key-r>", lambda e: self.rotate_view(-15))
        self.root.bind("<Shift-L>", lambda e: self.rotate_view(90))
        self.root.bind("<Shift-R>", lambda e: self.rotate_view(-90))

    # --- ЛОГИКА ИНСТРУМЕНТОВ/ОПЕРАЦИЙ ---

    def choose_segment_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет фигуры")[1]
        if color_code: self.segment_color = color_code

    def choose_bg_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет фона")[1]
        if color_code:
            self.view.set_bg_color(color_code)
            self.view.draw_all()

    def zoom_extents(self):
        self.trans.zoom_extents()
        self.view.draw_all()
        self.update_status_bar()

    def rotate_view(self, d):
        self.trans.rotate_view(d)
        self.view.draw_all()
        self.update_status_bar()

    def reset_view(self):
        self.trans.rotation_angle = 0
        self.zoom_extents()

    def set_tool(self, t):
        self.tool.set(t)
        self.temp_point = None
        self.view.clear_preview()
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
            self.view.draw_all()

    def cancel_operation(self, e):
        self.temp_point = None
        self.view.clear_preview()
        self.set_tool("segment")

    # --- ОБРАБОТКА ВВОДА ---

    def get_world_coords(self, e):
        """Получает мировые координаты, применяя привязку, если включена."""
        wx, wy = self.trans.canvas_to_world(e.x, e.y)
        if self.snap_enabled.get():
            s = self.trans.grid_step()
            wx, wy = round(wx / s) * s, round(wy / s) * s
        return wx, wy

    def on_mouse_down(self, e):
        self.canvas.focus_set()
        wx, wy = self.get_world_coords(e)

        if self.tool.get() == "segment":
            if not self.temp_point:
                self.temp_point = (wx, wy)
            else:
                self.scene.add_segment(self.temp_point[0], self.temp_point[1], wx, wy, self.segment_color)
                self.temp_point = None
                self.view.clear_preview()
                self.view.draw_all()
                self.update_info()  # Обновляем инспектор

        elif self.tool.get() == "delete":
            for i in range(len(self.scene.segments) - 1, -1, -1):
                s = self.scene.segments[i]
                if distance_point_to_segment(wx, wy, s.x1, s.y1, s.x2, s.y2) < 8 / self.trans.scale:
                    del self.scene.segments[i]
                    self.view.draw_all()
                    self.update_info()
                    break

    def on_mouse_move(self, e):
        wx, wy = self.get_world_coords(e)
        self.last_mouse_world = (wx, wy)
        self.update_status_bar()
        self.canvas.config(cursor="" if self.tool.get() != "pan" else "fleur")  # Обновляем курсор

        if self.tool.get() == "segment" and self.temp_point:
            self.view.draw_preview(self.temp_point, (wx, wy), self.segment_color)

    def on_mouse_drag(self, e):
        if self.tool.get() == "pan": self.pan_drag(e)

    def start_pan(self, e):
        self.drag_start = (e.x, e.y)
        self.canvas.config(cursor="fleur")

    def pan_drag(self, e):
        if not self.drag_start: return
        dx, dy = e.x - self.drag_start[0], e.y - self.drag_start[1]
        self.trans.pan(-dx, -dy)  # Инвертируем смещение
        self.drag_start = (e.x, e.y)
        self.view.draw_all()

    def end_pan(self, e):
        self.drag_start = None
        self.canvas.config(cursor="")

    def on_wheel(self, e, delta=None):
        d = delta if delta else e.delta
        zoom_factor = 1.1 if d > 0 else 0.9
        self.trans.zoom_at_point(zoom_factor, e.x, e.y)
        self.view.draw_all()
        self.update_status_bar()

    def update_status_bar(self):
        wx, wy = self.last_mouse_world
        scale_pct = int((self.trans.scale / self.trans.BASE_SCALE) * 100)
        angle_deg = degrees(self.trans.rotation_angle) % 360
        tools = {'segment': 'Отрезок', 'pan': 'Панорама', 'delete': 'Удаление'}
        active_tool = tools.get(self.tool.get(), self.tool.get())

        status_text = (f"Курсор (X, Y): {wx:.2f}, {wy:.2f}    |    "
                       f"Масштаб: {scale_pct}%    |    "
                       f"Поворот Вида: {angle_deg:.1f}°    |    "
                       f"Активный Инструмент: {active_tool}")
        self.status_bar.config(text=status_text)