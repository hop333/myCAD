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

        # Шаблоны в мировых единицах, используемые для описания и логики
        dash = LineStyle.DASH_LEN
        space = LineStyle.SPACE_LEN
        dot = LineStyle.DOT_LEN

        default_styles = [
            LineStyle("Сплошная основная", s, (), True, "#E0E0E0"),
            LineStyle("Сплошная тонкая", s_half, (), True, "#C0C0C0"),
            LineStyle("Штриховая", s_half, (dash, space), True, "#999999"),
            LineStyle("Штрихпунктирная утолщенная", s, (dash, space, dot, space), True, "#66CCFF"),
            LineStyle("Штрихпунктирная тонкая", s_half, (dash, space, dot, space), True, "#66CCFF"),
            LineStyle("Штрихпунктирная с двумя точками", s_half, (dash, space, dot, space, dot, space), True,
                      "#FF6666"),
            LineStyle("Сплошная волнистая", s_half, (), True, "#E09999"),
            LineStyle("Сплошная тонкая с изломами", s_half, (), True, "#E09999"),
        ]

        for style in default_styles:
            self.styles[style.name] = style

    def get_style(self, name):
        """Возвращает объект LineStyle по имени."""
        return self.styles.get(name)

    def get_style_names(self):
        """Возвращает список имен всех стилей."""
        return list(self.styles.keys())

    def add_style(self, name, thickness_mm, dash_pattern=(), color="#FFFFFF", is_basic=False):
        """Добавляет новый пользовательский стиль."""
        if name in self.styles:
            raise ValueError(f"Стиль с именем '{name}' уже существует.")
        self.styles[name] = LineStyle(name, thickness_mm, dash_pattern, is_basic, color)

    def update_style(self, name, **kwargs):
        """Обновляет параметры существующего стиля."""
        style = self.styles.get(name)
        if not style:
            raise KeyError(f"Стиль '{name}' не найден.")

        if 'thickness_mm' in kwargs:
            style.thickness_mm = kwargs['thickness_mm']
        if 'dash_pattern' in kwargs:
            style.dash_pattern = kwargs['dash_pattern']
        if 'color' in kwargs:
            style.color = kwargs['color']

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