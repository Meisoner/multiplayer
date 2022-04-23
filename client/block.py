import pygame as pg


HEIGHT = 800


class Block(pg.sprite.Sprite):
    def __init__(self, group, delta, image, playerpos, blockpos, protected, id):
        super().__init__(group)
        self.image = image
        self.dx, self.dy = 0, 0
        self.rect = self.image.get_rect()
        self.rect.x = (blockpos[0] - playerpos[0] + 15) * 50 - int(delta[0])
        self.rect.y = HEIGHT - (blockpos[1] - playerpos[1] + 7) * 50 - int(delta[1])
        self.coords = tuple(blockpos)
        self.unbreakable = protected
        self.id = id

    def update(self, click, move):
        try:
            if click and not self.unbreakable:
                x, y = click[:2]
                if self.rect.x <= x <= self.rect.x + 49 and self.rect.y <= y <= self.rect.y + 49:
                    self.remove(self.groups()[0])
                    toremove, topart, last = click[2:]
                    toremove += [self.coords]
                    topart += [(self.rect.x, self.rect.y, pg.transform.average_color(self.image)[:3])]
                    last += [self.id]
            if move:
                self.rect.x += move[0]
                self.rect.y += move[1]
        except Exception:
            pass

    def check(self, coords):
        return self.rect.x <= coords[0] <= self.rect.x + 49 and self.rect.y <= coords[1] <= self.rect.y + 49