import pygame as pg
from player import Player
from utils import HEIGHT


# Класс стороннего игрока
class Other(Player):
    def __init__(self, group, playerpos, mypos, delta, nick, col, item):
        self.ready = False
        super().__init__(group)
        new = pg.Surface((50, 75), pg.SRCALPHA)
        new.blit(self.image, (0, 25))
        font = pg.font.Font(None, 20)
        text = font.render(nick, True, (0, 0, 0))
        new.blit(text, (0, 0))
        self.image = new
        self.dx, self.dy = 0, 0
        self.rect.x = (mypos[0] - playerpos[0] + 15) * 50 - int(delta[0])
        self.rect.y = HEIGHT - (mypos[1] - playerpos[1] + 7) * 50 - int(delta[1]) - 25
        self.coords = mypos
        self.goal = []
        self.knock = 0
        self.ready = True

    def update(self, tick, pdelta, playerpos):
        if not self.ready:
            return
        if self.goal:
            data = self.goal[0]
            self.goal = self.goal[1:]
            self.dx, self.dy = data[2], data[3]
            self.coords = [data[0], data[1]]
        self.rect.x = (self.coords[0] - playerpos[0] + 15) * 50 - int(pdelta[0]) + self.dx
        self.rect.y = HEIGHT - (self.coords[1] - playerpos[1] + 7) * 50 - int(pdelta[1]) + self.dy - 25

    def move(self, act):
        self.ready = False
        self.goal += [[int(i) for i in act.split()]]
        self.ready = True