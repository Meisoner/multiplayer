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
    while rn2:
        screen.blit(fn, (0, 0))
        pg.draw.rect(screen, (255, 255, 255), (avx - 50, 100, 100, 40))
        pg.display.flip()
        for i in pg.event.get():
            if i.type == pg.KEYDOWN:
                if i.key == pg.K_ESCAPE:
                    return