import pygame as pg


# Класс текущего игрока
class Player(pg.sprite.Sprite):
    plimg = pg.image.load('textures/ninja.png')

    def __init__(self, group):
        super().__init__(group)
        self.image = pg.transform.scale(Player.plimg, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 50 * 15, 50 * 9
        self.right = False

    def turn(self, right):
        if self.right != right:
            self.image = pg.transform.flip(self.image, True, False)
            self.right = right