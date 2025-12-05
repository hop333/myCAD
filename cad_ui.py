import tkinter as tk
from tkinter import colorchooser, messagebox, ttk
from math import sin, pi


class CADUI:
    """Класс для построения пользовательского интерфейса Tkinter.
    SceneCADApp наследует этот класс для получения ссылок на виджеты."""

    def __init__(self, root, app_ref):
        self.app = app_ref
        self._setup_ui(root)
        # Дополнительная инициализация
        self.app.style_combobox.set(self.app.style_manager.current_style_name)
        self.update_current_style_ui()

    def _create_styled_button(self, parent, text, command, bg="#3a3a3a", fg="white", activebackground="#555555",
                              font_size=9, **kwargs):
        """Создает кнопку со стилем."""
        if "padx" not in kwargs:
            kwargs["padx"] = 12
        if "pady" not in kwargs:
            kwargs["pady"] = 7
        return tk.Button(parent, text=text, command=command,
                         bg=bg, fg=fg, activebackground=activebackground, activeforeground="white",
                         relief="flat", bd=0, highlightthickness=0,
                         font=("Segoe UI", font_size, "bold"),
                         **kwargs)

    def render_style_preview(self, canvas, style):
        """Рисует визуальный образец линии на указанном Canvas."""
        if not canvas:
            return
        canvas.delete("all")
        try:
            width = int(canvas.cget("width"))
        except Exception:
            width = canvas.winfo_width()
        try:
            height = int(canvas.cget("height"))
        except Exception:
            height = canvas.winfo_height()
        if width <= 0: width = 120
        if height <= 0: height = 22

        margin = 10
        baseline = height // 2 + 5

        # фон карточки предпросмотра
        canvas.create_rectangle(0, 0, width, height, fill="#1b1b1b", outline="#2c2c2c")
        canvas.create_line(margin, baseline + 2, width - margin, baseline + 2, fill="#2f2f2f")

        if not style:
            canvas.create_line(margin, baseline - 5, width - margin, baseline - 5,
                               fill="#5a5a5a", width=2, dash=(6, 4))
            canvas.create_text(width // 2, baseline - 8, text="нет стиля",
                               fill="#888888", font=("Segoe UI", 8, "italic"))
            return

        # цветовой маркер
        chip_radius = 5
        chip_x = margin - 4
        chip_y = baseline - 6
        canvas.create_oval(chip_x - chip_radius, chip_y - chip_radius,
                           chip_x + chip_radius, chip_y + chip_radius,
                           fill=style.color, outline="#1b1b1b", width=2)

        MM_TO_PIXEL = 3.0
        line_width = max(1.5, style.thickness_mm * MM_TO_PIXEL)
        dash_pattern = style.get_tk_dash_pattern(1.0)
        name_lower = style.name.lower()
        preview_y = baseline - 6

        if "волнистая" in name_lower:
            self._render_wavy_preview(canvas, margin + 8, preview_y, width - margin,
                                      preview_y, style.color, line_width)
        elif "изломами" in name_lower:
            self._render_zigzag_preview(canvas, margin + 8, preview_y, width - margin,
                                        preview_y, style.color, line_width)
        else:
            canvas.create_line(margin + 8, preview_y, width - margin, preview_y,
                               fill=style.color,
                               width=line_width,
                               dash=dash_pattern)

        canvas.create_text(width - margin, baseline - 12,
                           text=f"{style.thickness_mm:.2f} мм",
                           fill="#aaaaaa", anchor="e", font=("Segoe UI", 8, "bold"))

    def _render_wavy_preview(self, canvas, x1, y1, x2, y2, color, width):
        points = self._build_preview_wave_points(x1, x2, y1, amplitude=4, wavelength=28, mode="wave")
        canvas.create_line(*points, fill=color, width=width, smooth=True, splinesteps=8)

    def _render_zigzag_preview(self, canvas, x1, y1, x2, y2, color, width):
        points = self._build_preview_wave_points(x1, x2, y1, amplitude=4, wavelength=18, mode="zigzag")
        canvas.create_line(*points, fill=color, width=width, smooth=False)

    def _build_preview_wave_points(self, x1, x2, baseline, amplitude, wavelength, mode):
        length = max(x2 - x1, 1)
        if mode == "wave":
            periods = max(length / wavelength, 1)
            steps = max(int(periods * 16), 8)
            points = []
            for i in range(steps + 1):
                t = i / steps
                dist = t * length
                x = x1 + dist
                phase = 2 * pi * dist / wavelength
                y = baseline + sin(phase) * amplitude
                points.extend([x, y])
            return points
        else:
            spacing = max(wavelength, 12)
            points = [x1, baseline]
            i = 1
            while True:
                dist = i * spacing
                if dist >= length:
                    break
                x = x1 + dist
                points.extend([x, baseline])
                offset = amplitude if i % 2 else -amplitude
                points.extend([x, baseline + offset, x, baseline])
                i += 1
            points.extend([x2, baseline])
            return points

    def _setup_ui(self, root):
        """Создает и размещает все виджеты (Меню, Панель, Статусбар, Холст, Инспектор)."""

        # 1. Главное меню
        menubar = tk.Menu(root, bg="#2b2b2b", fg="white")
        root.config(menu=menubar)
        view_menu = tk.Menu(menubar, tearoff=0, bg="#2b2b2b", fg="white")
        menubar.add_cascade(label="Вид", menu=view_menu)
        view_menu.add_command(label="Показать все (Ctrl+0)", command=self.app.zoom_extents)
        view_menu.add_separator()
        view_menu.add_command(label="Увеличить (+)", command=self.app.zoom_in)
        view_menu.add_command(label="Уменьшить (-)", command=self.app.zoom_out)
        view_menu.add_command(label="Панорамирование (P)", command=lambda: self.app.set_tool("pan"))
        view_menu.add_command(label="Сбросить вид", command=self.app.reset_view)

        # 2. Панель инструментов (Top Bar)
        top = tk.Frame(root, bg="#2b2b2b", height=40, bd=0, relief="flat")
        top.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        self._create_styled_button(top, text="🖐 Рука [P]", command=lambda: self.app.set_tool("pan"),
                                   bg="#444444").pack(side=tk.LEFT, padx=3)
        self._create_styled_button(top, text="🔍 +", command=self.app.zoom_in,
                                   bg="#444444").pack(side=tk.LEFT, padx=3)
        self._create_styled_button(top, text="🔍 -", command=self.app.zoom_out,
                                   bg="#444444").pack(side=tk.LEFT, padx=3)
        tk.Label(top, text="|", bg="#2b2b2b", fg="#555").pack(side=tk.LEFT, padx=5)

        self._create_styled_button(top, text="Показать все [Ctrl+0]", command=self.app.zoom_extents,
                                   bg="#444444").pack(side=tk.LEFT, padx=3)
        self._create_styled_button(top, text="↺ 15° [L]",
                                   command=lambda: self.app.rotate_view(15),
                                   bg="#444444").pack(side=tk.LEFT, padx=3)
        self._create_styled_button(top, text="↻ 15° [R]",
                                   command=lambda: self.app.rotate_view(-15),
                                   bg="#444444").pack(side=tk.LEFT, padx=3)
        self._create_styled_button(top, text="Сброс Вида", command=self.app.reset_view).pack(side=tk.LEFT, padx=3)

        # Выбор текущего стиля на Top Bar
        style_frame = tk.Frame(top, bg="#2b2b2b")
        style_frame.pack(side=tk.LEFT, padx=(15, 3))
        tk.Label(style_frame, text="Текущий Стиль:", bg="#2b2b2b", fg="#cccccc", font=("Segoe UI", 9)).pack(
            side=tk.LEFT, padx=5)

        self.app.current_style_var = tk.StringVar()
        style_names = self.app.style_manager.get_style_names()

        # Стилизация ComboBox (Tkinter Style)
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox',
                        fieldbackground='#3a3a3a', background='#444444', foreground='white',
                        selectbackground='#555555', selectforeground='white', borderwidth=0)
        style.map('TCombobox', fieldbackground=[('readonly', '#3a3a3a')], background=[('readonly', '#3a3a3a')])

        self.app.style_combobox = ttk.Combobox(style_frame,
                                               textvariable=self.app.current_style_var,
                                               values=style_names,
                                               state='readonly',
                                               width=25,
                                               style='TCombobox')

        self.app.style_combobox.set(self.app.style_manager.current_style_name)
        self.app.style_combobox.bind("<<ComboboxSelected>>", self._on_style_select)
        self.app.style_combobox.pack(side=tk.LEFT)

        self.current_style_preview = tk.Canvas(style_frame, width=90, height=20,
                                               bg="#2b2b2b", bd=0, highlightthickness=0)
        self.current_style_preview.pack(side=tk.LEFT, padx=8)
        self.render_style_preview(self.current_style_preview,
                                  self.app.style_manager.get_style(self.app.style_manager.current_style_name))

        quick_frame = tk.Frame(top, bg="#2b2b2b")
        quick_frame.pack(side=tk.LEFT, padx=(10, 0))
        tk.Label(quick_frame, text="Быстрые стили:", bg="#2b2b2b", fg="#cccccc",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=4)

        self.quick_style_names = ["Сплошная основная", "Сплошная тонкая", "Штриховая"]
        for name in self.quick_style_names:
            if name not in style_names:
                continue
            btn = self._create_styled_button(quick_frame, text=name,
                                             command=lambda n=name: self._apply_quick_style(n),
                                             bg="#3a3a3a", font_size=8, padx=8, pady=4)
            btn.pack(side=tk.LEFT, padx=3)

        # 3. Строка состояния
        self.app.status_bar = tk.Label(root, text="", bd=0, relief=tk.FLAT, anchor=tk.W,
                                       bg="#3a3a3a", fg="#cccccc", font=("Segoe UI", 9), padx=10, pady=2)
        self.app.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 4. Боковая панель
        sidebar = tk.Frame(root, bg="#2b2b2b", width=180, bd=0, relief="flat")
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        sidebar.pack_propagate(False)

        # Инструменты
        self.app.tool_buttons = {}
        for tool_name, text, key in [("segment", "✏️ Отрезок [S]", "s"),
                                     ("select", "🖱 Выбор [V]", "v"),
                                     ("delete", "🗑 Удалить Объект [D]", "d")]:
            btn = self._create_styled_button(sidebar, text=text, command=lambda t=tool_name: self.app.set_tool(t),
                                             bg="#3a3a3a", font_size=10, height=1)
            btn.pack(fill=tk.X, pady=4, padx=8)
            self.app.tool_buttons[tool_name] = btn
        self.app.update_tool_buttons()

        # КНОПКА ДОБАВЛЕНИЯ ЧЕРЕЗ ДИАЛОГ
        self._create_styled_button(sidebar, text="➕ По координатам...", command=self.app.open_add_segment_dialog,
                                   bg="#3a3a3a", font_size=9).pack(fill=tk.X, pady=(0, 10), padx=8)

        # УПРАВЛЕНИЕ СТИЛЯМИ
        self._create_styled_button(sidebar, text="⚙️ Управление Стилями", command=self.open_style_manager_dialog,
                                   bg="#4477aa", font_size=9).pack(fill=tk.X, pady=(15, 4), padx=8)

        # Цвета (теперь для фона)
        self._create_styled_button(sidebar, text="🌄 Цвет Фона", command=self.app.choose_bg_color,
                                   bg="#444444").pack(fill=tk.X, pady=4, padx=8)

        # Привязка
        self.app.snap_check = tk.Checkbutton(sidebar, text="Привязка к Сетке [G]", variable=self.app.snap_enabled,
                                             bg="#2b2b2b", fg="white",
                                             selectcolor="#4477aa",
                                             activebackground="#2b2b2b",
                                             font=("Segoe UI", 10),
                                             bd=0, highlightthickness=0,
                                             padx=8, pady=5,
                                             anchor="w")
        self.app.snap_check.pack(fill=tk.X, pady=(10, 5), padx=8)

        # Очистка сцены
        self._create_styled_button(sidebar, text="ОЧИСТИТЬ ВСЕ [Ctrl+W]", command=self.app.clear_scene,
                                   bg="#993333", activebackground="#aa5555", fg="white", font_size=10).pack(fill=tk.X,
                                                                                                            pady=(10,
                                                                                                                  20),
                                                                                                            padx=8)

        # 5. Холст
        self.app.canvas = tk.Canvas(root, bg="#121212", highlightthickness=0, bd=0)
        self.app.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 6. Панель информации
        info_frame = tk.Frame(root, bg="#252526", width=250, bd=0, relief="flat")
        info_frame.pack(side=tk.RIGHT, fill=tk.Y)
        info_frame.pack_propagate(False)

        tk.Label(info_frame, text="СВОЙСТВА ОБЪЕКТОВ", bg="#333333", fg="#cccccc",
                 font=("Segoe UI", 9, "bold"), anchor="w", padx=10, pady=5).pack(fill=tk.X)

        props_frame = tk.Frame(info_frame, bg="#252526")
        props_frame.pack(fill=tk.X, padx=10, pady=6)

        self.app.selection_info_label = tk.Label(props_frame, text="Ничего не выбрано",
                                                 bg="#252526", fg="#dddddd", anchor="w",
                                                 font=("Segoe UI", 9, "bold"))
        self.app.selection_info_label.pack(fill=tk.X)

        state_frame = tk.Frame(props_frame, bg="#252526")
        state_frame.pack(fill=tk.X, pady=(6, 2))
        tk.Label(state_frame, text="Текущий стиль:",
                 bg="#252526", fg="#999999", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        self.app.selection_style_state_label = tk.Label(state_frame, text="—",
                                                        bg="#252526", fg="#ffffff",
                                                        font=("Segoe UI", 9, "bold"))
        self.app.selection_style_state_label.pack(side=tk.LEFT, padx=5)

        assign_frame = tk.Frame(props_frame, bg="#252526")
        assign_frame.pack(fill=tk.X, pady=(4, 2))
        tk.Label(assign_frame, text="Назначить стиль:",
                 bg="#252526", fg="#999999", font=("Segoe UI", 9)).pack(anchor="w")

        self.app.selection_style_combobox = ttk.Combobox(assign_frame,
                                                         textvariable=self.app.selection_style_var,
                                                         values=style_names,
                                                         state='disabled',
                                                         width=23,
                                                         style='TCombobox')
        self.app.selection_style_combobox.bind("<<ComboboxSelected>>", self._on_selection_style_select)
        self.app.selection_style_combobox.pack(anchor="w", pady=2)

        self.app.selection_preview_canvas = tk.Canvas(assign_frame, width=180, height=22,
                                                      bg="#1e1e1e", bd=0, highlightthickness=0)
        self.app.selection_preview_canvas.pack(fill=tk.X, pady=(4, 0))
        self.render_style_preview(self.app.selection_preview_canvas, None)

        self.app.selection_apply_btn = self._create_styled_button(props_frame,
                                                                  text="Применить к выделенным",
                                                                  command=self._apply_selection_style,
                                                                  bg="#3a5a3a", font_size=9)
        self.app.selection_apply_btn.pack(fill=tk.X, pady=(8, 2))
        self.app.selection_apply_btn.config(state=tk.DISABLED)

        tk.Label(props_frame, text="Свойства объектов:", bg="#252526", fg="#aaaaaa",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(10, 2))
        self.app.selection_details_text = tk.Text(props_frame, height=8, bg="#1b1b1b", fg="#dcdcdc",
                                                  font=("Consolas", 9), bd=0, highlightthickness=0,
                                                  wrap=tk.NONE, state=tk.DISABLED)
        self.app.selection_details_text.pack(fill=tk.X, pady=(0, 5))

        tk.Label(info_frame, text="ИНСПЕКТОР ОБЪЕКТОВ", bg="#333333", fg="#cccccc", font=("Segoe UI", 9, "bold"),
                 anchor="w", padx=10, pady=5).pack(fill=tk.X)

        self.app.info_text = tk.Text(info_frame, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 9),
                                     bd=0, highlightthickness=0, wrap=tk.WORD, state=tk.DISABLED)
        self.app.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)

        sb = tk.Scrollbar(info_frame, command=self.app.info_text.yview, bg="#252526", troughcolor="#1e1e1e",
                          borderwidth=0)
        sb.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        self.app.info_text.config(yscrollcommand=sb.set)

        return self.app.canvas, self.app.status_bar, self.app.info_text

    def _on_style_select(self, event):
        """Обрабатывает выбор стиля из ComboBox."""
        new_style_name = self.app.current_style_var.get()
        self.app.style_manager.set_current_style(new_style_name)
        # Обновляем цвет для обратной совместимости
        style = self.app.style_manager.get_style(new_style_name)
        self.app.segment_color = style.color
        self.render_style_preview(self.current_style_preview, style)

    def update_current_style_ui(self):
        """Обновляет выпадающий список стилей."""
        style_names = self.app.style_manager.get_style_names()
        self.app.style_combobox['values'] = style_names
        self.app.current_style_var.set(self.app.style_manager.current_style_name)
        if hasattr(self.app, "selection_style_combobox"):
            self.app.selection_style_combobox['values'] = style_names
        if hasattr(self, "current_style_preview"):
            style = self.app.style_manager.get_style(self.app.style_manager.current_style_name)
            self.render_style_preview(self.current_style_preview, style)

    def _apply_quick_style(self, style_name):
        if self.app.style_manager.set_current_style(style_name):
            self.app.current_style_var.set(style_name)
            style = self.app.style_manager.get_style(style_name)
            self.app.segment_color = style.color
            self.render_style_preview(self.current_style_preview, style)

    def _on_selection_style_select(self, event):
        self._apply_selection_style()

    def _apply_selection_style(self):
        self.app.apply_style_to_selection(self.app.selection_style_var.get())

    def open_style_manager_dialog(self):
        """Открывает диалог управления стилями линий."""
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Управление Стилями Линий (ГОСТ 2.303-68)")
        dialog.geometry("500x450")
        dialog.configure(bg="#2b2b2b")
        dialog.transient(self.app.root)
        dialog.grab_set()

        # Заголовок
        tk.Label(dialog, text="ГЛОБАЛЬНАЯ ПАЛИТРА СТИЛЕЙ", bg="#333333", fg="#cccccc",
                 font=("Segoe UI", 10, "bold"), padx=10, pady=8).pack(fill=tk.X)

        # Фрейм со списком стилей
        style_list_frame = tk.Frame(dialog, bg="#1e1e1e")
        style_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.style_list_widget = StylePreviewList(style_list_frame,
                                                  render_preview_callback=self.render_style_preview,
                                                  on_select=self._on_style_preview_select)
        self.style_list_widget.pack(fill=tk.BOTH, expand=True)

        self.style_details_frame = tk.Frame(dialog, bg="#2b2b2b", bd=0, relief=tk.FLAT)
        self.style_details_frame.pack(fill=tk.X, padx=10, pady=5)

        self.edit_thickness_var = tk.StringVar()
        self.edit_dash_var = tk.StringVar()
        self.edit_class_var = tk.StringVar(value="s")

        tk.Label(self.style_details_frame, text="Толщина (мм):", bg="#2b2b2b", fg="#cccccc").grid(row=0, column=0,
                                                                                                  sticky="w", padx=5,
                                                                                                  pady=2)
        tk.Entry(self.style_details_frame, textvariable=self.edit_thickness_var, width=10, bg="#3a3a3a", fg="white",
                 relief="flat").grid(row=0, column=1, sticky="w", padx=5, pady=2)

        tk.Label(self.style_details_frame, text="Шаблон штрихов (X,Y...):", bg="#2b2b2b", fg="#cccccc").grid(row=1,
                                                                                                             column=0,
                                                                                                             sticky="w",
                                                                                                             padx=5,
                                                                                                             pady=2)
        tk.Entry(self.style_details_frame, textvariable=self.edit_dash_var, width=20, bg="#3a3a3a", fg="white",
                 relief="flat").grid(row=1, column=1, sticky="w", padx=5, pady=2)

        tk.Label(self.style_details_frame, text="Тип толщины:", bg="#2b2b2b", fg="#cccccc").grid(row=2, column=0,
                                                                                                sticky="w", padx=5,
                                                                                                pady=2)
        self.edit_class_combobox = ttk.Combobox(self.style_details_frame,
                                                textvariable=self.edit_class_var,
                                                state="readonly",
                                                values=["s", "s_half"],
                                                width=12,
                                                style='TCombobox')
        self.edit_class_combobox.grid(row=2, column=1, sticky="w", padx=5, pady=2)

        self.apply_btn = self._create_styled_button(self.style_details_frame, text="Сохранить Изменения",
                                                    command=lambda: self._apply_style_changes(dialog), bg="#4477aa",
                                                    font_size=8)
        self.apply_btn.grid(row=3, column=0, columnspan=2, pady=10)
        self.apply_btn.config(state=tk.DISABLED)

        # Кнопки
        btn_frame = tk.Frame(dialog, bg="#2b2b2b")
        btn_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self._create_styled_button(btn_frame, text="Добавить (Пользоват.)",
                                   command=lambda: self._open_add_style_dialog(dialog), bg="#3a5a3a", font_size=9).pack(
            side=tk.LEFT, padx=5)
        self._create_styled_button(btn_frame, text="Удалить Выделенный",
                                   command=lambda: self._delete_selected_style(dialog), bg="#993333", font_size=9).pack(
            side=tk.RIGHT, padx=5)

        self.refresh_style_list()  # Первоначальное заполнение списка

    def refresh_style_list(self, preserve_selection=True):
        """Перезаполняет список стилей в диалоге управления."""
        if not hasattr(self, "style_list_widget"):
            return
        selected = self.style_list_widget.get_selected_style() if preserve_selection else None
        styles = [(name, self.app.style_manager.get_style(name)) for name in self.app.style_manager.get_style_names()]
        self.style_list_widget.populate(styles)
        if selected:
            self.style_list_widget.select(selected)

    def _on_style_preview_select(self, style_name):
        """Загружает параметры выбранного стиля в поля редактирования."""
        if not style_name:
            return
        style = self.app.style_manager.get_style(style_name)
        if not style:
            return

        self.edit_thickness_var.set(f"{style.thickness_mm:.2f}")
        self.edit_dash_var.set(", ".join(map(str, style.dash_pattern)))
        self.edit_class_var.set(style.thickness_class or "s_half")
        self.apply_btn.config(state=tk.NORMAL)

    def _apply_style_changes(self, parent_dialog):
        """Применяет изменения, введенные пользователем."""
        try:
            selected_name = self.style_list_widget.get_selected_style()
            if not selected_name:
                raise IndexError
            style = self.app.style_manager.get_style(selected_name)

            new_thickness = float(self.edit_thickness_var.get())
            new_dash_pattern_str = self.edit_dash_var.get().replace(' ', '')

            if not new_dash_pattern_str:
                new_dash_pattern = ()
            else:
                new_dash_pattern = tuple(float(x) for x in new_dash_pattern_str.split(',') if x)

            new_class = self.edit_class_var.get() or style.thickness_class

            self.app.style_manager.update_style(selected_name,
                                                thickness_mm=new_thickness,
                                                dash_pattern=new_dash_pattern,
                                                thickness_class=new_class)

            self.refresh_style_list()
            self.app.view.draw_all()

            messagebox.showinfo("Успех", f"Стиль '{selected_name}' обновлен.", parent=parent_dialog)

        except IndexError:
            messagebox.showerror("Ошибка", "Сначала выберите стиль.", parent=parent_dialog)
        except ValueError:
            messagebox.showerror("Ошибка",
                                 "Некорректный ввод чисел или толщина вне допустимого диапазона.",
                                 parent=parent_dialog)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка при сохранении: {e}", parent=parent_dialog)

    def _delete_selected_style(self, parent_dialog):
        """Удаляет выбранный пользовательский стиль."""
        try:
            selected_name = self.style_list_widget.get_selected_style()
            if not selected_name:
                raise IndexError

            style = self.app.style_manager.get_style(selected_name)
            if style.is_basic:
                messagebox.showerror("Ошибка", "Базовые стили ЕСКД нельзя удалять.", parent=parent_dialog)
                return

            if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить стиль '{selected_name}'?",
                                   parent=parent_dialog):
                self.app.style_manager.delete_style(selected_name)
                self.refresh_style_list()
                self.update_current_style_ui()
                self.app.view.draw_all()
                messagebox.showinfo("Успех", f"Стиль '{selected_name}' удален.", parent=parent_dialog)

        except IndexError:
            messagebox.showerror("Ошибка", "Сначала выберите стиль для удаления.", parent=parent_dialog)

    def _open_add_style_dialog(self, parent_dialog):
        """Диалог для добавления нового пользовательского стиля."""
        add_dialog = tk.Toplevel(parent_dialog)
        add_dialog.title("Добавить Пользовательский Стиль")
        add_dialog.geometry("320x230")
        add_dialog.configure(bg="#2b2b2b")
        add_dialog.transient(parent_dialog)
        add_dialog.grab_set()

        name_var = tk.StringVar()
        thickness_var = tk.StringVar(value="0.4")
        dash_var = tk.StringVar(value="")
        class_var = tk.StringVar(value="s_half")

        tk.Label(add_dialog, text="Имя:", bg="#2b2b2b", fg="#cccccc").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Entry(add_dialog, textvariable=name_var, bg="#3a3a3a", fg="white", relief="flat").grid(row=0, column=1,
                                                                                                  padx=5, pady=5)

        tk.Label(add_dialog, text="Толщина (мм):", bg="#2b2b2b", fg="#cccccc").grid(row=1, column=0, padx=5, pady=5,
                                                                                    sticky="w")
        tk.Entry(add_dialog, textvariable=thickness_var, bg="#3a3a3a", fg="white", relief="flat").grid(row=1, column=1,
                                                                                                       padx=5, pady=5)

        tk.Label(add_dialog, text="Шаблон (X,Y...):", bg="#2b2b2b", fg="#cccccc").grid(row=2, column=0, padx=5, pady=5,
                                                                                       sticky="w")
        tk.Entry(add_dialog, textvariable=dash_var, bg="#3a3a3a", fg="white", relief="flat").grid(row=2, column=1,
                                                                                                  padx=5, pady=5)

        tk.Label(add_dialog, text="Тип толщины:", bg="#2b2b2b", fg="#cccccc").grid(row=3, column=0, padx=5, pady=5,
                                                                                   sticky="w")
        ttk.Combobox(add_dialog, textvariable=class_var, values=["s", "s_half"], state="readonly",
                     width=12, style='TCombobox').grid(row=3, column=1, padx=5, pady=5, sticky="w")

        def on_add():
            try:
                name = name_var.get().strip()
                thickness = float(thickness_var.get())
                dash_str = dash_var.get().replace(' ', '')
                dash_pattern = tuple(float(x) for x in dash_str.split(',') if x) if dash_str else ()
                thickness_class = class_var.get() or None

                if not name:
                    raise ValueError("Имя стиля не может быть пустым.")

                self.app.style_manager.add_style(name, thickness, dash_pattern, is_basic=False,
                                                 thickness_class=thickness_class)
                self.refresh_style_list()
                self.update_current_style_ui()
                self.app.view.draw_all()
                add_dialog.destroy()
                messagebox.showinfo("Успех", f"Стиль '{name}' добавлен.")

            except ValueError as e:
                messagebox.showerror("Ошибка", str(e), parent=add_dialog)

        self._create_styled_button(add_dialog, text="Добавить", command=on_add, bg="#4477aa").grid(row=4, column=0,
                                                                                                   columnspan=2,
                                                                                                   pady=10)


class StylePreviewList(tk.Frame):
    """Список стилей с визуальным превью."""

    def __init__(self, master, render_preview_callback, on_select):
        super().__init__(master, bg="#1e1e1e")
        self.render_preview = render_preview_callback
        self.on_select = on_select
        self.canvas = tk.Canvas(self, bg="#1e1e1e", highlightthickness=0, bd=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                      bg="#252526", troughcolor="#1e1e1e", borderwidth=0)
        self.inner = tk.Frame(self.canvas, bg="#1e1e1e")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.row_widgets = {}
        self.selected_name = None

    def populate(self, styles):
        for child in self.inner.winfo_children():
            child.destroy()
        self.row_widgets.clear()
        for name, style in styles:
            def _fmt_dash(v):
                if isinstance(v, float):
                    return str(int(v)) if v.is_integer() else f"{v:.1f}"
                if isinstance(v, int):
                    return str(v)
                return str(v)
            row = tk.Frame(self.inner, bg="#1e1e1e", padx=8, pady=6,
                           highlightthickness=1, highlightbackground="#2b2b2b")
            preview = tk.Canvas(row, width=200, height=28, bg="#1e1e1e", highlightthickness=0, bd=0)
            self.render_preview(preview, style)
            preview.pack(side=tk.LEFT)
            info = tk.Frame(row, bg="#1e1e1e")
            info.pack(side=tk.LEFT, padx=10)
            tk.Label(info, text=name, bg="#1e1e1e", fg="#eeeeee", font=("Segoe UI", 9, "bold")).pack(anchor="w")
            tag = "ЕСКД" if style.is_basic else "Польз."
            pattern = "Сплошная линия" if not style.dash_pattern else \
                "Шаблон: " + " - ".join(_fmt_dash(v) for v in style.dash_pattern)
            tk.Label(info, text=f"{style.thickness_mm:.2f} мм • {tag}", bg="#1e1e1e", fg="#aaaaaa",
                     font=("Segoe UI", 8)).pack(anchor="w")
            tk.Label(info, text=pattern, bg="#1e1e1e", fg="#888888",
                     font=("Segoe UI", 8, "italic")).pack(anchor="w", pady=(2, 0))
            row.pack(fill=tk.X, padx=4, pady=3)

            for widget in (row, preview, info):
                widget.bind("<Button-1>", lambda e, n=name: self.select(n))

            self.row_widgets[name] = (row, preview, info)

        if self.selected_name and self.selected_name in self.row_widgets:
            self._set_row_state(self.selected_name, True)

    def select(self, name):
        if name not in self.row_widgets:
            return
        if self.selected_name and self.selected_name in self.row_widgets:
            self._set_row_state(self.selected_name, False)
        self.selected_name = name
        self._set_row_state(name, True)
        if self.on_select:
            self.on_select(name)

    def get_selected_style(self):
        return self.selected_name

    def _set_row_state(self, name, active):
        row, preview, info = self.row_widgets[name]
        bg = "#2b2b2b" if active else "#1e1e1e"
        for widget in (row, preview, info):
            widget.configure(bg=bg)
        for child in info.winfo_children():
            child.configure(bg=bg)