import tkinter as tk
from tkinter import colorchooser, messagebox
from math import degrees, radians, cos, sin


class CADUI:
    """Класс для построения пользовательского интерфейса Tkinter. 
    SceneCADApp наследует этот класс для получения ссылок на виджеты."""

    def __init__(self, root, app_ref):
        # app_ref нужен, чтобы кнопки могли вызывать методы SceneCADApp (например, self.zoom_in)
        self.app = app_ref
        self._setup_ui(root)

    def _create_styled_button(self, parent, text, command, bg="#3a3a3a", fg="white", activebackground="#555555",
                              font_size=9, **kwargs):
        """Создает кнопку со стилем."""
        return tk.Button(parent, text=text, command=command,
                         bg=bg, fg=fg, activebackground=activebackground, activeforeground="white",
                         relief="flat", bd=0, highlightthickness=0,
                         font=("Segoe UI", font_size, "bold"),
                         padx=12, pady=7, **kwargs)

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
        view_menu.add_separator()
        view_menu.add_command(label="Повернуть на 15° ↺ (L)", command=lambda: self.app.rotate_view(15))
        view_menu.add_command(label="Повернуть на 15° ↻ (R)", command=lambda: self.app.rotate_view(-15))
        view_menu.add_separator()
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
                                     ("delete", "🗑 Удалить Объект [D]", "d")]:
            btn = self._create_styled_button(sidebar, text=text, command=lambda t=tool_name: self.app.set_tool(t),
                                             bg="#3a3a3a", font_size=10, height=1)
            btn.pack(fill=tk.X, pady=4, padx=8)
            self.app.tool_buttons[tool_name] = btn
        self.app.update_tool_buttons()

        # КНОПКА ДОБАВЛЕНИЯ ЧЕРЕЗ ДИАЛОГ
        self._create_styled_button(sidebar, text="➕ По координатам...", command=self.app.open_add_segment_dialog,
                                   bg="#3a3a3a", font_size=9).pack(fill=tk.X, pady=(0, 10), padx=8)

        # Цвета
        self._create_styled_button(sidebar, text="🎨 Цвет фигуры", command=self.app.choose_segment_color,
                                   bg="#444444").pack(fill=tk.X, pady=(15, 4), padx=8)
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

        tk.Label(info_frame, text="ИНСПЕКТОР ОБЪЕКТОВ", bg="#333333", fg="#cccccc", font=("Segoe UI", 9, "bold"),
                 anchor="w", padx=10, pady=5).pack(fill=tk.X)

        self.app.info_text = tk.Text(info_frame, bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 9),
                                     bd=0, highlightthickness=0, wrap=tk.WORD, state=tk.DISABLED)
        self.app.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)

        sb = tk.Scrollbar(info_frame, command=self.app.info_text.yview, bg="#252526", troughcolor="#1e1e1e",
                          borderwidth=0)
        sb.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        self.app.info_text.config(yscrollcommand=sb.set)

        # Передаем ссылки на ключевые виджеты обратно в SceneCADApp
        return self.app.canvas, self.app.status_bar, self.app.info_text