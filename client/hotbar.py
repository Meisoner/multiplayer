import pygame as pg


class Cell(pg.sprite.Sprite):
    def __init__(self, group, num, textures):
        super().__init__(group)
        self.chosen = False
        self.update_image()
        self.rect = self.image.get_rect()
        self.itemid = 0
        self.amount = 0
        self.rect.y = 25
        self.rect.x = 200 + num * 50
        self.textures = textures

    def update_image(self):
        self.image = pg.Surface((50, 50))
        self.image.fill((255, 255, 255))
        pg.draw.rect(self.image, (0, 0, 0), (0, 0, 50, 50), 1 + int(self.chosen) * 4)

    def placeitem(self, id, amount):
        self.itemid = id + 1
        self.amount = amount
        self.update_image()
        self.image.blit(self.textures[id], (10, 10))
        font = pg.font.Font(None, 20)
        amounttext = font.render(str(amount), True, (0, 0, 0))
        self.image.blit(amounttext, (5, 5))

    def getitem(self):
        if self.itemid:
            return self.itemid - 1

    def rmitem(self):
        self.itemid = 0
        self.amount = 0
        self.update_image()

    def choose(self):
        self.chosen = not self.chosen
        self.update_image()
        if self.itemid:
            self.placeitem(self.itemid - 1, self.amount)