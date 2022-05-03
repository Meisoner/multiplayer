from random import randrange as rr


# Функция, обеспечивающая генерацию строений в мире
def generator(x, height, rev):
    res = []
    if rr(30):
        template = tree()
    else:
        template = house()
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


# Строение: Дерево
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


# Строение: Заброшенный дом
def house():
    w = 2 * rr(3) + 7
    h = rr(3) + 6
    res = [(4, 0, 0), (4, w - 1, 0), (5, w - 1, 1), (4, 0, h - 1), (4, w - 1, h - 1)]
    for y in range(2, h - 1):
        res += [(5, 0, y)]
        res += [(5, w - 1, y)]
    for x in range(w - 2):
        res += [(5, x + 1, 0)]
        res += [(5, x + 1, h - 1)]
    ln = 1
    for y in range((w - 1) // 2):
        for x in range(ln, w - ln):
            res += [(4, x, h + y)]
        ln += 1
    for i in range(len(res)):
        if not rr(6):
            if res[i][0] == 5:
                res[i] = 7, res[i][1], res[i][2]
            else:
                res[i] = 10, res[i][1], res[i][2]
    return res