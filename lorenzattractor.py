import argparse
import contextlib
import math
import os
import time

from pathlib import Path

with contextlib.redirect_stdout(open(os.devnull,'w')):
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


class LorenzAttractor:

    def __init__(self):
        self.n = 500
        self.x_scale = 13
        self.y_offset = 28
        self.y_scale = 99
        self.z_scale = 39
        self.c_scale = 20
        self.d_scale = 23

    def draw(self, surf):
        x = y = z = 1
        a = b = c = d = 0
        for i in range(self.n):
            t = time.time()
            x += (y - x) / self.x_scale
            y += (self.y_offset - z) * x / self.y_scale
            z += (x * y - z) / self.z_scale
            c = int(400 + (x * math.cos(t) - y * math.sin(t)) * self.c_scale)
            d = int(900 - z * self.d_scale)
            if i > 0:
                pg.draw.line(surf, (200,200,200), (a,b), (c,d), 1)
            a, b = c, d

    def handle(self, event):
        if event.type == pg.KEYDOWN:
            if event.key in (pg.K_ESCAPE, pg.K_q):
                pg.event.post(pg.event.Event(pg.QUIT))

    def update(self, ms):
        pass


def main(argv=None):
    """
    Python version of "Lorenz Attractor" by frankforce.com (Killed By A Pixel).
    """
    # Reference:
    # http://frankforce.com/?p=6584
    parser = argparse.ArgumentParser(prog=Path(__file__).stem, description=main.__doc__)
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
    lorenzattractor = LorenzAttractor()
    engine = Engine(clock, screen, LorenzAttractor())
    engine.run()

if __name__ == '__main__':
    main()
