import tkinter as tk
from tkinter import simpledialog, colorchooser, messagebox
from math import sqrt, atan2, degrees
from core.scene import Scene

def distance_point_to_segment(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return sqrt((px - x1)**2 + (py - y1)**2)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy
    return sqrt((px - nearest_x)**2 + (py - nearest_y)**2)

class SceneCADApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MiniCAD Modern Dark")
        self.root.geometry("1200x700")
        self.root.configure(bg="#222222")

        # Core
        self.scene = Scene()
        self.coord_system = tk.StringVar(value="cartesian")
        self.angle_unit = tk.StringVar(value="degrees")
        self.segment_color = "#ff4b4b"
        self.bg_color = "#1c1c1c"
        self.grid_color = "#333333"

        self.temp_point = None
        self.preview_line = None
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self.drag_data = None

        self.tool = tk.StringVar(value="segment")  # segment/pan/delete
        self.snap_enabled = tk.BooleanVar(value=False)

        # UI
        self.create_top_controls()
        self.create_sidebar()
        self.create_canvas()
        self.create_info_panel()
        self.bind_events()
        self.draw_scene()

    # ---------- Верхняя панель ----------
    def create_top_controls(self):
        top = tk.Frame(self.root, bg="#2b2b2b", height=40)
        top.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Radiobutton(top, text="Декартовы", variable=self.coord_system, value="cartesian",
                       bg="#2b2b2b", fg="white", selectcolor="#444444", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=6)
        tk.Radiobutton(top, text="Полярные", variable=self.coord_system, value="polar",
                       bg="#2b2b2b", fg="white", selectcolor="#444444", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=6)
        tk.Radiobutton(top, text="Градусы", variable=self.angle_unit, value="degrees",
                       bg="#2b2b2b", fg="white", selectcolor="#444444", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=6)
        tk.Radiobutton(top, text="Радианы", variable=self.angle_unit, value="radians",
                       bg="#2b2b2b", fg="white", selectcolor="#444444", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=6)

    # ---------- Боковая панель ----------
    def create_sidebar(self):
        sidebar = tk.Frame(self.root, bg="#2b2b2b", width=180)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        # Инструменты
        self.btn_segment = tk.Button(sidebar, text="✏️ Отрезок", command=lambda: self.select_tool("segment"),
                                     bg="#3a3a3a", fg="white", relief="flat", font=("Segoe UI", 10))
        self.btn_segment.pack(pady=4, fill=tk.X)

        self.btn_pan = tk.Button(sidebar, text="🖐 Перемещение", command=lambda: self.select_tool("pan"),
                                 bg="#3a3a3a", fg="white", relief="flat", font=("Segoe UI", 10))
        self.btn_pan.pack(pady=4, fill=tk.X)

        self.btn_delete = tk.Button(sidebar, text="🗑 Удалить отрезок", command=lambda: self.select_tool("delete"),
                                    bg="#3a3a3a", fg="white", relief="flat", font=("Segoe UI", 10))
        self.btn_delete.pack(pady=4, fill=tk.X)

        self.snap_btn = tk.Checkbutton(sidebar, text="Привязка к сетке", variable=self.snap_enabled,
                                       bg="#2b2b2b", fg="white", selectcolor="#2b2b2b", font=("Segoe UI", 10))
        self.snap_btn.pack(pady=6)

        tk.Frame(sidebar, height=2, bg="#444444").pack(fill=tk.X, pady=6)

        # Действия
        for text, cmd in [("Удалить все", self.clear),
                          ("Добавить вручную", self.manual_input),
                          ("Цвет отрезка", self.choose_segment_color),
                          ("Цвет фона", self.choose_bg_color)]:
            tk.Button(sidebar, text=text, command=cmd, bg="#3a3a3a", fg="white",
                      relief="flat", font=("Segoe UI", 10)).pack(pady=3, fill=tk.X)

        self.update_tool_buttons()

    def select_tool(self, tool_name):
        self.tool.set(tool_name)
        self.temp_point = None
        if self.preview_line:
            self.canvas.delete(self.preview_line)
            self.preview_line = None
        self.canvas.unbind("<Motion>")
        self.update_tool_buttons()

    def update_tool_buttons(self):
        self.btn_segment.config(bg="#4caf4c" if self.tool.get()=="segment" else "#3a3a3a")
        self.btn_pan.config(bg="#4c79ff" if self.tool.get()=="pan" else "#3a3a3a")
        self.btn_delete.config(bg="#ff5555" if self.tool.get()=="delete" else "#3a3a3a")

    # ---------- Canvas ----------
    def create_canvas(self):
        self.canvas = tk.Canvas(self.root, bg=self.bg_color)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # ---------- Правая панель ----------
    def create_info_panel(self):
        frame = tk.Frame(self.root, bg="#2b2b2b", width=220)
        frame.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        tk.Label(frame, text="Информация:", bg="#2b2b2b", fg="white", font=("Segoe UI", 10)).pack()
        self.info = tk.Text(frame, width=28, height=40, bg="#1c1c1c", fg="white", font=("Segoe UI", 10))
        self.info.pack(pady=5)

    # ---------- События ----------
    def bind_events(self):
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)
        self.canvas.bind("<Configure>", lambda e: self.draw_scene())

    # ---------- Методы ----------
    def on_click(self, e):
        x, y = self.canvas_to_world(e.x, e.y)
        step = self.adaptive_axis_step()

        if self.snap_enabled.get():
            x = round(x / step) * step
            y = round(y / step) * step

        if self.tool.get() == "segment":
            if not self.temp_point:
                self.temp_point = (x, y)
                self.canvas.bind("<Motion>", self.on_motion)
            else:
                x1, y1 = self.temp_point
                self.scene.add_segment(x1, y1, x, y, self.segment_color)
                self.temp_point = None
                if self.preview_line:
                    self.canvas.delete(self.preview_line)
                    self.preview_line = None
                self.canvas.unbind("<Motion>")
                self.draw_scene()
                self.update_info()
        elif self.tool.get() == "delete":
            threshold = 5 / self.scale
            for seg in self.scene.segments:
                if distance_point_to_segment(x, y, seg.x1, seg.y1, seg.x2, seg.y2) < threshold:
                    seg.deleted = True
                    break
            self.scene.segments = [s for s in self.scene.segments if not getattr(s, "deleted", False)]
            self.draw_scene()
            self.update_info()

    def on_motion(self, e):
        if self.temp_point and self.tool.get() == "segment":
            x1, y1 = self.temp_point
            x2, y2 = self.canvas_to_world(e.x, e.y)
            if self.snap_enabled.get():
                step = self.adaptive_axis_step()
                x2 = round(x2 / step) * step
                y2 = round(y2 / step) * step
            if self.preview_line:
                self.canvas.delete(self.preview_line)
            cx1, cy1 = self.world_to_canvas(x1, y1)
            cx2, cy2 = self.world_to_canvas(x2, y2)
            self.preview_line = self.canvas.create_line(cx1, cy1, cx2, cy2,
                                                        fill=self.segment_color, dash=(4, 2), width=2)

    # Здесь вставляем остальные методы: draw_scene, draw_grid, draw_axis_labels, adaptive_axis_step, on_drag, on_release, on_zoom, world_to_canvas, canvas_to_world, clear, manual_input, choose_segment_color, choose_bg_color, update_info

    def on_drag(self, e):
        if self.tool.get() != "pan":
            return
        if not self.drag_data:
            self.drag_data = (e.x, e.y)
        else:
            dx = (e.x - self.drag_data[0]) / self.scale
            dy = (e.y - self.drag_data[1]) / self.scale
            self.offset_x -= dx
            self.offset_y += dy
            self.drag_data = (e.x, e.y)
            self.draw_scene()

    def on_release(self, e):
        self.drag_data = None

    def on_zoom(self, e):
        f = 1.1 if e.delta > 0 or getattr(e, "num", 0) == 4 else 0.9
        self.scale *= f
        self.draw_scene()

    # ---------- Рисование ----------
    def draw_scene(self):
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        cx, cy = self.world_to_canvas(0, 0)
        self.draw_grid()
        c.create_line(cx, 0, cx, h, fill="white", width=2)
        c.create_line(0, cy, w, cy, fill="white", width=2)
        self.draw_axis_labels(cx, cy)
        for s in self.scene.segments:
            x1, y1 = self.world_to_canvas(s.x1, s.y1)
            x2, y2 = self.world_to_canvas(s.x2, s.y2)
            c.create_line(x1, y1, x2, y2, fill=s.color, width=2)

    def draw_grid(self):
        c = self.canvas
        w, h = c.winfo_width(), c.winfo_height()
        step = self.adaptive_axis_step()
        start_x = self.offset_x - (w / 2) / self.scale
        end_x = self.offset_x + (w / 2) / self.scale
        start_y = self.offset_y - (h / 2) / self.scale
        end_y = self.offset_y + (h / 2) / self.scale

        x = (int(start_x // step) + 1) * step
        while x < end_x:
            cx, _ = self.world_to_canvas(x, 0)
            c.create_line(cx, 0, cx, h, fill=self.grid_color)
            x += step

        y = (int(start_y // step) + 1) * step
        while y < end_y:
            _, cy = self.world_to_canvas(0, y)
            c.create_line(0, cy, w, cy, fill=self.grid_color)
            y += step

    def draw_axis_labels(self, cx, cy):
        c = self.canvas
        w, h = c.winfo_width(), c.winfo_height()
        step = self.adaptive_axis_step()

        # X
        sx = self.offset_x - (w / 2) / self.scale
        ex = self.offset_x + (w / 2) / self.scale
        x = (int(sx // step) + 1) * step
        while x < ex:
            cx_pos, _ = self.world_to_canvas(x, 0)
            c.create_line(cx_pos, cy - 5, cx_pos, cy + 5, fill="white")
            if abs(x) > 1e-5:
                c.create_text(cx_pos, cy + 15, text=f"{x:.0f}", fill="white", font=("Arial", 8))
            x += step

        # Y
        sy = self.offset_y - (h / 2) / self.scale
        ey = self.offset_y + (h / 2) / self.scale
        y = (int(sy // step) + 1) * step
        while y < ey:
            _, cy_pos = self.world_to_canvas(0, y)
            c.create_line(cx - 5, cy_pos, cx + 5, cy_pos, fill="white")
            if abs(y) > 1e-5:
                c.create_text(cx - 15, cy_pos, text=f"{y:.0f}", fill="white", font=("Arial", 8))
            y += step

    def adaptive_axis_step(self):
        for s in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]:
            if s * self.scale > 40:
                return s
        return 1000

    # ---------- Преобразования ----------
    def world_to_canvas(self, x, y):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx = w / 2 + (x - self.offset_x) * self.scale
        cy = h / 2 - (y - self.offset_y) * self.scale
        return cx, cy

    def canvas_to_world(self, cx, cy):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        x = (cx - w / 2) / self.scale + self.offset_x
        y = (h / 2 - cy) / self.scale + self.offset_y
        return x, y

    # ---------- Утилиты ----------
    def clear(self):
        self.scene.clear()
        self.draw_scene()
        self.update_info()

    def manual_input(self):
        if self.coord_system.get() == "cartesian":
            prompt = "Введите x1,y1,x2,y2 через запятую:"
        else:
            prompt = "Введите x1,y1,r,θ через запятую:"
        coords = simpledialog.askstring("Новый отрезок", prompt)
        if not coords: return
        try:
            vals = list(map(float, coords.split(",")))
            if self.coord_system.get() == "cartesian":
                x1, y1, x2, y2 = vals
                self.scene.add_segment(x1, y1, x2, y2, self.segment_color)
            else:
                x1, y1, r, t = vals
                self.scene.add_segment_polar(x1, y1, r, t, self.segment_color,
                                             self.angle_unit.get() == "degrees")
            self.draw_scene()
            self.update_info()
        except Exception:
            messagebox.showerror("Ошибка", "Неверный формат ввода")

    def choose_segment_color(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.segment_color = c

    def choose_bg_color(self):
        c = colorchooser.askcolor()[1]
        if c:
            self.bg_color = c
            self.canvas.config(bg=c)
            self.draw_scene()

    def update_info(self):
        self.info.delete(1.0, tk.END)
        self.info.insert(tk.END, self.scene.describe(self.angle_unit.get() == "degrees"))
