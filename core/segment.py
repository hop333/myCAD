from math import sqrt, atan2, pi


# --- Assuming this is the class definition around line 15-25 ---
class Segment:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    # Line 20: CORRECTED length method
    def length(self):
        """Calculates the Euclidean distance (length) of the segment."""
        # The error was here: 'x1' was missing 'self.'
        # Corrected to use self.x1 and self.y1
        return sqrt((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2)

    def angle(self, degrees_mode=False):
        """Calculates the angle of the segment relative to the positive x-axis."""
        # Calculate the angle using atan2
        delta_x = self.x2 - self.x1
        delta_y = self.y2 - self.y1

        angle_rad = atan2(delta_y, delta_x)

        if degrees_mode:
            # Convert radians to degrees
            angle_deg = angle_rad * 180 / pi
            # Normalize angle to be between 0 and 360 degrees
            if angle_deg < 0:
                angle_deg += 360
            return angle_deg

        return angle_rad

    # Placeholder for the describe method mentioned in the traceback (Line 53)
    # The actual implementation depends on the CAD logic, but the signature is likely:
    def describe(self, degrees_mode=False):
        """Returns a string description of the segment."""
        length = self.length()
        angle = self.angle(degrees_mode)
        unit = "°" if degrees_mode else " rad"

        description = (
            f"Segment: ({self.x1:.2f}, {self.y1:.2f}) -> ({self.x2:.2f}, {self.y2:.2f})\n"
            f"  Length (L): {length:.2f}\n"
            f"  Angle (∠): {angle:.1f}{unit}\n"
        )
        return description

# Note: The rest of your myCAD application code would follow here.