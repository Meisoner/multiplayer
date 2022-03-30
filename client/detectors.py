import pygame as pg


class FallDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 15 + 2, 50 * 10, 46, 1)


class JumpDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 15 + 2, 50 * 9, 46, 1)


class RightDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 16, 50 * 9 + 20, 1, 10)


class LeftDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 15, 50 * 9 + 20, 1, 10)


class FallRightDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 16 + 1, 50 * 9, 1, 50)


class FallLeftDetector(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.rect = pg.rect.Rect(50 * 15 - 1, 50 * 9, 1, 50)