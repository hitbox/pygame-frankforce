import argparse
import configparser
import contextlib
import math
import os
import weakref
from pathlib import Path

with contextlib.redirect_stdout(open(os.devnull,'w')):
    import pygame as pg

class Key:

    def __init__(self, code, cooldown):
        self.code = code
        self.cooldown = cooldown
        self.heat = 0

    def is_pressed(self, pressed):
        return pressed[self.code] and not self.heat

    def update(self):
        if self.heat > 0:
            self.heat -= 1


class KeyAttr:

    def __init__(self, key, attr, amount):
        self.key = key
        self.attr = attr
        self.amount = amount


class Keymap:

    def __init__(self, keyattrs, target):
        self.keyattrs = keyattrs
        self.target = target

    def update(self):
        for keyattr in self.keyattrs:
            keyattr.key.update()
        pressed = pg.key.get_pressed()
        mods = pg.key.get_mods()
        shift = mods & pg.KMOD_SHIFT
        sign = -1 if shift else 1
        for keyattr in self.keyattrs:
            if keyattr.key.is_pressed(pressed):
                value = getattr(self.target, keyattr.attr)
                setattr(self.target, keyattr.attr, value + sign * keyattr.amount)
                keyattr.key.heat = keyattr.key.cooldown


class RingWeave:

    def __init__(self, space):
        self.space = space
        self.color = (200, 200, 200)
        self.width = 1
        self.base = min(self.space.size) / 3
        self.closed = 0
        self.focus = 9
        self.nsteps = 3000
        self.nwaves = 4
        self.somevar = 159
        self.spread = self.base / 8 # 60

    def get_point(self, index, time):
        angle = index / self.somevar + time
        radius = (
            self.base
            + self.spread
            * math.sin(index / (self.nsteps / math.tau) + angle * self.nwaves)
            * (math.sin(angle - time) / 2 + 0.5) ** self.focus)
        x = self.space.centerx + math.cos(angle) * radius
        y = self.space.centery + math.sin(angle) * radius
        return (x, y)

    def draw(self, surf, time):
        points = [self.get_point(index, time) for index in range(self.nsteps)]
        self.draw_points(surf, points)
        #self.draw_circles(surf, points)

    def draw_points(self, surf, points):
        pg.draw.lines(surf, self.color, self.closed % 2, points, self.width)

    def draw_circles(self, surf, points):
        for i, point in enumerate(points):
            if i % 50 == 0:
                pg.draw.circle(surf, (200,10,10), tuple(map(int, point)), 20, 1)


def loop(clock, screen, size, fps, ringweave):
    space = screen.get_rect()
    font = pg.font.Font(None, int(min(size) / 18))
    font_color = (200, 200, 200)

    cooldown = 15 # frames
    keymap = Keymap(
            [
                KeyAttr(Key(pg.K_w, cooldown), 'width', 1),
                KeyAttr(Key(pg.K_n, cooldown), 'nsteps', 1),
                KeyAttr(Key(pg.K_b, cooldown), 'base', 1),
                KeyAttr(Key(pg.K_s, cooldown), 'spread', 1),
                KeyAttr(Key(pg.K_x, cooldown), 'somevar', 1),
                # when 0 the whole circle is wavey
                KeyAttr(Key(pg.K_f, cooldown), 'focus', 1),
                KeyAttr(Key(pg.K_c, cooldown), 'closed', 1),
                # seems to be the number of waves inside the focus
                KeyAttr(Key(pg.K_a, cooldown), 'nwaves', 1),
            ],
            ringweave,
        )

    time = 0
    while not pg.event.peek(pg.QUIT):
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_ESCAPE, pg.K_q):
                    pg.event.post(pg.event.Event(pg.QUIT))
                elif event.key == pg.K_r:
                    # reset
                    keymap.target = RingWeave(screen.get_rect())
        keymap.update()
        # clear
        screen.fill((0,0,0))
        # draw info
        rect = None
        for keyattr in keymap.keyattrs:
            value = getattr(keymap.target, keyattr.attr)
            text = f'{keyattr.attr}, {pg.key.name(keyattr.key.code)} +/-{keyattr.amount}: {value}'
            image = font.render(text, True, font_color)
            rect = image.get_rect(topright = rect.bottomright if rect else space.topright)
            screen.blit(image, rect)
        # draw ring weave
        keymap.target.draw(screen, time)

        pg.display.flip()
        seconds = clock.tick(fps) / 1000
        time += seconds

        pg.display.set_caption(f'{clock.get_fps():.2f}')

def prompt(msg, valid, caseinsensitive=True, default=None):
    valid = set(valid.lower() if caseinsensitive else valid)
    for value in valid:
        if value == '':
            raise ValueError('empty string not allowed as valid input')
    while True:
        answer = input(msg)
        if caseinsensitive:
            answer = answer.lower()
        if answer in valid or answer == '':
            if answer == '':
                answer = default
            break
        else:
            print('invalid input')
    return answer

def main(argv=None):
    """
    Ring Weave
    """
    # Reference:
    # http://frankforce.com/?p=6597
    parser = argparse.ArgumentParser(prog=Path(__file__).stem, description=main.__doc__)
    parser.add_argument('--xres', type=int, default=800,
                        help='Horizontal resolution. [%(default)s]')
    parser.add_argument('--yres', type=int, default=600,
                        help='Vertical resolution. [%(default)s]')
    parser.add_argument('--fps', type=int, default=60,
                        help='Target frames per second. [%(default)s]')
    parser.add_argument('--config', help='Load from config.')
    parser.add_argument('--yes', action='store_true', help='Always save config.')
    args = parser.parse_args(argv)
    size = (args.xres, args.yres)

    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode(size)
    ringweave = RingWeave(screen.get_rect())

    attrs = ['base', 'closed', 'focus', 'nsteps', 'nwaves', 'somevar', 'spread']
    if args.config:
        cp = configparser.ConfigParser()
        cp.read(args.config)
        for attr in attrs:
            fallback = getattr(ringweave, attr)
            value = cp.getint('ringweave', attr, fallback=fallback)
            setattr(ringweave, attr, value)

    loop(clock, screen, size, args.fps, ringweave)
    pg.quit()

    if (args.config
            and (args.yes or prompt('Save config? [y/N]> ', 'yn', default='n') == 'y')):
            for attr in attrs:
                cp['ringweave'][attr] = str(getattr(ringweave, attr))
            with open(args.config, 'w') as config_file:
                cp.write(config_file)


if __name__ == '__main__':
    main()
