# core/style_manager.py

from .line_style import LineStyle
from tkinter import messagebox


class StyleManager:
    """Централизованный менеджер стилей линий (палитра стилей) согласно ГОСТ 2.303-68."""

    def __init__(self):
        self.styles = {}
        self._initialize_default_styles()
        self.current_style_name = list(self.styles.keys())[0]

    def _initialize_default_styles(self):
        """Инициализирует базовые стили ЕСКД."""
        s = LineStyle.BASIC_THICKNESS_S
        s_half = LineStyle.BASIC_THICKNESS_S_HALF

        default_styles = [
            LineStyle("Сплошная основная", s, (), True, "#E0E0E0", thickness_class="s"),
            LineStyle("Сплошная тонкая", s_half, (), True, "#C0C0C0", thickness_class="s_half"),
            LineStyle("Штриховая", s_half, (8.0, 2.0), True, "#999999", thickness_class="s_half"),
            LineStyle("Штрихпунктирная утолщенная", s, (24.0, 4.0, 2.0, 4.0), True, "#66CCFF", thickness_class="s"),
            LineStyle("Штрихпунктирная тонкая", s_half, (24.0, 4.0, 2.0, 4.0), True, "#66CCFF",
                      thickness_class="s_half"),
            LineStyle("Штрихпунктирная с двумя точками", s_half, (24.0, 4.0, 2.0, 4.0, 2.0, 4.0), True,
                      "#FF6666", thickness_class="s_half"),
            LineStyle("Сплошная волнистая", s_half, (), True, "#E09999", thickness_class="s_half"),
            LineStyle("Сплошная тонкая с изломами", s_half, (), True, "#E09999", thickness_class="s_half"),
        ]

        for style in default_styles:
            self.styles[style.name] = style

    def get_style(self, name):
        """Возвращает объект LineStyle по имени."""
        return self.styles.get(name)

    def get_style_names(self):
        """Возвращает список имен всех стилей."""
        return list(self.styles.keys())

    def add_style(self, name, thickness_mm, dash_pattern=(), color="#FFFFFF", is_basic=False, thickness_class=None):
        """Добавляет новый пользовательский стиль."""
        if name in self.styles:
            raise ValueError(f"Стиль с именем '{name}' уже существует.")
        thickness_class = thickness_class or LineStyle.infer_class(thickness_mm)
        self._assert_valid_thickness(thickness_mm, thickness_class)
        self.styles[name] = LineStyle(name, thickness_mm, dash_pattern, is_basic, color,
                                      thickness_class=thickness_class)

    def update_style(self, name, **kwargs):
        """Обновляет параметры существующего стиля."""
        style = self.styles.get(name)
        if not style:
            raise KeyError(f"Стиль '{name}' не найден.")

        new_thickness = kwargs.get('thickness_mm', style.thickness_mm)
        new_class = kwargs.get('thickness_class', style.thickness_class)
        self._assert_valid_thickness(new_thickness, new_class)
        style.thickness_mm = new_thickness
        style.thickness_class = new_class
        if 'dash_pattern' in kwargs:
            style.dash_pattern = kwargs['dash_pattern']
        if 'color' in kwargs:
            style.color = kwargs['color']
        if 'thickness_mm' not in kwargs and 'thickness_class' not in kwargs:
            # уже все обновлено, но для совместимости возвращаем
            pass

    def delete_style(self, name):
        """Удаляет пользовательский стиль."""
        style = self.styles.get(name)
        if not style:
            return
        if style.is_basic:
            messagebox.showwarning("Запрет", "Нельзя удалять базовые стили ЕСКД.")
            return
        del self.styles[name]

        # Сброс текущего стиля, если удалили выбранный
        if self.current_style_name == name:
            self.current_style_name = list(self.styles.keys())[0]

    def set_current_style(self, name):
        """Устанавливает текущий стиль для новых объектов."""
        if name in self.styles:
            self.current_style_name = name
            return True
        return False

    @staticmethod
    def _assert_valid_thickness(thickness_mm, thickness_class):
        if thickness_class not in ("s", "s_half"):
            raise ValueError("Неизвестный тип толщины линии.")
        bounds = (0.5, 1.4) if thickness_class == "s" else (0.25, 0.7)
        if not (bounds[0] <= thickness_mm <= bounds[1]):
            raise ValueError(
                f"Толщина {thickness_mm:.2f} мм выходит за пределы для типа '{thickness_class}'. "
                f"Допустимо: {bounds[0]}—{bounds[1]} мм."
            )