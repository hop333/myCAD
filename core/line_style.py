# core/line_style.py

class LineStyle:
    """
    Класс, представляющий стиль линии согласно ГОСТ 2.303-68.
    """
    BASIC_THICKNESS_S = 0.8
    BASIC_THICKNESS_S_HALF = BASIC_THICKNESS_S / 2.0

    # Константы для длин штрихов в мировых единицах (используются для описания стиля, не для отрисовки Tk)
    DASH_LEN = 10.0
    SPACE_LEN = 2.0
    DOT_LEN = 0.5

    def __init__(self, name, thickness_mm, dash_pattern=None, is_basic=True, color="#FFFFFF"):
        self.name = name
        self.thickness_mm = thickness_mm
        self.dash_pattern = dash_pattern if dash_pattern is not None else ()
        self.is_basic = is_basic
        self.color = color

    def get_tk_dash_pattern(self, scale):
        """
        Преобразует шаблон штриховки в формат Tkinter (пиксели) для визуально
        постоянного отображения на экране.
        """
        if not self.dash_pattern:
            return ()  # Сплошная линия

        # Для визуально постоянного на экране вида, используем константы пикселей:
        if "Сплошная" in self.name:
            return ()
        elif "Штриховая" in self.name:
            return (12, 6)
        elif "Штрихпунктирная" in self.name and "двумя" not in self.name:
            return (20, 5, 2, 5)  # Штрих-Пробел-Точка-Пробел
        elif "двумя точками" in self.name:
            return (20, 5, 2, 5, 2, 5)  # Штрих-Пробел-Точка-Пробел-Точка-Пробел
        elif "волнистая" in self.name or "с изломами" in self.name:
            return ()  # Tkinter не поддерживает

        return ()