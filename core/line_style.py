# core/line_style.py

class LineStyle:
    """
    Класс, представляющий стиль линии согласно ГОСТ 2.303-68.
    """
    BASIC_THICKNESS_S = 1.0
    BASIC_THICKNESS_S_HALF = 0.5
    MM_TO_PIXEL = 3.7795  # ~96 DPI
    DASH_VISUAL_SCALE = 1.8

    def __init__(self, name, thickness_mm, dash_pattern=None, is_basic=True, color="#FFFFFF",
                 thickness_class=None):
        self.name = name
        self.thickness_mm = thickness_mm
        self.dash_pattern = dash_pattern if dash_pattern is not None else ()
        self.is_basic = is_basic
        self.color = color
        self.thickness_class = thickness_class or self.infer_class(thickness_mm)

    def get_tk_dash_pattern(self, scale, override_pattern=None):
        """
        pattern — длины в шагах сетки (1 шаг = 1 мм).
        """
        pattern = override_pattern if override_pattern is not None else self.dash_pattern
        if not pattern:
            return ()

        base = 20.0  # BASE_SCALE
        raw_factor = scale / base if base > 0 else 1.0
        factor = max(0.8, min(1.2, raw_factor))  # чуть смягчаем при зуме

        pattern_pixels = []
        for length_mm in pattern:
            px = length_mm * self.MM_TO_PIXEL * factor
            pixels = int(max(1, min(255, round(px))))
            pattern_pixels.append(pixels)
        return tuple(pattern_pixels)

    @staticmethod
    def infer_class(thickness_mm):
        return "s" if thickness_mm > 0.5 else "s_half"