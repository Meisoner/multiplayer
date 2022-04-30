from random import randrange as rr
import pygame as pg
from math import cos, pi


# Класс частицы ломания блока
class Particle(pg.sprite.Sprite):
    def __init__(self, group, col, pos):
        super().__init__(group)
        self.lifetime = rr(500)
        im = pg.Surface((rr(3) + 1, rr(3) + 1))
        im.fill(col)
        self.image = im
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = [i + rr(50) for i in pos]
        self.angle = pi * (rr(120) + 210) / 180
        self.dx, self.dy = 0, 0
        self.usk = 0.2

    def update(self, tick, blocks, napr, up):
        if up:
            self.dy -= up
        else:
            self.lifetime -= tick
            if self.lifetime <= 0:
                self.remove(self.groups()[0])
            if napr == 0:
                self.dx += tick / 5
            elif napr == 3:
                self.dx -= tick / 5
            if not pg.sprite.spritecollideany(self, blocks):
                self.dx += cos(self.angle) * tick / 5
                self.dy += tick * self.usk
            self.usk += 0.001
        if abs(self.dx) >= 1:
                self.rect.x += int(self.dx)
                self.dx -= int(self.dx)
        if abs(self.dy) >= 1:
                self.rect.y += int(self.dy)
                self.dy -= int(self.dy)