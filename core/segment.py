from math import sqrt, atan2, degrees


class Segment:
    """Класс для хранения геометрического отрезка и связанных с ним свойств."""
    def __init__(self, x1, y1, x2, y2, color):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.color = color

    def length(self):
        """Вычисляет длину отрезка."""
        return sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

    def angle(self, as_degrees=True):
        """Вычисляет угол отрезка относительно оси X."""
        # Угол в радианах от горизонтальной оси X
        angle = atan2(self.y2 - self.y1, self.x2 - self.x1)
        return degrees(angle) if as_degrees else angle

    def describe(self, as_degrees=True):
        """Возвращает форматированное описание отрезка."""
        unit = "°" if as_degrees else "rad"
        length = self.length()
        angle = self.angle(as_degrees)

        desc = (f"Начало: ({self.x1:.2f}, {self.y1:.2f})\n"
                f"Конец: ({self.x2:.2f}, {self.y2:.2f})\n"
                f"Длина: {length:.2f}\n"
                f"Угол: {angle:.2f} {unit}\n"
                f"Цвет: {self.color}")
        return desc


def distance_point_to_segment(px, py, x1, y1, x2, y2):
    """Вычисляет кратчайшее расстояние от точки до отрезка."""
    dx, dy = x2 - x1, y2 - y1
    seg_len_sq = dx * dx + dy * dy

    if seg_len_sq == 0.0:
        return sqrt((px - x1) ** 2 + (py - y1) ** 2)

    t = ((px - x1) * dx + (py - y1) * dy) / seg_len_sq

    # Находим ближайшую точку на отрезке
    if t < 0.0:
        closest_x, closest_y = x1, y1
    elif t > 1.0:
        closest_x, closest_y = x2, y2
    else:
        closest_x, closest_y = x1 + t * dx, y1 + t * dy

    return sqrt((px - closest_x) ** 2 + (py - closest_y) ** 2)