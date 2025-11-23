import tkinter as tk
from tkinter import colorchooser, messagebox
from math import degrees, radians, cos, sin

# Импорты из разделенных файлов
from core.scene import Scene
from core.segment import distance_point_to_segment
from core.view_transforms import ViewTransform
from core.style_manager import StyleManager
from cad_view import CADView
from cad_ui import CADUI


class SceneCADApp(CADUI):
    def __init__(self, root):
        self.root = root
        self.root.title("MiniCAD - Стили по ГОСТ")
        self.root.geometry("1200x700")
        self.root.configure(bg="#1e1e1e")

        self.FALLBACK_W = 760
        self.FALLBACK_H = 630

        # 1. Инициализация менеджера стилей и сцены
        self.style_manager = StyleManager()
        self.scene = Scene(self.style_manager)

        # Глобальные переменные для состояния
        self.angle_unit = tk.StringVar(value="degrees")
        self.tool = tk.StringVar(value="segment")
        self.snap_enabled = tk.BooleanVar(value=False)
        self.segment_color = self.style_manager.get_style(self.style_manager.current_style_name).color

        self.temp_point = None
        self.drag_start = None
        self.last_mouse_world = (0, 0)

        # Ссылки на виджеты (будут заполнены в CADUI.__init__)
        self.canvas = None
        self.status_bar = None
        self.info_text = None
        self.tool_buttons = {}
        self.current_style_var = None
        self.style_combobox = None

        # 2. Настройка UI (через наследованный класс)
        CADUI.__init__(self, root, self)

        # 3. Инициализация View и Transform
        self.trans = ViewTransform(self.canvas, self.scene)
        self.view = CADView(self.canvas, self.trans, self.scene, self.style_manager)

        # 4. Биндинг событий
        self._bind_events()
        self.view.draw_all()
        self.update_status_bar()

    # --- Методы UI и управления состоянием ---

    def _bind_events(self):
        self.canvas.bind("<Configure>", lambda e: self.view.draw_all())
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<Motion>", self.on_mouse_move)

        self.canvas.bind("<Button-3>", self.show_context_menu)

        self.canvas.bind("<Button-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.pan_drag)
        self.canvas.bind("<ButtonRelease-2>", self.end_pan)

        self.canvas.bind("<MouseWheel>", self.on_wheel)
        self.canvas.bind("<Button-4>", lambda e: self.on_wheel(e, 120))
        self.canvas.bind("<Button-5>", lambda e: self.on_wheel(e, -120))

        # Хоткеи
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

    def show_context_menu(self, e):
        menu = tk.Menu(self.root, tearoff=0, bg="#2b2b2b", fg="white")
        menu.add_command(label="Показать все", command=self.zoom_extents)
        menu.add_separator()
        menu.add_command(label="Увеличить", command=self.zoom_in)
        menu.add_command(label="Уменьшить", command=self.zoom_out)
        menu.add_command(label="Панорамирование (P)", command=lambda: self.set_tool("pan"))
        menu.add_separator()
        menu.add_command(label="Повернуть вид ↺", command=lambda: self.rotate_view(15))
        menu.add_command(label="Сбросить вид", command=self.reset_view)

        try:
            menu.tk_popup(e.x_root, e.y_root)
        finally:
            menu.grab_release()

    def open_add_segment_dialog(self):
        """Диалог для добавления отрезка по координатам/длине/углу."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить отрезок")

        window_width = 340
        window_height = 330
        parent_x = self.root.winfo_rootx()
        parent_y = self.root.winfo_rooty()
        parent_width = self.root.winfo_width()
        parent_height = self.root.winfo_height()
        center_x = parent_x + (parent_width // 2) - (window_width // 2)
        center_y = parent_y + (parent_height // 2) - (window_height // 2)
        dialog.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        dialog.configure(bg="#2b2b2b")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        input_mode = tk.StringVar(value="cartesian")
        angle_unit_local = tk.StringVar(value="degrees")

        frame_mode = tk.Frame(dialog, bg="#2b2b2b")
        frame_mode.pack(pady=(15, 5))

        frame_units = tk.Frame(dialog, bg="#2b2b2b")
        labels_refs = {}

        def update_ui_state():
            if input_mode.get() == "cartesian":
                labels_refs["l1"].config(text="X1:")
                labels_refs["l2"].config(text="Y1:")
                labels_refs["l3"].config(text="X2:")
                labels_refs["l4"].config(text="Y2:")
                frame_units.pack_forget()
            else:
                unit_label = "°" if angle_unit_local.get() == "degrees" else "rad"
                labels_refs["l1"].config(text="Старт X:")
                labels_refs["l2"].config(text="Старт Y:")
                labels_refs["l3"].config(text="Длина:")
                labels_refs["l4"].config(text=f"Угол ({unit_label}):")
                frame_units.pack(after=frame_mode, pady=5)

            # Выбор стиля
            style_label = tk.Label(dialog, text=f"Текущий стиль: {self.style_manager.current_style_name}",
                                   bg="#2b2b2b", fg="#cccccc")
            style_label.pack_forget()
            style_label.pack(pady=5)

        tk.Radiobutton(frame_mode, text="2 Точки (X,Y)", variable=input_mode, value="cartesian",
                       command=update_ui_state, bg="#2b2b2b", fg="#cccccc", selectcolor="#4477aa",
                       activebackground="#2b2b2b", activeforeground="white", font=("Segoe UI", 9, "bold")).pack(
            side=tk.LEFT, padx=10)

        tk.Radiobutton(frame_mode, text="Длина / Угол", variable=input_mode, value="length_angle",
                       command=update_ui_state, bg="#2b2b2b", fg="#cccccc", selectcolor="#4477aa",
                       activebackground="#2b2b2b", activeforeground="white", font=("Segoe UI", 9, "bold")).pack(
            side=tk.LEFT, padx=10)

        tk.Label(frame_units, text="Угол в:", bg="#2b2b2b", fg="#888888", font=("Segoe UI", 8)).pack(side=tk.LEFT,
                                                                                                     padx=5)
        tk.Radiobutton(frame_units, text="Градусах", variable=angle_unit_local, value="degrees",
                       command=update_ui_state, bg="#2b2b2b", fg="#cccccc", selectcolor="#555555",
                       activebackground="#2b2b2b", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=2)
        tk.Radiobutton(frame_units, text="Радианах", variable=angle_unit_local, value="radians",
                       command=update_ui_state, bg="#2b2b2b", fg="#cccccc", selectcolor="#555555",
                       activebackground="#2b2b2b", font=("Segoe UI", 8)).pack(side=tk.LEFT, padx=2)

        frame_inputs = tk.Frame(dialog, bg="#2b2b2b")
        frame_inputs.pack(pady=10, padx=20)

        entry_style = {"bg": "#3a3a3a", "fg": "white", "font": ("Consolas", 10), "relief": "flat",
                       "insertbackground": "white"}
        label_style = {"bg": "#2b2b2b", "fg": "#cccccc", "font": ("Segoe UI", 10)}

        entries = {}
        field_ids = ["v1", "v2", "v3", "v4"]

        for i, fid in enumerate(field_ids):
            lbl = tk.Label(frame_inputs, text="", **label_style)
            lbl.grid(row=i, column=0, padx=5, pady=5, sticky="e")
            labels_refs[f"l{i + 1}"] = lbl

            ent = tk.Entry(frame_inputs, width=15, **entry_style)
            ent.grid(row=i, column=1, padx=5, pady=5)
            entries[fid] = ent
            if i == 0: ent.focus_set()

        update_ui_state()

        def on_confirm():
            try:
                v1 = float(entries["v1"].get())
                v2 = float(entries["v2"].get())
                v3 = float(entries["v3"].get())
                v4 = float(entries["v4"].get())

                x1, y1, x2, y2 = 0, 0, 0, 0
                current_style = self.style_manager.current_style_name

                if input_mode.get() == "cartesian":
                    x1, y1, x2, y2 = v1, v2, v3, v4
                else:
                    x1, y1 = v1, v2
                    length = v3
                    angle = v4
                    if angle_unit_local.get() == "degrees":
                        angle = radians(angle)

                    x2 = x1 + length * cos(angle)
                    y2 = y1 + length * sin(angle)

                self.scene.add_segment(x1, y1, x2, y2, current_style)
                self.view.draw_all()
                self.update_info()
                self.zoom_extents()
                dialog.destroy()

            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные числа!", parent=dialog)

        self._create_styled_button(dialog, text="Добавить", command=on_confirm, bg="#4477aa").pack(pady=15)
        dialog.bind('<Return>', lambda e: on_confirm())

    # --- Методы View/Zoom ---

    def _get_reliable_center(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w <= 1 or h <= 1:
            w = self.FALLBACK_W
            h = self.FALLBACK_H
        return w / 2, h / 2

    def zoom_in(self):
        cx, cy = self._get_reliable_center()
        self.trans.zoom_at_point(1.2, cx, cy)
        self.view.draw_all()
        self.update_status_bar()

    def zoom_out(self):
        cx, cy = self._get_reliable_center()
        self.trans.zoom_at_point(0.8, cx, cy)
        self.view.draw_all()
        self.update_status_bar()

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

    # --- Методы Состояния ---

    def choose_segment_color(self):
        """Изменяет цвет для текущего выбранного стиля."""
        color_code = colorchooser.askcolor(title="Выберите цвет для текущего стиля")[1]
        if color_code:
            style_name = self.style_manager.current_style_name
            self.style_manager.update_style(style_name, color=color_code)
            self.segment_color = color_code
            self.view.draw_all()

    def choose_bg_color(self):
        color_code = colorchooser.askcolor(title="Выберите цвет фона")[1]
        if color_code:
            self.view.set_bg_color(color_code)
            self.view.draw_all()

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

    def clear_scene(self, e=None):
        if messagebox.askyesno("Подтверждение", "Очистить все объекты на сцене? (Ctrl+W)"):
            self.scene.clear()
            self.view.draw_all()
            self.update_info()

    def cancel_operation(self, e=None):
        self.temp_point = None
        self.view.clear_preview()
        self.set_tool("segment")

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

    # --- Методы Обработки Мыши ---

    def get_world_coords(self, e):
        wx, wy = self.trans.canvas_to_world(e.x, e.y)
        if self.snap_enabled.get():
            s = self.trans.grid_step()
            wx, wy = round(wx / s) * s, round(wy / s) * s
        return wx, wy

    def on_mouse_down(self, e):
        self.canvas.focus_set()
        wx, wy = self.get_world_coords(e)
        current_style = self.style_manager.current_style_name

        if self.tool.get() == "segment":
            if not self.temp_point:
                self.temp_point = (wx, wy)
            else:
                self.scene.add_segment(self.temp_point[0], self.temp_point[1], wx, wy, current_style)
                self.temp_point = None
                self.view.clear_preview()
                self.view.draw_all()
                self.update_info()

        elif self.tool.get() == "delete":
            tolerance = 8 / self.trans.scale
            for i in range(len(self.scene.segments) - 1, -1, -1):
                s = self.scene.segments[i]
                if distance_point_to_segment(wx, wy, s.x1, s.y1, s.x2, s.y2) < tolerance:
                    del self.scene.segments[i]
                    self.view.draw_all()
                    self.update_info()
                    break

        elif self.tool.get() == "pan":
            self.drag_start = (e.x, e.y)
            self.canvas.config(cursor="fleur")

    def on_mouse_move(self, e):
        wx, wy = self.get_world_coords(e)
        self.last_mouse_world = (wx, wy)
        self.update_status_bar()
        self.canvas.config(cursor="" if self.tool.get() != "pan" else "fleur")

        if self.tool.get() == "segment" and self.temp_point:
            self.view.draw_preview(self.temp_point, (wx, wy), self.style_manager.current_style_name)

    def on_mouse_drag(self, e):
        if self.tool.get() == "pan":
            self.pan_drag(e)

    def start_pan(self, e):
        self.drag_start = (e.x, e.y)
        self.canvas.config(cursor="fleur")

    def pan_drag(self, e):
        if not self.drag_start: return
        dx, dy = e.x - self.drag_start[0], e.y - self.drag_start[1]
        self.trans.pan(dx, dy)
        self.drag_start = (e.x, e.y)
        self.view.draw_all()

    def end_pan(self, e):
        self.drag_start = None
        self.canvas.config(cursor="")
        self.cancel_operation()

    def on_wheel(self, e, delta=None):
        d = delta if delta else e.delta
        zoom_factor = 1.1 if d > 0 else 0.9
        self.trans.zoom_at_point(zoom_factor, e.x, e.y)
        self.view.draw_all()
        self.update_status_bar()