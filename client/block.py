import pygame as pg


HEIGHT = 800


class Block(pg.sprite.Sprite):
    def __init__(self, group, delta, image, playerpos, blockpos, protected):
        super().__init__(group)
        self.image = image
        self.dx, self.dy = 0, 0
        self.rect = self.image.get_rect()
        self.rect.x = (blockpos[0] - playerpos[0] + 15) * 50 - int(delta[0])
        self.rect.y = HEIGHT - (blockpos[1] - playerpos[1] + 7) * 50 - int(delta[1])
        self.coords = tuple(blockpos)
        self.unbreakable = protected

    def update(self, click, move):
        try:
            if click and not self.unbreakable:
                x, y = click[:2]
                if self.rect.x <= x <= self.rect.x + 49 and self.rect.y <= y <= self.rect.y + 49:
                    self.remove(self.groups()[0])
                    toremove, topart = click[2:]
                    toremove += [self.coords]
                    topart += [(self.rect.x, self.rect.y, pg.transform.average_color(self.image)[:3])]
            if move:
                self.dx += move[0]
                self.dy -= move[1]
                if abs(self.dx) >= 1:
                    self.rect.x += int(self.dx)
                    self.dx -= int(self.dx)
                if abs(self.dy) >= 1:
                    self.rect.y += int(self.dy)
                    self.dy -= int(self.dy)
        except Exception:
            pass