from math import atan2, degrees, sqrt
from core.segment import Segment
from core.geometry import polar_to_cartesian

class Scene:
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
        info = ""
        for i, seg in enumerate(self.segments):
            length = seg.length()
            angle = seg.angle(degrees_mode)
            info += (
                f"Отрезок {i+1}:\n"
                f"  Точка1: ({seg.x1:.2f}, {seg.y1:.2f})\n"
                f"  Точка2: ({seg.x2:.2f}, {seg.y2:.2f})\n"
                f"  Длина: {length:.2f}, Угол: {angle:.2f}\n\n"
            )
        return info
