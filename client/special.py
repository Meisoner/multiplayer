import pygame as pg
from block import Block


# Планируется добавить возможность создания специальных блоков с особыми свойствами (например, контейнеры или жидкости).
# Они будут реализованы в ближайшем будущем.
class special(Block):
    def __init__(self, group, delta, image, playerpos, blockpos, protected, id, data):
        super().__init__(group, delta, image, playerpos, blockpos, protected, id)