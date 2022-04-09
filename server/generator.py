from random import randrange as rr


def generator(x, height, rev):
    res = []
    if True: # Здесь будет разбиение на разные генерации
        template = tree()
    if rev:
        mx = mn = x - template[0][1]
        for i in template:
            if x - i[1] > mx:
                mx = x - i[1]
            if x - i[1] < mn:
                mn = x - i[1]
            res += [f'INSERT INTO Map(block, x, y) VALUES({i[0]}, {x - i[1]}, {i[2] + height + 1})']
    else:
        mx = mn = x + template[0][1]
        for i in template:
            if x + i[1] > mx:
                mx = x + i[1]
            if x + i[1] < mn:
                mn = x + i[1]
            res += [f'INSERT INTO Map(block, x, y) VALUES({i[0]}, {x + i[1]}, {i[2] + height + 1})']
    return res, range(mn - 1, mx + 2)


def tree():
    height = rr(4, 6)
    length = height - height % 2 + 1
    res = [(4, length // 2 + 1, i) for i in range(height)]
    res += [(3, length // 2 + 1, height)]
    n = 0
    for i in range(height, 0, -1):
        n += 1
        if n > length // 2 + 1:
            break
        for j in range(n):
            res += [(3, length // 2 - j, i)]
            res += [(3, length // 2 + j + 2, i)]
    return res