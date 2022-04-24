import pygame as pg
from block import Block


class special(Block):
    def __init__(self, group, delta, image, playerpos, blockpos, protected, id, data):
        super().__init__(group, delta, image, playerpos, blockpos, protected, id)