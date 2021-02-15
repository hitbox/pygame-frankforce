# Killed By A Pixel
# Dissecting A Dweet #8: Shattered Tunnel
# http://frankforce.com/?p=7160
import argparse
import contextlib
import math
import os

with contextlib.redirect_stdout(open(os.devnull,'w')):
    import pygame as pg

def run(framerate, size, fontsize):
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode(size)
    space = screen.get_rect()
    font = pg.font.Font(None, fontsize)
    angle = 0
    original_constants = {
        pg.K_z: 1e5, # used to calculate a radius
        pg.K_y: 3e4, # used to calculate size of rects.
        pg.K_x: 9,   # used to calculate lightness and the size of rects.
        pg.K_w: .01, # angle step.
    }
    constants = original_constants.copy()
    while not pg.event.peek(pg.QUIT):
        clock.tick(framerate)
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key in (pg.K_ESCAPE, pg.K_q):
                    pg.event.post(pg.event.Event(pg.QUIT))

        pressed = pg.key.get_pressed()
        modifiers = pg.key.get_mods()
        ctrl = modifiers & pg.KMOD_CTRL
        shift = modifiers & pg.KMOD_SHIFT
        for key, value in constants.items():
            if pressed[key]:
                if ctrl:
                    # reset
                    constants[key] = original_constants[key]
                else:
                    # adjust
                    value = original_constants[key] * .005
                    if shift:
                        value = -value
                    constants[key] += value

        # the code I expanded in his custom javascript editor.
        """
        for(c.width |= k=i=960; --i;) {
          x.fillStyle = `hsl(0, 99%, ${ i/9 }%`;
          j = i / k + t / 4;
          m = k * j;
          r = 1e5 / i;
          xpos = k + Math.sin(j) * i + Math.sin(m) * r;
          ypos = 540 + Math.cos(j) * i + Math.cos(m) * r;
          width = 3e4 / i * Math.sin(j * 9);
          x.fillRect(xpos, ypos, width, width);
        }
        """
        angle = (angle + constants[pg.K_w]) % math.tau
        color = pg.Color(255,255,255)
        screen.fill(color)
        k = i = space.width / 2
        while i > 0:
            color.hsla = (0, 99, (i / constants[pg.K_x]) % 100, 100)
            # He uses the time in seconds divided by four here, where I use
            # angle. Dividing time by one thousand just spins too fast.
            j = i / k + angle
            m = k * j
            r = constants[pg.K_z] / i
            x = k + math.sin(j) * i + math.sin(m) * r
            y = (space.height / 2) + math.cos(j) * i + math.cos(m) * r
            size = constants[pg.K_y] / i * math.sin(j * constants[pg.K_x])
            rect = pg.Rect(x, y, size, size)
            pg.draw.rect(screen, color, rect)
            i -= 1

        prev = pg.Rect(space.left, -space.height, space.width, space.height)
        for key, value in constants.items():
            image = font.render(f'{pg.key.name(key)}: {value:.4f}', True, (0,0,200))
            prev = image.get_rect(topright=prev.bottomright)
            screen.blit(image, prev)
        image = font.render(f'FPS: {clock.get_fps():.2f}', True, (0,0,200))
        screen.blit(image, image.get_rect(topright=prev.bottomright))

        pg.display.flip()

def main(argv=None):
    "Shattered Tunnel"
    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('--framerate', default=60)
    parser.add_argument('--width', default=960, type=int)
    parser.add_argument('--height', default=540, type=int)
    parser.add_argument('--fontsize', default=48, type=int)
    args = parser.parse_args(argv)
    run(args.framerate, (args.width,args.height), args.fontsize)

if __name__ == '__main__':
    main()
