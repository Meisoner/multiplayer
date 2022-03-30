import pygame as pg


class Player(pg.sprite.Sprite):
    plimg = pg.Surface((50, 50), pg.SRCALPHA)
    pg.draw.ellipse(plimg, (255, 255, 150), (0, 0, 50, 50))

    def __init__(self, group):
        super().__init__(group)
        self.image = Player.plimg
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 50 * 15, 50 * 9