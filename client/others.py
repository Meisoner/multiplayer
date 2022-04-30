import pygame as pg
from player import Player
from block import HEIGHT


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
        self.ready = True

    def update(self, move, tick):
        if not self.ready:
            return
        self.dx += move[0]
        self.dy -= move[1]
        if self.goal:
            self.dx -= self.goal[0][0]
            self.dy -= self.goal[0][1]
            self.goal = self.goal[1:]
        if abs(self.dx) >= 1:
            self.rect.x += int(self.dx)
            self.dx -= int(self.dx)
        if abs(self.dy) >= 1:
            self.rect.y += int(self.dy)
            self.dy -= int(self.dy)

    def move(self, type, act):
        self.ready = False
        if self.goal:
            if not self.goal[-1][0] and type == 1:
                self.goal[-1][0] = act
            elif not self.goal[-1][1] and type == 2:
                self.goal[-1][1] = act
            elif type == 1:
                self.goal += [[act, 0]]
            elif type == 2:
                self.goal += [[0, act]]
        elif type == 1:
            self.goal += [[act, 0]]
        elif type == 2:
            self.goal += [[0, act]]
        self.ready = True