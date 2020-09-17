import pygame
from pygame.locals import *
import random


pygame.init()
clock = pygame.time.Clock()
frame_rate = 60
# Screen and game grid dimensions
screen_height = 600
grid_rows = 15
grid_cols = 10
grid_size = int(screen_height / grid_rows)
screen_width = grid_cols * grid_size + 1
screen_height = grid_rows * grid_size + 1
screen = pygame.display.set_mode((screen_width, screen_height))
# Title
pygame.display.set_caption('Tetris for Ashton')
# Colors
black = [0, 0, 0]
white = [255, 255, 255]
red = [255, 0, 0]
green = [0, 255, 0]
blue = [0, 0, 255]
cyan = [0, 255, 255]
orange = [255, 165, 0]
yellow = [255, 255, 0]
purple = [128, 0, 128]
pink = [255, 192, 203]
grid_color = [50, 50, 50]
# Font
font_size = 25
font_face = "Helvetica"
main_font = pygame.font.SysFont(font_face, font_size)


class Block:
    def __init__(self, x, y, tet_type=''):
        self.x = x
        self.y = y
        self.width = grid_size
        self.height = grid_size
        self.locked = False
        self.color = white
        self.drop = 0
        self.type = tet_type
        self.pos = [0, 0]

    def draw(self):
        accent0 = [self.color[0] * 0.2, self.color[1] * 0.2, self.color[2] * 0.2]
        accent1 = [self.color[0] * 0.4, self.color[1] * 0.4, self.color[2] * 0.4]
        accent2 = [self.color[0] * 0.6, self.color[1] * 0.6, self.color[2] * 0.6]
        accent3 = [self.color[0] * 0.8, self.color[1] * 0.8, self.color[2] * 0.8]
        pygame.draw.rect(screen, accent0, (self.x, self.y, self.height, self.width))
        pygame.draw.rect(screen, accent1, (self.x + 1, self.y + 1, self.height - 2, self.width - 2))
        pygame.draw.rect(screen, accent2, (self.x + 3, self.y + 3, self.height - 6, self.width - 6))
        pygame.draw.rect(screen, accent3, (self.x + 4, self.y + 4, self.height - 8, self.width - 8))
        pygame.draw.rect(screen, self.color, (self.x + 5, self.y + 5, self.height - 10, self.width - 10))

    def lock(self):
        if not self.locked:
            self.change_color()
            self.locked = True
            temp_row = grid_rows - int(self.y / grid_size)
            temp_col = int(self.x / grid_size) + 1
            if 1 <= temp_row <= grid_rows and 1 <= temp_col <= grid_cols:
                for blk in blocks:
                    if blk is self:
                        continue
                    if blk.pos == self.pos:
                        return
                self.pos = [temp_row, temp_col]

    def unlock(self):
        if self.locked:
            self.locked = False
            self.pos = [0, 0]

    def clear(self):
        global cleared_blocks
        for blk in blocks:
            if blk.locked and blk.x == self.x and blk.y < self.y:
                blk.drop += 1
        cleared_blocks += 1
        blocks.pop(blocks.index(self))

    def change_color(self):
        if self.type == '':
            self.color = pink
        elif self.type == 'TBlock':
            self.color = purple
        elif self.type == 'JBlock':
            self.color = blue
        elif self.type == 'LBlock':
            self.color = orange
        elif self.type == 'IBlock':
            self.color = cyan
        elif self.type == 'OBlock':
            self.color = yellow
        elif self.type == 'SBlock':
            self.color = green
        elif self.type == 'ZBlock':
            self.color = red


class Tet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.rotation = 0
        self.body = []
        self.locked = False
        self.influence = -1

    def update_x(self, x_offset):
        edge = False
        for i in range(len(self.body)):
            if falling_blocks[self.body[i]].x + x_offset >= grid_size * grid_cols or \
                    falling_blocks[self.body[i]].x + x_offset < 0:
                edge = True
                break
        if self.collide_block(x_mod=x_offset):
            edge = True
        if not edge:
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].x += x_offset
            self.x += x_offset

    def update_y(self, y_offset):
        if not self.collide_y(y_offset):
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].y += y_offset
            self.y += y_offset

    def collide_y(self, y_offset):
        collide = False
        for i in range(len(self.body)):
            if falling_blocks[self.body[i]].y + y_offset >= grid_size * grid_rows:
                collide = True
                break
            for bi in range(len(blocks)):
                if falling_blocks[self.body[i]].y + y_offset == blocks[bi].y and \
                        falling_blocks[self.body[i]].x == blocks[bi].x:
                    collide = True
                    break
        if collide:
            return True
        else:
            return False

    def collide_block(self, x_mod=0, y_mod=0):
        for i in range(len(self.body)):
            for blk in blocks:
                if falling_blocks[self.body[i]].x + x_mod == blk.x and falling_blocks[self.body[i]].y + y_mod == blk.y:
                    return True

    def correct_off_screen_x(self):
        off_screen = None
        for i in range(len(self.body)):
            if falling_blocks[self.body[i]].x >= grid_size * grid_cols:
                off_screen = 'right'
                break
            elif falling_blocks[self.body[i]].x < 0:
                off_screen = 'left'
                break
        if off_screen == 'right':
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].x -= grid_size
            self.correct_off_screen_x()
        elif off_screen == 'left':
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].x += grid_size
            self.correct_off_screen_x()

    def correct_off_screen_y(self):
        off_screen = False
        for i in range(len(self.body)):
            if falling_blocks[self.body[i]].y >= grid_size * grid_rows:
                off_screen = True
                break
        if off_screen:
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].y -= grid_size
            self.correct_off_screen_y()

    def commit_self_die(self):
        if self.locked and self.influence == 0 and self.y >= 0:
            for i in range(len(self.body)):
                blocks.append(falling_blocks[self.body[i]])
                blocks[len(blocks) - 1].lock()
            self.body.sort(reverse=True)
            for i in range(len(self.body)):
                falling_blocks.pop(self.body[i])
            tet_list.pop(0)
        elif self.locked and self.influence == 0 and self.y < 0:
            round_over()


class TBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y, 'TBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y + grid_size, 'TBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y + grid_size, 'TBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 2, self.y + grid_size, 'TBlock'))

    def rotate(self, ccw=True):
        if ccw:
            if self.rotation == 0:
                falling_blocks[self.body[0]].x -= grid_size
                falling_blocks[self.body[0]].y += grid_size
                falling_blocks[self.body[1]].x += grid_size
                falling_blocks[self.body[1]].y += grid_size
                falling_blocks[self.body[3]].x -= grid_size
                falling_blocks[self.body[3]].y -= grid_size
                self.rotation += 1
            elif self.rotation == 1:
                falling_blocks[self.body[0]].x += grid_size
                falling_blocks[self.body[1]].x += grid_size
                falling_blocks[self.body[1]].y -= grid_size * 2
                falling_blocks[self.body[2]].y -= grid_size
                falling_blocks[self.body[3]].x -= grid_size
                self.rotation += 1
            elif self.rotation == 2:
                falling_blocks[self.body[1]].x -= grid_size * 2
                falling_blocks[self.body[2]].x -= grid_size
                falling_blocks[self.body[2]].y += grid_size
                falling_blocks[self.body[3]].y += grid_size * 2
                self.rotation += 1
            elif self.rotation == 3:
                falling_blocks[self.body[0]].y -= grid_size
                falling_blocks[self.body[1]].y += grid_size
                falling_blocks[self.body[2]].x += grid_size
                falling_blocks[self.body[3]].x += grid_size * 2
                falling_blocks[self.body[3]].y -= grid_size
                self.rotation = 0
        else:
            if self.rotation == 1:
                falling_blocks[self.body[0]].x += grid_size
                falling_blocks[self.body[0]].y -= grid_size
                falling_blocks[self.body[1]].x -= grid_size
                falling_blocks[self.body[1]].y -= grid_size
                falling_blocks[self.body[3]].x += grid_size
                falling_blocks[self.body[3]].y += grid_size
                self.rotation -= 1
            elif self.rotation == 2:
                falling_blocks[self.body[0]].x -= grid_size
                falling_blocks[self.body[1]].x -= grid_size
                falling_blocks[self.body[1]].y += grid_size * 2
                falling_blocks[self.body[2]].y += grid_size
                falling_blocks[self.body[3]].x += grid_size
                self.rotation -= 1
            elif self.rotation == 3:
                falling_blocks[self.body[1]].x += grid_size * 2
                falling_blocks[self.body[2]].x += grid_size
                falling_blocks[self.body[2]].y -= grid_size
                falling_blocks[self.body[3]].y -= grid_size * 2
                self.rotation -= 1
            elif self.rotation == 0:
                falling_blocks[self.body[0]].y += grid_size
                falling_blocks[self.body[1]].y -= grid_size
                falling_blocks[self.body[2]].x -= grid_size
                falling_blocks[self.body[3]].x -= grid_size * 2
                falling_blocks[self.body[3]].y += grid_size
                self.rotation = 3

        if self.collide_block() and self.y > 0:
            self.rotate(not ccw)
        self.correct_off_screen_x()
        self.correct_off_screen_y()


class JBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y, 'JBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y + grid_size, 'JBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y + grid_size, 'JBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 2, self.y + grid_size, 'JBlock'))

    def rotate(self, ccw=True):
        if ccw:
            if self.rotation == 0:
                falling_blocks[self.body[0]].y += grid_size * 2
                falling_blocks[self.body[1]].x += grid_size
                falling_blocks[self.body[1]].y += grid_size
                falling_blocks[self.body[3]].x -= grid_size
                falling_blocks[self.body[3]].y -= grid_size
                self.rotation += 1
            elif self.rotation == 1:
                falling_blocks[self.body[0]].x += grid_size * 2
                falling_blocks[self.body[0]].y -= grid_size
                falling_blocks[self.body[1]].x += grid_size
                falling_blocks[self.body[1]].y -= grid_size * 2
                falling_blocks[self.body[2]].y -= grid_size
                falling_blocks[self.body[3]].x -= grid_size
                self.rotation += 1
            elif self.rotation == 2:
                falling_blocks[self.body[0]].x -= grid_size
                falling_blocks[self.body[0]].y -= grid_size
                falling_blocks[self.body[1]].x -= grid_size * 2
                falling_blocks[self.body[2]].x -= grid_size
                falling_blocks[self.body[2]].y += grid_size
                falling_blocks[self.body[3]].y += grid_size * 2
                self.rotation += 1
            elif self.rotation == 3:
                falling_blocks[self.body[0]].x -= grid_size
                falling_blocks[self.body[1]].y += grid_size
                falling_blocks[self.body[2]].x += grid_size
                falling_blocks[self.body[3]].x += grid_size * 2
                falling_blocks[self.body[3]].y -= grid_size
                self.rotation = 0
        else:
            if self.rotation == 1:
                falling_blocks[self.body[0]].y -= grid_size * 2
                falling_blocks[self.body[1]].x -= grid_size
                falling_blocks[self.body[1]].y -= grid_size
                falling_blocks[self.body[3]].x += grid_size
                falling_blocks[self.body[3]].y += grid_size
                self.rotation -= 1
            elif self.rotation == 2:
                falling_blocks[self.body[0]].x -= grid_size * 2
                falling_blocks[self.body[0]].y += grid_size
                falling_blocks[self.body[1]].x -= grid_size
                falling_blocks[self.body[1]].y += grid_size * 2
                falling_blocks[self.body[2]].y += grid_size
                falling_blocks[self.body[3]].x += grid_size
                self.rotation -= 1
            elif self.rotation == 3:
                falling_blocks[self.body[0]].x += grid_size
                falling_blocks[self.body[0]].y += grid_size
                falling_blocks[self.body[1]].x += grid_size * 2
                falling_blocks[self.body[2]].x += grid_size
                falling_blocks[self.body[2]].y -= grid_size
                falling_blocks[self.body[3]].y -= grid_size * 2
                self.rotation -= 1
            elif self.rotation == 0:
                falling_blocks[self.body[0]].x += grid_size
                falling_blocks[self.body[1]].y -= grid_size
                falling_blocks[self.body[2]].x -= grid_size
                falling_blocks[self.body[3]].x -= grid_size * 2
                falling_blocks[self.body[3]].y += grid_size
                self.rotation = 3

        if self.collide_block() and self.y > 0:
            self.rotate(not ccw)
        self.correct_off_screen_x()
        self.correct_off_screen_y()


class LBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 2, self.y, 'LBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y + grid_size, 'LBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y + grid_size, 'LBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 2, self.y + grid_size, 'LBlock'))

    def rotate(self, ccw=True):
        if ccw:
            if self.rotation == 0:
                falling_blocks[self.body[0]].x -= grid_size * 2
                falling_blocks[self.body[1]].x += grid_size
                falling_blocks[self.body[1]].y += grid_size
                falling_blocks[self.body[3]].x -= grid_size
                falling_blocks[self.body[3]].y -= grid_size
                self.rotation += 1
            elif self.rotation == 1:
                falling_blocks[self.body[0]].y += grid_size
                falling_blocks[self.body[1]].x += grid_size
                falling_blocks[self.body[1]].y -= grid_size * 2
                falling_blocks[self.body[2]].y -= grid_size
                falling_blocks[self.body[3]].x -= grid_size
                self.rotation += 1
            elif self.rotation == 2:
                falling_blocks[self.body[0]].x += grid_size
                falling_blocks[self.body[0]].y += grid_size
                falling_blocks[self.body[1]].x -= grid_size * 2
                falling_blocks[self.body[2]].x -= grid_size
                falling_blocks[self.body[2]].y += grid_size
                falling_blocks[self.body[3]].y += grid_size * 2
                self.rotation += 1
            elif self.rotation == 3:
                falling_blocks[self.body[0]].x += grid_size
                falling_blocks[self.body[0]].y -= grid_size * 2
                falling_blocks[self.body[1]].y += grid_size
                falling_blocks[self.body[2]].x += grid_size
                falling_blocks[self.body[3]].x += grid_size * 2
                falling_blocks[self.body[3]].y -= grid_size
                self.rotation = 0
        else:
            if self.rotation == 1:
                falling_blocks[self.body[0]].x += grid_size * 2
                falling_blocks[self.body[1]].x -= grid_size
                falling_blocks[self.body[1]].y -= grid_size
                falling_blocks[self.body[3]].x += grid_size
                falling_blocks[self.body[3]].y += grid_size
                self.rotation -= 1
            elif self.rotation == 2:
                falling_blocks[self.body[0]].y -= grid_size
                falling_blocks[self.body[1]].x -= grid_size
                falling_blocks[self.body[1]].y += grid_size * 2
                falling_blocks[self.body[2]].y += grid_size
                falling_blocks[self.body[3]].x += grid_size
                self.rotation -= 1
            elif self.rotation == 3:
                falling_blocks[self.body[0]].x -= grid_size
                falling_blocks[self.body[0]].y -= grid_size
                falling_blocks[self.body[1]].x += grid_size * 2
                falling_blocks[self.body[2]].x += grid_size
                falling_blocks[self.body[2]].y -= grid_size
                falling_blocks[self.body[3]].y -= grid_size * 2
                self.rotation -= 1
            elif self.rotation == 0:
                falling_blocks[self.body[0]].x -= grid_size
                falling_blocks[self.body[0]].y += grid_size * 2
                falling_blocks[self.body[1]].y -= grid_size
                falling_blocks[self.body[2]].x -= grid_size
                falling_blocks[self.body[3]].x -= grid_size * 2
                falling_blocks[self.body[3]].y += grid_size
                self.rotation = 3

        if self.collide_block() and self.y > 0:
            self.rotate(not ccw)
        self.correct_off_screen_x()
        self.correct_off_screen_y()


class IBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y, 'IBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y, 'IBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 2, self.y, 'IBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 3, self.y, 'IBlock'))

    def rotate(self, ccw=None):
        if ccw:
            pass
        if self.rotation == 0:
            falling_blocks[self.body[1]].x -= grid_size
            falling_blocks[self.body[1]].y += grid_size
            falling_blocks[self.body[2]].x -= grid_size * 2
            falling_blocks[self.body[2]].y += grid_size * 2
            falling_blocks[self.body[3]].x -= grid_size * 3
            falling_blocks[self.body[3]].y += grid_size * 3
            self.rotation += 1
        elif self.rotation == 1:
            falling_blocks[self.body[1]].x += grid_size
            falling_blocks[self.body[1]].y -= grid_size
            falling_blocks[self.body[2]].x += grid_size * 2
            falling_blocks[self.body[2]].y -= grid_size * 2
            falling_blocks[self.body[3]].x += grid_size * 3
            falling_blocks[self.body[3]].y -= grid_size * 3
            self.rotation = 0

        if self.collide_block() and self.y > 0:
            self.rotate()
        self.correct_off_screen_x()
        self.correct_off_screen_y()


class OBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y, 'OBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y + grid_size, 'OBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y, 'OBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y + grid_size, 'OBlock'))

    def rotate(self, ccw=None):
        pass


class SBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y + grid_size, 'SBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y + grid_size, 'SBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y, 'SBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 2, self.y, 'SBlock'))

    def rotate(self, ccw=None):
        if ccw:
            pass
        if self.rotation == 0:
            falling_blocks[self.body[0]].y += grid_size
            falling_blocks[self.body[0]].x += grid_size
            falling_blocks[self.body[2]].x -= grid_size
            falling_blocks[self.body[2]].y += grid_size
            falling_blocks[self.body[3]].x -= grid_size * 2
            self.rotation += 1
        elif self.rotation == 1:
            falling_blocks[self.body[0]].y -= grid_size
            falling_blocks[self.body[0]].x -= grid_size
            falling_blocks[self.body[2]].x += grid_size
            falling_blocks[self.body[2]].y -= grid_size
            falling_blocks[self.body[3]].x += grid_size * 2
            self.rotation = 0

        if self.collide_block() and self.y > 0:
            self.rotate()
        self.correct_off_screen_x()
        self.correct_off_screen_y()


class ZBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y, 'ZBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y, 'ZBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y + grid_size, 'ZBlock'))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 2, self.y + grid_size, 'ZBlock'))

    def rotate(self, ccw=None):
        if ccw:
            pass
        if self.rotation == 0:
            falling_blocks[self.body[0]].y += grid_size
            falling_blocks[self.body[0]].x += grid_size
            falling_blocks[self.body[2]].x -= grid_size
            falling_blocks[self.body[2]].y += grid_size
            falling_blocks[self.body[3]].x -= grid_size * 2
            self.rotation += 1
        elif self.rotation == 1:
            falling_blocks[self.body[0]].y -= grid_size
            falling_blocks[self.body[0]].x -= grid_size
            falling_blocks[self.body[2]].x += grid_size
            falling_blocks[self.body[2]].y -= grid_size
            falling_blocks[self.body[3]].x += grid_size * 2
            self.rotation = 0

        if self.collide_block() and self.y > 0:
            self.rotate()
        self.correct_off_screen_x()
        self.correct_off_screen_y()


def draw_bg_grid(dif_color=None):
    if dif_color is None:
        dif_color = grid_color
    for i in range(0, grid_cols + 1):
        pygame.draw.rect(screen, dif_color, (grid_size * i, 0, 1, grid_size * grid_rows))
    for i in range(0, grid_rows + 1):
        pygame.draw.rect(screen, dif_color, (0, grid_size * i, grid_size * grid_cols, 1))


def fall_tet():
    for t in tet_list:
        t.update_y(grid_size)


def lock_tet():
    for t in tet_list:
        if not t.locked and t.collide_y(grid_size):
            t.locked = True
            if not mondo_mode:
                t.influence = lock_delay
            else:
                t.influence = 0
        if t.influence > 0 and t.collide_y(grid_size):
            t.influence -= 1
        elif t.influence > 0 and not t.collide_y(grid_size):
            t.locked = False
            t.influence = -1
        elif t.influence == 0 and t.collide_y(grid_size):
            t.commit_self_die()
            spawn_random_tet(True)


def move_tet():
    for t in tet_list:
        if move_left:
            t.update_x(-grid_size)
        elif move_right:
            t.update_x(grid_size)


def drop_blocks():
    for blk in blocks:
        if blk.drop > 0:
            blk.unlock()
            blk.y += grid_size * blk.drop
            blk.lock()
            blk.drop = 0


def clear_blocks():
    temp_array = []
    temp_block_array = []
    for blk in blocks:
        if blk.locked and blk.pos[0] != 0:
            temp_array.append(blk.pos[0])
            temp_block_array.append(blk)
    # strings = []
    for i in range(1, grid_rows + 1):
        if temp_array.count(i) == grid_cols:
            for z in range(len(temp_array)):
                if temp_array[z] == i:
                    temp_block_array[z].clear()
    #     string = 'r' + str(i) + ':' + str(temp_array.count(i))
    #     strings.append(string)
    # print(strings)


def spawn_random_tet(ran_pos=False):
    global last_spawned_blocks

    if len(tet_list) == 0:
        tet_array = [TBlock, JBlock, LBlock, IBlock, OBlock, SBlock, ZBlock]
        tet_array_str = ['TBlock', 'JBlock', 'LBlock', 'IBlock', 'OBlock', 'SBlock', 'ZBlock']
        i = random.randint(0, len(tet_array) - 1)
        # Prevent same block 3 times in a row
        if tet_array_str[i] == last_spawned_blocks[0] and tet_array_str[i] == last_spawned_blocks[1]:
            spawn_random_tet()
            return
        # 2/3 chance to re-roll if same block as last
        elif tet_array_str[i] == last_spawned_blocks[1]:
            roll = random.randint(0, 2)
            if roll > 0:
                last_spawned_blocks = [last_spawned_blocks[1], tet_array_str[i]]
                spawn_random_tet()
                return
        ran_tet = tet_array[i]
        if ran_pos:
            ran_x = random.randint(0, grid_size * grid_cols)
        else:
            ran_x = (grid_size * grid_cols) / 2 - grid_size
        ran_x = int(ran_x - (ran_x % grid_size)) - grid_size

        tet_list.append(ran_tet(ran_x, -grid_size * 2))
        tet_list[len(tet_list) - 1].correct_off_screen_x()

        last_spawned_blocks = [last_spawned_blocks[1], tet_array_str[i]]


def round_over():
    global blocks
    global falling_blocks
    global tet_list
    global round_frame_count
    global rounds_played
    global cleared_blocks

    num_active = int(len(blocks))
    num_clear = int(cleared_blocks / grid_cols)

    blocks = []
    falling_blocks = []
    tet_list = []
    cleared_blocks = 0

    if num_active != 0:
        rounds_played += 1
        print('########################################################################################')
        print('')
        print('cleared rows: ' + str(num_clear) + ', active blocks: ' + str(num_active) +
              ', round frames: ' + str(round_frame_count) + ', global frames: ' + str(global_frame_count) +
              ', round: ' + str(rounds_played))
        print('')
        print('########################################################################################')
    round_frame_count = 0
    spawn_random_tet(True)


def randomly_rotate():
    roll = random.randint(0, 19)
    roll2 = random.randint(0, 1)
    if roll == 0:
        if roll2 == 0:
            for t in tet_list:
                t.rotate()
        else:
            for t in tet_list:
                t.rotate(False)


def randomly_move():
    roll = random.randint(0, 9)
    roll2 = random.randint(0, 1)
    if roll == 0:
        if roll2 == 0:
            for t in tet_list:
                t.update_x(grid_size)
        else:
            for t in tet_list:
                t.update_x(-grid_size)


score = 0
fall_cool_down_timer = 0
fall_cool_down = frame_rate / 2
lock_delay = frame_rate / 2
blocks = []
cleared_blocks = 0
falling_blocks = []
last_spawned_blocks = ['', '']
tet_list = []
quick_drop = False
mondo_mode = False
move_left = False
move_right = False
move_delay = 0
running = True
pause = True
round_frame_count = 0
global_frame_count = 0
rounds_played = 0
while running:
    screen.fill(black)
    if pause:
        draw_bg_grid(pink)
    else:
        draw_bg_grid()

    # Event loop
    for event in pygame.event.get():
        # Press close button
        if event.type == pygame.QUIT:
            running = False
            break

        # Key down events
        keys = pygame.key.get_pressed()
        if event.type == pygame.KEYDOWN:
            # Close window shortcut
            if (keys[K_LCTRL] or keys[K_RCTRL]) and keys[K_w]:
                running = False
                break
            # Spawn JBlock
            if keys[K_j]:
                if len(tet_list) == 0:
                    tet_list.append(JBlock(0, -grid_size))
            # Spawn LBlock
            if keys[K_l]:
                if len(tet_list) == 0:
                    tet_list.append(LBlock(0, -grid_size))
            # Spawn IBlock
            if keys[K_i]:
                if len(tet_list) == 0:
                    tet_list.append(IBlock(0, -grid_size))
            # Spawn OBlock
            if keys[K_o]:
                if len(tet_list) == 0:
                    tet_list.append(OBlock(0, -grid_size))
            # Spawn SBlock
            if keys[K_s]:
                if len(tet_list) == 0:
                    tet_list.append(SBlock(0, -grid_size))
            # Spawn ZBlock
            if keys[K_z]:
                if len(tet_list) == 0:
                    tet_list.append(ZBlock(0, -grid_size))
            # Spawn TBlock
            if keys[K_t]:
                if len(tet_list) == 0:
                    tet_list.append(TBlock(0, -grid_size))
            # Rotate falling block
            if keys[K_r]:
                for tet in tet_list:
                    tet.rotate()
            elif keys[K_e]:
                for tet in tet_list:
                    tet.rotate(False)
            # Move falling block right
            if keys[K_RIGHT] and not move_right:
                move_right = True
                move_tet()
                move_delay = frame_rate / 4
            # Move falling block left
            if keys[K_LEFT] and not move_left:
                move_left = True
                move_tet()
                move_delay = frame_rate / 4
            # Turn on quick drop
            if keys[K_DOWN] and not quick_drop:
                quick_drop = True
            # Generate random block
            if keys[K_SPACE]:
                spawn_random_tet()
            # Pause
            if keys[K_p] and not pause:
                pause = True
            elif keys[K_p] and pause:
                pause = False
            # Mondo mode
            if keys[K_u]:
                mondo_mode = not mondo_mode

        # Key up events
        if event.type == pygame.KEYUP:
            # Turn off quick drop
            if not keys[K_DOWN] and quick_drop:
                quick_drop = False
            # Stop move falling block right
            if not keys[K_RIGHT] and move_right:
                move_delay = 0
                move_right = False
            # Stop move falling block left
            if not keys[K_LEFT] and move_left:
                move_delay = 0
                move_left = False

    if mondo_mode:
        randomly_move()
        randomly_rotate()
    # Block updates
    if not pause:
        if fall_cool_down_timer == 0 or quick_drop or mondo_mode:
            drop_blocks()
            fall_tet()
            clear_blocks()
            fall_cool_down_timer = fall_cool_down
        elif fall_cool_down_timer > 0:
            fall_cool_down_timer -= 1
        lock_tet()
        if move_delay == 0:
            move_tet()
        elif move_delay > 0:
            move_delay -= 1

    # Draw blocks
    for block in blocks:
        block.draw()
    for block in falling_blocks:
        block.draw()

    if not pause:
        round_frame_count += 1
        global_frame_count += 1

    if not mondo_mode:
        clock.tick(frame_rate)
    pygame.display.flip()


pygame.display.quit()
pygame.quit()
