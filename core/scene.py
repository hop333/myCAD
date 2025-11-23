from .segment import Segment

class Scene:
    """Класс для управления коллекцией геометрических объектов (отрезков)."""
    def __init__(self):
        self.segments = []

    def add_segment(self, x1, y1, x2, y2, color):
        self.segments.append(Segment(x1, y1, x2, y2, color))

    def clear(self):
        """Очищает сцену от всех объектов."""
        self.segments = []

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