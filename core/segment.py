from math import sqrt, atan2, degrees

class Segment:
    _id_counter = 1  # Статический счетчик для уникальных ID

    def __init__(self, x1, y1, x2, y2, color="#ff0000"):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2
        self.color = color
        self.uid = Segment._id_counter  # Присваиваем уникальный ID
        Segment._id_counter += 1

    def length(self):
        return sqrt((self.x2 - self.x1)**2 + (self.y2 - self.y1)**2)

    def angle(self, in_degrees=True):
        ang = atan2(self.y2 - self.y1, self.x2 - self.x1)
        return degrees(ang) if in_degrees else ang
