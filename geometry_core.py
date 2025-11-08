# geometry_core.py

from math import sqrt, atan2, degrees, radians, cos, sin, ceil, floor, log10

# ==============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ==============================================================================

def polar_to_cartesian(r, theta, degrees_mode=True):
    """Преобразует полярные координаты в декартовы."""
    if degrees_mode:
        theta = radians(theta)
    return r * cos(theta), r * sin(theta)

def distance_point_to_segment(px, py, x1, y1, x2, y2):
    """Вычисляет кратчайшее расстояние от точки (px, py) до отрезка (x1, y1)-(x2, y2)."""
    dx, dy = x2 - x1, y2 - y1
    if dx == 0 and dy == 0:
        return sqrt((px - x1) ** 2 + (py - y1) ** 2)
    t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    return sqrt((px - (x1 + t * dx)) ** 2 + (py - (y1 + t * dy)) ** 2)

# ==============================================================================
# ГЕОМЕТРИЧЕСКИЕ КЛАССЫ
# ==============================================================================

class Segment:
    """Представляет один геометрический отрезок."""
    _id_counter = 1

    def __init__(self, x1, y1, x2, y2, color="#ff0000"):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.color = color
        self.uid = Segment._id_counter
        Segment._id_counter += 1

    def length(self):
        """Возвращает длину отрезка."""
        return sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

    def angle(self, in_degrees=True):
        """Возвращает угол отрезка."""
        ang = atan2(self.y2 - self.y1, self.x2 - self.x1)
        return degrees(ang) if in_degrees else ang


class Scene:
    """Управляет коллекцией геометрических объектов (отрезков)."""
    def __init__(self):
        self.segments = []

    def add_segment(self, x1, y1, x2, y2, color="#ff0000"):
        self.segments.append(Segment(x1, y1, x2, y2, color))

    def add_segment_polar(self, x1, y1, r, theta, color="#ff0000", degrees_mode=True):
        dx, dy = polar_to_cartesian(r, theta, degrees_mode)
        self.segments.append(Segment(x1, y1, x1 + dx, y1 + dy, color))

    def clear(self):
        self.segments.clear()

    def describe(self, degrees_mode=True):
        """Возвращает текстовое описание всех отрезков для Инспектора."""
        if not self.segments:
            return "Сцена пуста."
        info = ""
        for seg in self.segments:
            info += (f"➤ Отрезок [{seg.uid}]\n"
                     f"   ({seg.x1:.1f}, {seg.y1:.1f}) → ({seg.x2:.1f}, {seg.y2:.1f})\n"
                     f"   L={seg.length():.2f}, ∠={seg.angle(degrees_mode):.1f}°\n\n")
        return info