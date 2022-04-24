import requests as rq
import pygame as pg
import threading
from time import sleep
from block import Block
from player import Player
from detectors import FallDetector, JumpDetector, RightDetector, LeftDetector, FallLeftDetector, FallRightDetector
from particles import Particle
from hotbar import Cell
from utils import searchinv
from block import HEIGHT
from others import Other
from independent_screens import pause, inventoryview, crafting
# from random import randrange as rr


SERVER = 'http://127.0.0.1:5000/'
# SERVER = 'http://192.168.1.72:5000/'
# r, g = rr(100), rr(100)
# b = rr(max(r, g) + 50, 255)
BLUE = (83, 75, 222)
# (9, 94, 180) (87, 88, 191)
sss = rq.Session()
actions = []


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
    global blocks, pos, sss, token, delta, broken, placed, stop
    while True:
        sleep(1)
        map = sss.get(SERVER + 'get_blocks/' + token).json()
        if map[0] == 'err':
            break
        new = pg.sprite.Group()
        for i in broken:
            sss.get(SERVER + f'break/{token}/{i[0]}/{i[1]}')
        for i in placed:
            if (i[1], i[2]) not in broken:
                sss.get(SERVER + f'place/{token}/{i[0]}/{i[1]}/{i[2]}')
        dbackup = delta[:]
        for i in placed:
            if (i[1], i[2]) not in broken:
                Block(new, dbackup, textures[i[0]], pos, (i[1], i[2]), False, i[0])
        for i in map[0]:
            if (i[1], i[2]) in broken:
                continue
            Block(new, dbackup, textures[i[0]], pos, (i[1], i[2]), False, i[0])
        for i in map[1]:
            Block(new, dbackup, textures[i[0]], pos, (i[1], i[2]), True, i[0])
        broken.clear()
        placed.clear()
        stop = True
        blocks = new
        stop = False


def playerdataexchanger():
    global pos, sss, token, others, delta, blocks, actions
    while True:
        sleep(1)
        try:
            la = len(actions)
            np = sss.post(SERVER + 'action', json={'actions': actions[:la], 'token': token}).json()
            if abs(np[0] - pos[0]) > 5 or abs(np[1] - pos[1]) > 5:
                pos = np
            actions = actions[la:]
            oth = sss.get(SERVER + f'players/{token}').json()
            pids = set()
            for i in oth:
                pids.add(i['id'])
                if i['id'] not in others[1].keys():
                    others[1][i['id']] = Other(others[0], pos, i['pos'], delta, i['name'], False, False)
                elif not others[1][i['id']]:
                    others[1][i['id']] = Other(others[0], pos, i['pos'], delta, i['name'], False, False)
                else:
                    if others[1][i['id']].get_pos() != tuple(i['pos']):
                        for j in i['acts']:
                            if j[0] == 1 or j[0] == 2:
                                others[1][i['id']].move(j[0], j[1])
            for i in others[1].keys():
                if i not in pids and others[1][i]:
                    others[1][i].remove(others[0])
                    others[1][i] = False
        except Exception:
            pass


def update_inv():
    global token, inventory
    newinv = sss.get(SERVER + f'get_inv/{token}').json()
    if newinv != inventory:
        inventory = newinv
        for i in range(5):
            if inventory[i][1]:
                hotlist[i].placeitem(inventory[i][0], inventory[i][1])
            else:
                hotlist[i].rmitem()


pg.init()
scr = pg.display.set_mode(size := (1500, HEIGHT))
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
broken, placed = [], []
last = []
particles, partlist = pg.sprite.Group(), []
mpos = (0, 0)
others = [pg.sprite.Group(), dict()]
inventory = [[0, 0] for _ in range(20)]
stop = False
othermove = [0, 0]
blockdelta = [0, 0]
crafts, pos = False, False
while run:
    try:
        tick = clock.tick()
        scr.fill(BLUE)
        if place == 'login':
            token = login(scr)
            if place == 'in_game':
                map = sss.get(SERVER + 'get_blocks/' + token).json()
                pos = sss.get(SERVER + 'get_pos/' + token).json()
                map[0] += [[num, pos[0], pos[1] - 1]]
                for i in map[0]:
                    Block(blocks, delta, textures[i[0]], pos, (i[1], i[2]), False, i[0])
                for i in map[1]:
                    Block(blocks, delta, textures[i[0]], pos, (i[1], i[2]), True, i[0])
                bdats.start()
                pdats.start()
                update_inv()
                crafts = sss.get(SERVER + 'crafts').json()
                print(crafts)
        elif place == 'noserver':
            noserver(scr)
        else:
            blocks.draw(scr)
            player.draw(scr)
            particles.draw(scr)
            hotbar.draw(scr)
            others[0].draw(scr)
            if pg.sprite.spritecollideany(falld, blocks):
                falling = False
                usk = 5
            elif not (jumping or stop):
                falling = True
            if falling:
                particles.update(0, False, 0, tick / usk)
                blockdelta[1] -= tick / usk
                othermove[1] += tick / usk
                delta[1] += tick / usk
                if usk > 3:
                    usk *= 0.999
                if delta[1] >= 50:
                    pos[1] -= 1
                    actions += [(0, 3)]
                    delta[1] -= 50
            elif jumping:
                particles.update(0, False, 0, -1 * tick / 5)
                blockdelta[1] += tick / 5
                othermove[1] -= tick / 5
                delta[1] -= tick / 5
                jumping -= tick / 5
                if jumping < 1 or pg.sprite.spritecollideany(jumpd, blocks):
                    jumping = 0
                    falling = True
                if delta[1] <= -50:
                    pos[1] += 1
                    actions += [(0, 2)]
                    delta[1] += 50
        if blocks:
            pg.display.flip()
        lf, rt = 0, 0
        if right:
            if not (pg.sprite.spritecollideany(rightd, blocks) or (pg.sprite.spritecollideany(frd, blocks)
                                                                   and falling)):
                blockdelta[0] -= tick / 5
                othermove[0] -= tick / 5
                delta[0] += tick / 5
                rt = 1
                if delta[0] > 50:
                    pos[0] += 1
                    actions += [(0, 1)]
                    delta[0] -= 50
        elif left:
            if not (pg.sprite.spritecollideany(leftd, blocks) or (pg.sprite.spritecollideany(fld, blocks) and falling)):
                othermove[0] += tick / 5
                delta[0] -= tick / 5
                blockdelta[0] += tick / 5
                lf = 1
                if delta[0] < -50:
                    pos[0] -= 1
                    actions += [(0, 0)]
                    delta[0] += 50
        for i in partlist:
            px, py, col = i
            for j in range(200):
                Particle(particles, col, (px, py))
        partlist.clear()
        particles.update(tick, blocks, 2 * rt - lf + 1, False)
        others[0].update(othermove, tick)
        othermove = [0, 0]
        bmove = [0, 0]
        if abs(blockdelta[0]) >= 1:
            bmove[0] += int(blockdelta[0])
            actions += [(1, int(blockdelta[0]))]
            blockdelta[0] -= int(blockdelta[0])
        if abs(blockdelta[1]) >= 1:
            bmove[1] += int(blockdelta[1])
            actions += [(2, int(blockdelta[1]))]
            blockdelta[1] -= int(blockdelta[1])
        blocks.update(False, bmove)
        for i in pg.event.get():
            if i.type == pg.QUIT:
                sss.get(SERVER + 'exit/' + token)
                run = False
            elif i.type == pg.MOUSEBUTTONDOWN:
                if i.button == pg.BUTTON_LEFT:
                    blocks.update((i.pos[0], i.pos[1], broken, partlist, last), False)
                    if last:
                        slot = searchinv(inventory, last[0])
                        if slot != -1 and slot < 5:
                            hotlist[slot].placeitem(last[0], hotlist[slot].getamount() + 1)
                            inventory[slot][0] = last[0]
                            inventory[slot][1] += 1
                        last = []
                elif i.button == pg.BUTTON_RIGHT:
                    if any([j.check(i.pos) for j in blocks]):
                        pass
                    elif inventory[hand][1] and not ((i.pos[0] // 50, i.pos[1] // 50) == (15, 9) or falling or jumping):
                        scrx, scry = i.pos
                        bx = (scrx + int(delta[0])) // 50 - 15 + pos[0]
                        by = (size[1] - scry - int(delta[1])) // 50 + pos[1] - 6
                        if (bx, by) not in broken:
                            block = inventory[hand][0]
                            Block(blocks, delta, textures[block], pos, (bx, by), False, block)
                            placed += [[block, bx, by]]
                            inventory[hand][1] -= 1
                            if inventory[hand][1]:
                                hotlist[hand].placeitem(hotlist[hand].getitem(), inventory[hand][1])
                            else:
                                hotlist[hand].rmitem()
            elif i.type == pg.KEYDOWN:
                if i.key == pg.K_RIGHT or i.key == pg.K_d:
                    right = True
                    player_spr.turn(True)
                elif i.key == pg.K_LEFT or i.key == pg.K_a:
                    left = True
                    player_spr.turn(False)
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
                elif i.key == pg.K_i or i.key == pg.K_e:
                    left, right, falling, jumping = False, False, False, 0
                    update_inv()
                    if i.key == pg.K_i:
                        inventory, moved = inventoryview(scr, inventory, minitextures)
                        sss.post(SERVER + 'get_inv/' + token, json={'moved': moved})
                    else:
                        crafting(scr, textures, crafts, lambda x: sss.get(SERVER + 'craft/' + token + '/' + str(x)))
                        update_inv()
                    for i in range(5):
                        if inventory[i][1]:
                            hotlist[i].placeitem(inventory[i][0], inventory[i][1])
                        else:
                            hotlist[i].rmitem()
                elif i.key == pg.K_ESCAPE:
                    left, right, falling, jumping = False, False, False, 0
                    pause(scr)
            elif i.type == pg.KEYUP:
                if i.key == pg.K_RIGHT or i.key == pg.K_d:
                    right = False
                elif i.key == pg.K_LEFT or i.key == pg.K_a:
                    left = False
            elif i.type == pg.MOUSEMOTION:
                mpos = i.pos
    except Exception as ex:
        raise ex