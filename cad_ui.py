import tkinter as tk
from tkinter import colorchooser, messagebox, ttk


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

    def update_current_style_ui(self):
        """Обновляет выпадающий список стилей."""
        style_names = self.app.style_manager.get_style_names()
        self.app.style_combobox['values'] = style_names
        self.app.current_style_var.set(self.app.style_manager.current_style_name)

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

        self.style_listbox = tk.Listbox(style_list_frame,
                                        bg="#1e1e1e", fg="#cccccc",
                                        selectbackground="#4477aa",
                                        selectforeground="white",
                                        font=("Consolas", 10),
                                        relief=tk.FLAT, bd=0, highlightthickness=0)
        self.style_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.style_listbox.bind("<<ListboxSelect>>", self._on_style_listbox_select)

        sb = tk.Scrollbar(style_list_frame, command=self.style_listbox.yview, bg="#252526", troughcolor="#1e1e1e",
                          borderwidth=0)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.style_listbox.config(yscrollcommand=sb.set)

        self.style_details_frame = tk.Frame(dialog, bg="#2b2b2b", bd=0, relief=tk.FLAT)
        self.style_details_frame.pack(fill=tk.X, padx=10, pady=5)

        self.edit_thickness_var = tk.StringVar()
        self.edit_dash_var = tk.StringVar()

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

        self.apply_btn = self._create_styled_button(self.style_details_frame, text="Сохранить Изменения",
                                                    command=lambda: self._apply_style_changes(dialog), bg="#4477aa",
                                                    font_size=8)
        self.apply_btn.grid(row=2, column=0, columnspan=2, pady=10)

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

    def refresh_style_list(self):
        """Перезаполняет список стилей в диалоге управления."""
        self.style_listbox.delete(0, tk.END)
        for name, style in self.app.style_manager.styles.items():
            thickness = f"{style.thickness_mm:.2f} мм"
            basic_tag = " (ЕСКД)" if style.is_basic else " (Польз.)"
            self.style_listbox.insert(tk.END, f"{name} ({thickness}){basic_tag}")

    def _on_style_listbox_select(self, event):
        """Загружает параметры выбранного стиля в поля редактирования."""
        try:
            index = self.style_listbox.curselection()[0]
            selected_name = self.app.style_manager.get_style_names()[index]
            style = self.app.style_manager.get_style(selected_name)

            self.edit_thickness_var.set(f"{style.thickness_mm:.2f}")
            self.edit_dash_var.set(", ".join(map(str, style.dash_pattern)))

            is_editable = not style.is_basic
            self.apply_btn.config(state=tk.NORMAL if is_editable else tk.DISABLED,
                                  text="Сохранить (Только для Пользоват. Стилей)")

        except IndexError:
            pass

    def _apply_style_changes(self, parent_dialog):
        """Применяет изменения, введенные пользователем."""
        try:
            index = self.style_listbox.curselection()[0]
            selected_name = self.app.style_manager.get_style_names()[index]
            style = self.app.style_manager.get_style(selected_name)

            if style.is_basic:
                messagebox.showerror("Ошибка", "Базовые стили ЕСКД нельзя редактировать!", parent=parent_dialog)
                return

            new_thickness = float(self.edit_thickness_var.get())
            new_dash_pattern_str = self.edit_dash_var.get().replace(' ', '')

            if not new_dash_pattern_str:
                new_dash_pattern = ()
            else:
                new_dash_pattern = tuple(float(x) for x in new_dash_pattern_str.split(',') if x)

            self.app.style_manager.update_style(selected_name,
                                                thickness_mm=new_thickness,
                                                dash_pattern=new_dash_pattern)

            self.refresh_style_list()
            self.app.view.draw_all()

            messagebox.showinfo("Успех", f"Стиль '{selected_name}' обновлен.", parent=parent_dialog)

        except IndexError:
            messagebox.showerror("Ошибка", "Сначала выберите стиль.", parent=parent_dialog)
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректный ввод чисел (толщина или шаблон).", parent=parent_dialog)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Неизвестная ошибка при сохранении: {e}", parent=parent_dialog)

    def _delete_selected_style(self, parent_dialog):
        """Удаляет выбранный пользовательский стиль."""
        try:
            index = self.style_listbox.curselection()[0]
            selected_name = self.app.style_manager.get_style_names()[index]

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
        add_dialog.geometry("300x200")
        add_dialog.configure(bg="#2b2b2b")
        add_dialog.transient(parent_dialog)
        add_dialog.grab_set()

        name_var = tk.StringVar()
        thickness_var = tk.StringVar(value="0.4")
        dash_var = tk.StringVar(value="")

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

        def on_add():
            try:
                name = name_var.get().strip()
                thickness = float(thickness_var.get())
                dash_str = dash_var.get().replace(' ', '')
                dash_pattern = tuple(float(x) for x in dash_str.split(',') if x) if dash_str else ()

                if not name:
                    raise ValueError("Имя стиля не может быть пустым.")

                self.app.style_manager.add_style(name, thickness, dash_pattern, is_basic=False)
                self.refresh_style_list()
                self.update_current_style_ui()
                add_dialog.destroy()
                messagebox.showinfo("Успех", f"Стиль '{name}' добавлен.")

            except ValueError as e:
                messagebox.showerror("Ошибка", str(e), parent=add_dialog)

        self._create_styled_button(add_dialog, text="Добавить", command=on_add, bg="#4477aa").grid(row=3, column=0,
                                                                                                   columnspan=2,
                                                                                                   pady=10)