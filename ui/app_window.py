import tkinter as tk
from tkinter import ttk, simpledialog, colorchooser, messagebox
from math import sqrt, atan2, degrees
from core.scene import Scene

class SceneCADApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Мини-CAD: Отрезки в координатных системах")

        self.scene = Scene()
        self.coord_system = tk.StringVar(value="cartesian")
        self.angle_unit = tk.StringVar(value="degrees")
        self.segment_color = "#ff0000"
        self.bg_color = "#ffffff"
        self.grid_color = "#e0e0e0"

        self.temp_point = None
        self.preview_line = None
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self.drag_data = None

        self.create_top_controls()
        self.create_vertical_tools()

        self.canvas = tk.Canvas(root, bg=self.bg_color, width=900, height=600)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_info_panel()

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.on_zoom)
        self.canvas.bind("<Button-4>", self.on_zoom)
        self.canvas.bind("<Button-5>", self.on_zoom)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        self.draw_scene()

    # ---------- Интерфейс ----------
    def create_top_controls(self):
        top = tk.Frame(self.root, bg="#e0e0e0", relief=tk.RAISED, bd=2)
        top.pack(side=tk.TOP, fill=tk.X)
        ttk.Radiobutton(top, text="Декартовы", variable=self.coord_system, value="cartesian").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(top, text="Полярные", variable=self.coord_system, value="polar").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(top, text="Градусы", variable=self.angle_unit, value="degrees").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(top, text="Радианы", variable=self.angle_unit, value="radians").pack(side=tk.LEFT, padx=5)

    def create_vertical_tools(self):
        tools = tk.Frame(self.root, bg="#e0e0e0", relief=tk.RAISED, bd=2)
        tools.pack(side=tk.LEFT, fill=tk.Y)
        tk.Button(tools, text="Удалить все", command=self.clear, width=20).pack(pady=5)
        tk.Button(tools, text="Добавить вручную", command=self.manual_input, width=20).pack(pady=5)
        tk.Button(tools, text="Цвет отрезка", command=self.choose_segment_color, width=20).pack(pady=5)
        tk.Button(tools, text="Цвет фона", command=self.choose_bg_color, width=20).pack(pady=5)

    def create_info_panel(self):
        frame = tk.Frame(self.root, relief=tk.SUNKEN, bd=2)
        frame.pack(side=tk.RIGHT, fill=tk.Y)
        tk.Label(frame, text="Информация:").pack()
        self.info = tk.Text(frame, width=35, height=40)
        self.info.pack()

    # ---------- Рисование ----------
    def on_canvas_resize(self, e): self.draw_scene()

    def draw_scene(self):
        c = self.canvas
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        cx, cy = self.world_to_canvas(0, 0)
        self.draw_grid()
        c.create_line(cx, 0, cx, h, fill="black", width=2)
        c.create_line(0, cy, w, cy, fill="black", width=2)
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
        sx = self.offset_x - (w / 2) / self.scale
        ex = self.offset_x + (w / 2) / self.scale
        x = (int(sx // step) + 1) * step
        while x < ex:
            cx_pos, _ = self.world_to_canvas(x, 0)
            c.create_line(cx_pos, cy - 5, cx_pos, cy + 5, fill="black")
            if abs(x) > 1e-5:
                c.create_text(cx_pos, cy + 15, text=f"{x:.0f}", fill="black", font=("Arial", 8))
            x += step

    def adaptive_axis_step(self):
        for s in [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]:
            if s * self.scale > 40:
                return s
        return 1000

    # ---------- Действия ----------
    def on_click(self, e):
        x, y = self.canvas_to_world(e.x, e.y)
        if not self.temp_point:
            self.temp_point = (x, y)
            self.canvas.bind("<Motion>", self.on_motion)
        else:
            x1, y1 = self.temp_point
            if self.coord_system.get() == "polar":
                r = sqrt((x - x1)**2 + (y - y1)**2)
                theta = atan2(y - y1, x - x1)
                if self.angle_unit.get() == "degrees":
                    theta = degrees(theta)
                self.scene.add_segment_polar(x1, y1, r, theta, self.segment_color,
                                              self.angle_unit.get() == "degrees")
            else:
                self.scene.add_segment(x1, y1, x, y, self.segment_color)
            self.temp_point = None
            if self.preview_line:
                self.canvas.delete(self.preview_line)
                self.preview_line = None
            self.canvas.unbind("<Motion>")
            self.draw_scene()
            self.update_info()

    def on_motion(self, e):
        if self.temp_point:
            x1, y1 = self.temp_point
            x2, y2 = self.canvas_to_world(e.x, e.y)
            if self.preview_line:
                self.canvas.delete(self.preview_line)
            cx1, cy1 = self.world_to_canvas(x1, y1)
            cx2, cy2 = self.world_to_canvas(x2, y2)
            self.preview_line = self.canvas.create_line(
                cx1, cy1, cx2, cy2, fill=self.segment_color, dash=(4, 2), width=2
            )

    def on_drag(self, e):
        if not self.drag_data:
            self.drag_data = (e.x, e.y)
        else:
            dx = (e.x - self.drag_data[0]) / self.scale
            dy = (e.y - self.drag_data[1]) / self.scale
            self.offset_x -= dx
            self.offset_y += dy
            self.drag_data = (e.x, e.y)
            self.draw_scene()

    def on_release(self, e): self.drag_data = None

    def on_zoom(self, e):
        f = 1.1 if e.delta > 0 or getattr(e, "num", 0) == 4 else 0.9
        self.scale *= f
        self.draw_scene()

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

    # ---------- Преобразования координат ----------
    def world_to_canvas(self, x, y):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx = w/2 + (x - self.offset_x) * self.scale
        cy = h/2 - (y - self.offset_y) * self.scale
        return cx, cy

    def canvas_to_world(self, cx, cy):
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        x = (cx - w/2)/self.scale + self.offset_x
        y = (h/2 - cy)/self.scale + self.offset_y
        return x, y
