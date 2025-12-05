# core/segment.py (ОБНОВЛЕННЫЙ)

from math import sqrt, atan2, degrees
# Импорт менеджера стилей для доступа к текущим данным
# Здесь мы не будем импортировать StyleManager, чтобы избежать циклической зависимости.
# Вместо этого Segment будет работать с именем стиля и цветом,
# а LineStyle/StyleManager будут использоваться в SceneCADApp для получения данных.

class Segment:
    """
    Класс для хранения геометрического отрезка. Теперь хранит имя стиля линии.
    """
    def __init__(self, x1, y1, x2, y2, style_name, segment_id):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.style_name = style_name # Имя стиля, а не цвет
        self.segment_id = segment_id

    def length(self):
        """Вычисляет длину отрезка."""
        return sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

    def angle(self, as_degrees=True):
        """Вычисляет угол отрезка относительно оси X."""
        angle = atan2(self.y2 - self.y1, self.x2 - self.x1)
        return degrees(angle) if as_degrees else angle

    def describe(self, as_degrees=True):
        """Возвращает форматированное описание отрезка."""
        unit = "°" if as_degrees else "rad"
        length = self.length()
        angle = self.angle(as_degrees)

        desc = (f"Отрезок #{self.segment_id}\n"
                f"Начало: ({self.x1:.2f}, {self.y1:.2f})\n"
                f"Конец: ({self.x2:.2f}, {self.y2:.2f})\n"
                f"Длина: {length:.2f}\n"
                f"Угол: {angle:.2f} {unit}\n"
                f"Стиль: {self.style_name}")
        return desc


def distance_point_to_segment(px, py, x1, y1, x2, y2):
    """Вычисляет кратчайшее расстояние от точки до отрезка."""
    dx, dy = x2 - x1, y2 - y1
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0.0:
        return sqrt((px - x1) ** 2 + (py - y1) ** 2)

    t = ((px - x1) * dx + (py - y1) * dy) / seg_len_sq
    if t < 0.0:
        closest_x, closest_y = x1, y1
    elif t > 1.0:
        closest_x, closest_y = x2, y2
    else:
        closest_x, closest_y = x1 + t * dx, y1 + t * dy

    return sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)