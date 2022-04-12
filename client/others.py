import pygame as pg
from player import Player
from block import HEIGHT


class Other(Player):
    def __init__(self, group, playerpos, mypos, delta, col, item):
        super().__init__(group)
        self.rect.x = (mypos[0] - playerpos[0] + 15) * 50 - int(delta[0])
        self.rect.y = HEIGHT - (mypos[1] - playerpos[1] + 7) * 50 - int(delta[1])
        self.coords = tuple(mypos)

    def update(self):
        pass