from random import randrange as rr


def generator(x, height):
    res = []
    if True:
        template = tree()
    for i in template[0]:
        res += [f'INSERT INTO Map(block, x, y) VALUES({i[0]}, {i[1] + x}, {i[2] + height + 1})']
    return res, template[1]


def tree():
    height = rr(4, 6)
    length = height - height % 2 + 1
    res = [(4, length // 2, i) for i in range(height)]
    res += [(3, length // 2, height)]
    n = 0
    for i in range(height, 0, -1):
        n += 1
        if n > length // 2 + 1:
            break
        for j in range(n):
            res += [(3, length // 2 - j - 1, i)]
            res += [(3, length // 2 + j + 1, i)]
    return res, length