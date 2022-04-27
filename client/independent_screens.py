import pygame as pg


def pause(screen):
    fn = screen.copy()
    screct = screen.get_rect()
    cover = pg.Surface((screct[2], screct[3]))
    pg.draw.rect(cover, (0, 0, 0), (0, 0, screct[2], screct[3]))
    cover.set_alpha(130)
    fn.blit(cover, (0, 0))
    rn2 = True
    avx = screct[2] // 2
    buttons = ['Продолжить']
    font = pg.font.Font(None, 30)
    screen.blit(fn, (0, 0))
    rects = []
    for i in range(len(buttons)):
        text = font.render(buttons[i], True, (0, 0, 0))
        tsize = text.get_rect()[2]
        pg.draw.rect(screen, (255, 255, 255), (avx - tsize // 2 - 10, 100 + 70 * i, tsize + 20, 40))
        rects += [(avx - tsize // 2 - 10, avx + tsize // 2 + 10, 100 + 70 * i, 140 + 70 * i)]
        screen.blit(text, (avx - tsize // 2, 105 + 70 * i))
    while rn2:
        pg.display.flip()
        button = 0
        for i in pg.event.get():
            if i.type == pg.QUIT:
                return
            if i.type == pg.KEYDOWN:
                if i.key == pg.K_ESCAPE:
                    return
            if i.type == pg.MOUSEBUTTONDOWN:
                if i.button == pg.BUTTON_LEFT:
                    for j in range(len(rects)):
                        if rects[j][0] <= i.pos[0] <= rects[j][1] and rects[j][2] <= i.pos[1] <= rects[j][3]:
                            button = j + 1
        if button:
            if button == 1:
                return


def inventoryview(screen, inv, textures):
    fn = screen.copy()
    screct = screen.get_rect()
    cover = pg.Surface((screct[2], screct[3]))
    pg.draw.rect(cover, (0, 0, 0), (0, 0, screct[2], screct[3]))
    cover.set_alpha(130)
    fn.blit(cover, (0, 0))
    rn2 = True
    avx = screct[2] // 2
    chosen = 0
    font = pg.font.Font(None, 20)
    stat = []
    while rn2:
        screen.blit(fn, (0, 0))
        pg.draw.rect(screen, (255, 255, 255), (avx - 125, 100, 250, 200))
        for i in range(6):
            pg.draw.rect(screen, (0, 0, 0), (avx - 125 + 50 * i, 100, 2, 200))
        for i in range(5):
            pg.draw.rect(screen, (0, 0, 0), (avx - 125, 100 + 50 * i, 250, 2))
        if chosen:
            coords = ((chosen - 1) % 5) * 50 + avx - 123, ((chosen - 1) // 5) * 50 + 102
            pg.draw.rect(screen, (120, 120, 120), (coords[0], coords[1], 48, 48))
        for i in range(20):
            if inv[i][1]:
                coords = (i % 5) * 50 + avx - 114, (i // 5) * 50 + 110
                screen.blit(textures[inv[i][0]], coords)
                amounttext = font.render(str(inv[i][1]), True, (0, 0, 0))
                screen.blit(amounttext, (coords[0] - 8, coords[1] - 8))
        pg.display.flip()
        for i in pg.event.get():
            if i.type == pg.KEYDOWN:
                if i.key == pg.K_ESCAPE or i.key == pg.K_i:
                    return inv, stat
            elif i.type == pg.MOUSEBUTTONDOWN:
                if i.button == pg.BUTTON_LEFT:
                    xc1 = (i.pos[0] - avx + 125) // 50
                    yc1 = (i.pos[1] - 100) // 50
                    if xc1 > 4 or yc1 > 3 or xc1 < 0 or yc1 < 0:
                        chosen = 0
                    elif not chosen:
                        chosen = yc1 * 5 + xc1 + 1
                        print(chosen - 1)
                    else:
                        inv[yc1 * 5 + xc1], inv[chosen - 1] = inv[chosen - 1], inv[yc1 * 5 + xc1]
                        stat += [(yc1 * 5 + xc1, chosen - 1)]
                        chosen = 0
            elif i.type == pg.QUIT:
                return inv, stat


def crafting(screen, textures, crafts, func):
    screct = screen.get_rect()
    rn2 = True
    avx = screct[2] // 2
    font = pg.font.Font(None, 50)
    stat = []
    title = font.render('Крафтинг', True, (0, 0, 0))
    tx = title.get_rect()[0] // 2
    msg = ''
    alph = 255
    while rn2:
        pg.draw.rect(screen, (255, 255, 255), (0, 0, screct[2], screct[3]))
        screen.blit(title, (avx - tx, 0))
        for n, k in enumerate(crafts.keys()):
            y = 55 * n + 50
            x = 0
            for j in crafts[k].keys():
                if int(j) != -1:
                    txt = font.render(str(crafts[k][j]), True, (0, 0, 0))
                    screen.blit(txt, (x, y))
                    x += txt.get_rect()[2] + 10
                    screen.blit(textures[int(j)], (x, y))
                    x += 60
            txt = font.render('->', True, (0, 0, 0))
            screen.blit(txt, (x, y))
            x += txt.get_rect()[2] + 10
            txt = font.render(str(crafts[k]['-1']), True, (0, 0, 0))
            screen.blit(txt, (x, y))
            x += txt.get_rect()[2] + 10
            screen.blit(textures[int(k)], (x, y))
            pg.draw.line(screen, (240, 240, 240), (0, y - 3), (screct[2], y - 3), 5)
        message = font.render(msg, True, (0, 0, 0))
        message.set_alpha(alph)
        alph -= 1
        screen.blit(message, (avx - message.get_rect()[2] // 2, screct[3] - message.get_rect()[3] - 10))
        pg.display.flip()
        for i in pg.event.get():
            if i.type == pg.QUIT:
                return
            elif i.type == pg.KEYDOWN:
                if i.key == pg.K_e:
                    return
            elif i.type == pg.MOUSEBUTTONDOWN:
                if i.button == pg.BUTTON_LEFT:
                    item = (i.pos[1] - 50) // 50
                    if 0 <= item < len(crafts.keys()):
                        msg = func(list(crafts.keys())[item]).json()[-1]
                        alph = 255