from .segment import Segment

class Scene:
    """Класс для управления коллекцией геометрических объектов (отрезков)."""
    def __init__(self, style_manager):
        self.segments = []
        self.style_manager = style_manager # Ссылка на менеджер стилей
        self._segment_counter = 1

    def add_segment(self, x1, y1, x2, y2, style_name):
        style = self.style_manager.get_style(style_name)
        if style:
            # Храним только имя стиля; цвет и остальные параметры берутся при отрисовке
            self.segments.append(Segment(x1, y1, x2, y2, style_name, self._segment_counter))
            self._segment_counter += 1

    def clear(self):
        """Очищает сцену от всех объектов."""
        self.segments = []
        self._segment_counter = 1

    def describe(self, as_degrees=True):
        """Возвращает описание всех объектов на сцене."""
        if not self.segments:
            return "Нет объектов на сцене."

        output = f"Всего объектов: {len(self.segments)}\n\n"
        for i, s in enumerate(self.segments):
            output += f"--- Отрезок {i + 1} ---\n"
            output += s.describe(as_degrees)
            output += "\n\n"
        return output