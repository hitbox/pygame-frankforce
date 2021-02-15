import argparse
import contextlib
import math
import os

with contextlib.redirect_stdout(open(os.devnull,'w')):
    import pygame as pg

def clamp(x, min, max):
    if x > max:
        x = max
    elif x < min:
        x = min
    return x

class BlackHole:

    def __init__(self, nstars, size):
        self.nstars = nstars
        self.size = size
        self.center = (self.size[0] / 2, self.size[1] / 2)
        self.speed_up = 260
        self.voffset = .1 # .2
        self.deepness = 2e4
        self.star_scale = int(self.size[1] * .005) # 9

    def draw(self, time, surf):
        space = surf.get_rect()
        centerx, centery = self.center
        for i in range(1, self.nstars):
            color = (clamp(99 * i, 0, 255), clamp(2 * i, 0, 255), clamp(i, 0, 255))
            angle = self.speed_up * time / i + math.sin(i ** 3)
            x = centerx + i * math.sin(angle)
            y = centery + self.voffset * (2 * i * math.cos(angle) + self.deepness / i)
            s = math.sin(i) * self.star_scale
            rect = pg.Rect(x, y, s, s)
            if space.colliderect(rect):
                pg.draw.rect(surf, color, rect)


def loop(size, fps, nstars):
    clock = pg.time.Clock()
    screen = pg.display.set_mode(size)
    space = screen.get_rect()
    font = pg.font.Font(None, int(min(size) / 18))
    font_color = (200, 200, 200)

    blackhole = BlackHole(nstars, space.size)

    keymap = { pg.K_h: ('voffset', .005),
               pg.K_d: ('deepness', 100),
               pg.K_j: ('star_scale', .1),
               pg.K_s: ('speed_up', 1),
               pg.K_n: ('nstars', 1) }

    info = True
    time = 0
    padding = 5
    while not pg.event.peek(pg.QUIT):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_ESCAPE, ):
                    pg.event.post(pg.event.Event(pg.QUIT))
                elif event.key == pg.K_TAB:
                    info = not info

        pressed = pg.key.get_pressed()
        mods = pg.key.get_mods()
        direction = -1 if mods & pg.KMOD_SHIFT else 1
        for key, (attr, amount) in keymap.items():
            if pressed[key]:
                value = getattr(blackhole, attr) + direction * amount
                setattr(blackhole, attr, value)

        screen.fill((0,0,0))
        blackhole.draw(time, screen)

        if info:
            table = ( ('time', f'{time:.2f}'),
                      ('fps', f'{clock.get_fps():.2f}'),
                      ('nstars', f'{blackhole.nstars}'),
                      ('voffset', f'{blackhole.voffset:.2f}'),
                      ('deepness', f'{blackhole.deepness}'),
                      ('star_scale', f'{blackhole.star_scale:.2f}'),
                      ('speed_up', f'{blackhole.speed_up:.2f}') )
            label_width = 0
            value_width = 0
            height = 0
            images = []
            for label, value in table:
                label_image = font.render(label, True, font_color)
                value_image = font.render(value, True, font_color)
                images.append((label_image, value_image))
                if label_image.get_width() > label_width:
                    label_width = label_image.get_width()
                if value_image.get_width() > value_width:
                    value_width = value_image.get_width()
                height += max((label_image.get_height(), value_image.get_height()))
            rect = pg.Rect(0, 0, label_width + value_width + padding, height)
            rect.topright = space.inflate(-padding, -padding).topright
            y = rect.top
            for label_image, value_image in images:
                screen.blit(label_image, (label_image.get_rect(right=rect.centerx, y=y)))
                screen.blit(value_image, (value_image.get_rect(right=rect.right, y=y)))
                y += max((label_image.get_height(), value_image.get_height()))

        pg.display.flip()
        ms = clock.tick(fps)
        time += ms / 1000

def main(argv=None):
    """
    Mini Black Hole in pygame
    """
    # Reference:
    # http://frankforce.com/?p=637
    parser = argparse.ArgumentParser(prog='miniblackhole', description=main.__doc__)
    parser.add_argument('--xres', type=int, default=800,
                        help='Horizontal resolution. [%(default)s]')
    parser.add_argument('--yres', type=int, default=600,
                        help='Vertical resolution. [%(default)s]')
    parser.add_argument('--fps', type=int, default=60,
                        help='Target frames per second. [%(default)s]')
    parser.add_argument('--nstars', type=int, default=2000,
                        help='Number of stars. [%(default)s]')
    args = parser.parse_args(argv)
    pg.init()
    size = (args.xres, args.yres)
    loop(size, args.fps, args.nstars)

if __name__ == '__main__':
    main()
