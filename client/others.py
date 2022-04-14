import pygame as pg
from player import Player
from block import HEIGHT


class Other(Player):
    def __init__(self, group, playerpos, mypos, delta, nick, col, item):
        super().__init__(group)
        self.image = self.image
        self.rect.x = (mypos[0] - playerpos[0] + 15) * 50 - int(delta[0])
        self.rect.y = HEIGHT - (mypos[1] - playerpos[1] + 7) * 50 - int(delta[1])
        self.coords = tuple(mypos)
        self.dx, self.dy = 0, 0

    def update(self, move):
        self.dx += move[0]
        self.dy -= move[1]
        if abs(self.dx) >= 1:
            self.rect.x += int(self.dx)
            self.dx -= int(self.dx)
        if abs(self.dy) >= 1:
            self.rect.y += int(self.dy)
            self.dy -= int(self.dy)

    def move(self, playerpos, mypos, delta):
        self.rect.x = (mypos[0] - playerpos[0] + 15) * 50 - int(delta[0])
        self.rect.y = HEIGHT - (mypos[1] - playerpos[1] + 7) * 50 - int(delta[1])
        self.coords = tuple(mypos)

    def get_pos(self):
        return self.coords