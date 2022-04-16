import pygame as pg
from player import Player
from block import HEIGHT


class Other(Player):
    def __init__(self, group, playerpos, mypos, delta, nick, col, item):
        super().__init__(group)
        self.image = self.image
        self.dx, self.dy = 0, 0
        self.rect.x = (mypos[0] - playerpos[0] + 15) * 50 - int(delta[0])
        self.rect.y = HEIGHT - (mypos[1] - playerpos[1] + 7) * 50 - int(delta[1])
        self.coords = tuple(mypos)
        self.goal = []

    def update(self, move, tick):
        self.dx += move[0]
        self.dy -= move[1]
        if self.goal:
            if abs(self.goal[0][0]) > 1:
                if self.goal[0][0] > 0:
                    self.goal[0][0] -= tick / 5
                    self.dx += tick / 5
                else:
                    self.goal[0][0] += tick / 5
                    self.dx -= tick / 5
            elif abs(self.goal[0][1]) > 1:
                self.dx += self.goal[0][0]
                self.goal[0][0] = 0
                if self.goal[0][1] < 0:
                    self.goal[0][1] += tick / 5
                    self.dy -= tick / 5
                else:
                    self.goal[0][1] -= tick / 5
                    self.dy += tick / 5
            else:
                self.dy += self.goal[0][1]
                self.goal[0][1] = 0
                self.goal = self.goal[1:]
        if abs(self.dx) >= 1:
            self.rect.x += int(self.dx)
            self.dx -= int(self.dx)
        if abs(self.dy) >= 1:
            self.rect.y += int(self.dy)
            self.dy -= int(self.dy)

    def move(self, playerpos, mypos, delta):
        tox = (mypos[0] - playerpos[0] + 15) * 50 - int(delta[0]) - self.rect.x
        toy = HEIGHT - (mypos[1] - playerpos[1] + 7) * 50 - int(delta[1]) - self.rect.y
        self.goal += [[tox, toy]]
        self.coords = tuple(mypos)

    def get_pos(self):
        return self.coords