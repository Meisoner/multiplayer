import pygame as pg


# Детектор падения
class FallDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 15 + 2, 50 * 10, 46, 1)


# Детектор прыжка
class JumpDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 15 + 2, 50 * 9, 46, 1)


# Детектор удара справа
class RightDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 16, 50 * 9 + 20, 1, 10)


# Детектор улара слева
class LeftDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 15, 50 * 9 + 20, 1, 10)


# Детектор удара справа во время прыжка
class FallRightDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 16 + 1, 50 * 9, 1, 50)


# Детектор удара слева во время прыжка
class FallLeftDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 15 - 1, 50 * 9, 1, 50)