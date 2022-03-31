import requests as rq
import pygame as pg
import threading
from time import sleep
from block import Block
from player import Player
from detectors import FallDetector, JumpDetector, RightDetector, LeftDetector, FallLeftDetector, FallRightDetector
from particles import Particle
from hotbar import Cell


SERVER = 'http://127.0.0.1:5000/'
sss = rq.Session()


def login(screen):
    global run, place
    keys = {getattr(pg, 'K_' + str(key)): str(key) for key in list(range(10)) + [chr(ord('a') + j) for j in range(26)]}
    keys[pg.K_PERIOD] = '.'
    keys[pg.K_SPACE] = ' '
    text = ['', '']
    font = pg.font.Font(None, 30)
    title = font.render('Добро пожаловать в игру!', True, (255, 255, 255))
    nick = font.render('Введите ник:', True, (255, 255, 255))
    pswd = font.render('Введите пароль:', True, (255, 255, 255))
    x, y = size
    textsize = 2 * x // 3
    textcenter = x // 2 - textsize // 2
    titlesize = title.get_size()[0]
    titlecenter = x // 2 - titlesize // 2
    inp = 0
    err = ''
    while True:
        for i in pg.event.get():
            if i.type == pg.QUIT:
                run = False
                return
            if i.type == pg.MOUSEBUTTONDOWN:
                p = i.pos
                if 350 <= p[0] <= 1350 and 150 <= p[1] <= 190:
                    inp = 1
                elif 350 <= p[0] <= 1350 and 50 <= p[1] <= 90:
                    inp = 0
            elif i.type == pg.KEYDOWN:
                if i.key in keys.keys():
                    text[inp] += keys[i.key]
                elif i.key == pg.K_BACKSPACE:
                    text[inp] = text[inp][:-1]
                elif i.key == pg.K_RETURN and all(text):
                    rback = sss.get(SERVER + f'token/{text[1]}/{text[0]}').json()
                    if rback[0] == 'err':
                        err = rback[1]
                    elif rback[0] == 'ok':
                        place = 'in_game'
                        return rback[1]
                elif i.key == pg.K_RETURN:
                    inp = 1 - inp
        screen.fill((70, 80, 130))
        pg.draw.rect(screen, (255, 255, 255), (textcenter + 100, 50, textsize, 40))
        pg.draw.rect(screen, (255, 255, 255), (textcenter + 100, 150, textsize, 40))
        label_nick = font.render(text[0] + '|' * (1 - inp), True, (0, 0, 0))
        label_psw = font.render('*' * len(text[1]) + '|' * inp, True, (0, 0, 0))
        label_err = font.render(err, True, (255, 0, 0))
        screen.blit(label_nick, (textcenter + 100, 50))
        screen.blit(label_psw, (textcenter + 100, 150))
        screen.blit(nick, (textcenter - 100, 60))
        screen.blit(pswd, (textcenter - 100, 160))
        screen.blit(title, (titlecenter, 10))
        errrect = label_err.get_rect()
        errcenter = size[0] // 2 - errrect[2] // 2
        screen.blit(label_err, (errcenter, 400))
        pg.display.flip()


def noserver(screen):
    global run
    timerun = True
    font = pg.font.Font(None, 80)
    warn = font.render('Отсутствует подключение к игровому серверу.', True, (255, 255, 255))
    rect = warn.get_rect()
    while timerun:
        screen.fill((255, 0, 0))
        screen.blit(warn, (size[0] // 2 - rect[2] // 2, size[1] // 2 - rect[3] // 2))
        pg.display.flip()
        for i in pg.event.get():
            if i.type in [pg.KEYDOWN, pg.MOUSEBUTTONDOWN, pg.QUIT]:
                run = False
                return


def blockdataexchanger():
    global blocks, pos, sss, token, delta, broken
    while True:
        sleep(1)
        map = sss.get(SERVER + 'get_blocks/' + token).json()
        if map[0] == 'err':
            break
        new = pg.sprite.Group()
        for i in broken:
            sss.get(SERVER + f'break/{token}/{i[0]}/{i[1]}')
        dbackup = delta[:]
        for i in map[0]:
            if (i[1], i[2]) in broken:
                continue
            Block(new, dbackup, textures[i[0]], pos, (i[1], i[2]), False)
        for i in map[1]:
            Block(new, dbackup, textures[i[0]], pos, (i[1], i[2]), True)
        broken.clear()
        blocks = new


def playerdataexchanger():
    global pos, inventory, sss, token, delta, others, hotlist
    while True:
        sleep(1)
        sss.get(SERVER + f'update_pos/{token}/{pos[0]}/{pos[1]}')
        newinv = sss.get(SERVER + f'get_inv/{token}').json()
        if newinv != inventory:
            inventory = newinv
            for i in range(5):
                if inventory[i][1]:
                    hotlist[i].placeitem(inventory[i][0], inventory[i][1])
                else:
                    hotlist[i].rmitem()


pg.init()
scr = pg.display.set_mode(size := (1500, 800))
stat = ''
try:
    stat = sss.get(SERVER + 'game_status').json()
except Exception:
    pass
if stat == 'Working':
    place = 'login'
else:
    place = 'noserver'
run = True
token = ''
num = 0
textures = []
while run:
    try:
        textures += [pg.image.load('textures/' + str(num) + '.png')]
        num += 1
    except Exception:
        run = False
minitextures = []
for i in textures:
    minitextures += [pg.transform.scale(i, (30, 30))]
textures += [pg.Surface((50, 50), pg.SRCALPHA)]
hotbar, hotlist = pg.sprite.Group(), []
for i in range(5):
    hotlist += [Cell(hotbar, i, minitextures)]
hotlist[0].choose()
hand = 0
run = True
bdats = threading.Thread(target=blockdataexchanger)
bdats.setDaemon(True)
pdats = threading.Thread(target=playerdataexchanger)
pdats.setDaemon(True)
blocks = pg.sprite.Group()
delta = [0, 0]
clock = pg.time.Clock()
left, right = [False] * 2
player = pg.sprite.Group()
player_spr = Player(player)
falld, jumpd, rightd, leftd = FallDetector(), JumpDetector(), RightDetector(), LeftDetector()
frd, fld = FallRightDetector(), FallLeftDetector()
falling, jumping = False, 0
usk = 5
broken = []
particles, partlist = pg.sprite.Group(), []
mpos = (0, 0)
others = []
inventory = [0] * 20
while run:
    try:
        tick = clock.tick()
        scr.fill((70, 80, 130))
        if place == 'login':
            token = login(scr)
            if place == 'in_game':
                map = sss.get(SERVER + 'get_blocks/' + token).json()
                pos = sss.get(SERVER + 'get_pos/' + token).json()
                map[0] += [[num, pos[0], pos[1] - 1]]
                for i in map[0]:
                    Block(blocks, delta, textures[i[0]], pos, (i[1], i[2]), False)
                for i in map[1]:
                    Block(blocks, delta, textures[i[0]], pos, (i[1], i[2]), True)
                bdats.start()
                pdats.start()
        elif place == 'noserver':
            noserver(scr)
        else:
            blocks.draw(scr)
            player.draw(scr)
            particles.draw(scr)
            hotbar.draw(scr)
            if pg.sprite.spritecollideany(falld, blocks):
                falling = False
                usk = 5
            elif not jumping:
                falling = True
            if falling:
                particles.update(0, False, 0, tick / usk)
                blocks.update(False, (0, tick / usk))
                delta[1] += tick / usk
                if usk > 3:
                    usk *= 0.999
                if delta[1] >= 50:
                    pos[1] -= 1
                    delta[1] -= 50
            elif jumping:
                particles.update(0, False, 0, -1 * tick / 5)
                blocks.update(False, (0, -1 * tick / 5))
                delta[1] -= tick / 5
                jumping -= tick / 5
                if jumping < 1 or pg.sprite.spritecollideany(jumpd, blocks):
                    jumping = 0
                    falling = True
                if delta[1] <= -50:
                    pos[1] += 1
                    delta[1] += 50
        if blocks:
            pg.display.flip()
        lf, rt = 0, 0
        if right:
            if not (pg.sprite.spritecollideany(rightd, blocks) or (pg.sprite.spritecollideany(frd, blocks)
                                                                   and falling)):
                blocks.update(False, (-1 * tick / 5, 0))
                delta[0] += tick / 5
                rt = 1
                if delta[0] >= 50:
                    pos[0] += 1
                    delta[0] -= 50
        elif left:
            if not (pg.sprite.spritecollideany(leftd, blocks) or (pg.sprite.spritecollideany(fld, blocks) and falling)):
                blocks.update(False, (tick / 5, 0))
                delta[0] -= tick / 5
                lf = 1
                if delta[0] <= -50:
                    pos[0] -= 1
                    delta[0] += 50
        for i in partlist:
            px, py, col = i
            for j in range(200):
                Particle(particles, col, (px, py))
        partlist.clear()
        particles.update(tick, blocks, 2 * rt - lf + 1, False)
        for i in pg.event.get():
            if i.type == pg.QUIT:
                sss.get(SERVER + 'exit/' + token)
                run = False
            elif i.type == pg.MOUSEBUTTONDOWN:
                if i.button == pg.BUTTON_LEFT:
                    blocks.update((i.pos[0], i.pos[1], broken, partlist), False)
                elif i.button == pg.BUTTON_RIGHT:
                    scrx, scry = i.pos
                    bx = (scrx + int(delta[0])) // 50 - 15 + pos[0]
                    by = (size[1] - scry - int(delta[1])) // 50 + pos[1] - 6
                    Block(blocks, delta, textures[0], pos, (bx, by), False)
            elif i.type == pg.KEYDOWN:
                if i.key == pg.K_RIGHT or i.key == pg.K_d:
                    right = True
                elif i.key == pg.K_LEFT or i.key == pg.K_a:
                    left = True
                elif i.key == pg.K_SPACE and not (falling or jumping):
                    jumping = 60
                elif (i.key == pg.K_UP or i.key == pg.K_w) and hand < 4:
                    hotlist[hand].choose()
                    hand += 1
                    hotlist[hand].choose()
                elif (i.key == pg.K_DOWN or i.key == pg.K_s) and hand:
                    hotlist[hand].choose()
                    hand -= 1
                    hotlist[hand].choose()
            elif i.type == pg.KEYUP:
                if i.key == pg.K_RIGHT or i.key == pg.K_d:
                    right = False
                elif i.key == pg.K_LEFT or i.key == pg.K_a:
                    left = False
            elif i.type == pg.MOUSEMOTION:
                mpos = i.pos
    except Exception as ex:
        raise ex