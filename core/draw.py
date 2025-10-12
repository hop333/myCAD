from math import sqrt, atan2, degrees

class Segment:
    def __init__(self, x1, y1, x2, y2, color="#ff0000"):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.color = color

    def length(self):
        return sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)

    def angle(self, in_degrees=True):
        ang = atan2(self.y2 - self.y1, self.x2 - self.x1)
        return degrees(ang) if in_degrees else ang
