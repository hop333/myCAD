# D:\Programming\myCAD\line_styles.py

class LineStyle:
    """
    Представляет один стиль линии (цвет, толщина, тип).
    """

    def __init__(self, name, color, line_type, width, dash_pattern=()):
        # ⚠️ ИСПРАВЛЕНО: Убедитесь, что все атрибуты определены в __init__
        self.name = name
        self.color = color
        self.line_type = line_type
        self.width = width
        self.dash_pattern = dash_pattern
        self.attached_segments = set()  # Объекты, использующие этот стиль

    def attach(self, segment):
        """Добавляет сегмент к списку объектов, использующих этот стиль."""
        self.attached_segments.add(segment)

    def detach(self, segment):
        """Удаляет сегмент из списка."""
        self.attached_segments.discard(segment)

    def notify_change(self):
        """
        Уведомляет все прикрепленные сегменты, что стиль изменился.
        На практике, это вызывает перерисовку через cad_app.
        """
        # Если у вас есть ссылка на app, здесь можно вызвать app.redraw_due_to_style_change()
        # Для простоты, пока оставим пустым или с заглушкой.
        pass

    # --- Методы для свойств (если LineStyle был изменен на использование методов) ---
    # Эти методы оставлены здесь для обратной совместимости с последним исправлением в cad_view.py
    # Если вы используете атрибуты напрямую, эти методы можно удалить.
    def get_color(self):
        return self.color

    def get_width(self):
        return self.width

    def __repr__(self):
        return f"LineStyle('{self.name}', width={self.width})"


### 2. Класс `StyleManager`

class StyleManager:
    """
    Централизованное хранилище и управление всеми стилями линий.
    """

    def __init__(self):
        self.styles = {}
        self._initialize_gost_styles()

    def _initialize_gost_styles(self):
        """
        Инициализирует базовые стили линий по ГОСТ/ISO.
        """
        # ⚠️ ИСПРАВЛЕНО: Теперь все вызовы LineStyle имеют правильный порядок аргументов:
        # (name, color, line_type, width, dash_pattern)

        # 1. Сплошная основная (толщина 2.0 пикселя - заметная)
        self.add_style(LineStyle("Сплошная основная (s)", "#FFFFFF", "Сплошная", 2.0))

        # 2. Сплошная тонкая (толщина 1.0 пиксель)
        self.add_style(LineStyle("Сплошная тонкая (t)", "#CCCCCC", "Сплошная", 1.0))

        # 3. Штриховая
        self.add_style(LineStyle("Штриховая (h)", "#AAAAAA", "Штрих", 1.0, dash_pattern=(6, 3)))

        # 4. Штрихпунктирная
        self.add_style(LineStyle("Штрихпунктирная (hp)", "#999999", "Штрихпунктир", 1.0, dash_pattern=(10, 2, 2, 2)))

        # 5. Длинный штрих (для обозначения разреза, толстая)
        self.add_style(LineStyle("Линия разреза (l)", "#FF9900", "Длинный штрих", 3.0, dash_pattern=(10, 2)))

    def add_style(self, style: LineStyle):
        """Добавляет новый стиль в менеджер."""
        self.styles[style.name] = style

    def get_style(self, name: str) -> LineStyle:
        """Возвращает стиль по имени."""
        return self.styles.get(name)

    def get_all_names(self):
        """Возвращает список всех имен стилей."""
        return list(self.styles.keys())

    # --- Создание экземпляра менеджера стилей ---


style_manager = StyleManager()