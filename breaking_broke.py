import argparse
import collections
import contextlib
import itertools
import math
import os
import random

from pathlib import Path

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    import pygame as pg

class Clock:

    def __init__(self, framerate):
        self.framerate = framerate
        self._clock = pg.time.Clock()

    def tick(self):
        self._clock.tick(self.framerate)


class Engine:

    def __init__(self, clock, screen, state):
        self.clock = clock
        self.screen = screen
        self.state = state

    def run(self):
        running = True
        while running:
            ms = self.clock.tick()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                else:
                    self.state.handle(event)
            self.state.update(ms)
            self.screen.fill((0,0,0))
            self.state.draw(self.screen)
            pg.display.flip()


class BreakingBroke:

    def __init__(self):
        self.font = pg.font.Font(None, 200)
        self.colors = list(itertools.permutations((10,10,200)))
        self.colors.extend(itertools.permutations((10,200,200)))
        self.shuffle_colors()
        self.init_broken()

    def shuffle_colors(self):
        random.shuffle(self.colors)
        self.colors_queue = collections.deque(self.colors)

    def init_broken(self):
        if not self.colors_queue:
            self.shuffle_colors()
        self.textimage = self.font.render('BROKEN', True, self.colors_queue.popleft())
        self.broken = breakimage(self.textimage)

    def draw(self, surf):
        rect = self.textimage.get_rect()
        surf.blit(self.textimage, rect)
        pg.draw.rect(surf, (200, 10, 10), rect, 1)

        rect = self.broken.get_rect(topleft = rect.bottomleft)
        surf.blit(self.broken, rect)
        pg.draw.rect(surf, (200, 10, 10), rect, 1)

    def handle(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.event.post(pg.event.Event(pg.QUIT))
            elif event.key == pg.K_SPACE:
                self.init_broken()

    def update(self, ms):
        pass


def breakmasks(size, arcmin=5, arcmax=20):
    """
    Generate random image masks of rays from center.
    """
    rect = pg.Rect((0, 0), size)
    length = max(size) * 2
    color = (255, 255, 255)
    start = end = 0
    while end != 360:
        end = random.choice(range(start + arcmin, start + arcmax))
        if end > 360:
            end = 360
        start_radians = math.radians(start)
        end_radians = math.radians(end)
        points = (
            rect.center,
            (rect.centerx + math.cos(start_radians) * length,
             rect.centery - math.sin(start_radians) * length),
            (rect.centerx + math.cos(end_radians) * length,
             rect.centery - math.sin(end_radians) * length)
        )
        mask = pg.Surface(size, pg.SRCALPHA)
        pg.draw.polygon(mask, color, points, 0)
        yield mask
        start = end

def breakimage(source, shake=5):
    """
    Return a "broken" image of the source.
    """
    flags = pg.BLEND_RGBA_MULT
    size = source.get_size()
    result = pg.Surface(size, pg.SRCALPHA)
    masks = breakmasks(size)
    for mask in masks:
        temp = pg.Surface(size, pg.SRCALPHA)
        pos = (random.choice(range(-shake, shake+1)), random.choice(range(-shake, shake+1)))
        temp.blit(source, pos)
        temp.blit(mask, (0, 0), special_flags=flags)
        result.blit(temp, (0, 0))
    return result

def main(argv=None):
    """
    Python version of "Breaking Broke" by frankforce.com (Killed By A Pixel).
    """
    # Reference:
    # http://frankforce.com/?p=6766
    parser = argparse.ArgumentParser(
        prog=Path(__file__).stem, description=main.__doc__)
    parser.add_argument('--xres', type=int, default=800,
                        help='Horizontal resolution. [%(default)s]')
    parser.add_argument('--yres', type=int, default=600,
                        help='Vertical resolution. [%(default)s]')
    parser.add_argument('--fps', type=int, default=60,
                        help='Frames per second. [%(default)s]')
    args = parser.parse_args(argv)
    size = (args.xres, args.yres)
    pg.init()
    clock = Clock(args.fps)
    screen = pg.display.set_mode(size)
    breakingbroke = BreakingBroke()
    engine = Engine(clock, screen, breakingbroke)
    engine.run()

if __name__ == '__main__':
    main()
