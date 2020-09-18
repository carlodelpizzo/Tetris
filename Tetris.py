import pygame
from pygame.locals import *
import random


pygame.init()
clock = pygame.time.Clock()
frame_rate = 60
# Screen and game grid dimensions
screen_width = 600
screen_height = 700
screen = pygame.display.set_mode((screen_width, screen_height), RESIZABLE)
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


class GameGrid:
    def __init__(self, x, y, width, height, rows, cols=10):
        self.x = int(x)
        self.y = int(y)
        self.rows = int(rows)
        self.cols = int(cols)
        self.x_unit = int(width / cols)
        self.y_unit = int(height / rows)
        self.width = self.x_unit * self.cols
        self.height = self.y_unit * self.rows
        self.right_edge = self.x + self.width
        self.bottom = self.y + self.height

    def move_pos(self, x_offset, y_offset):
        global falling_tet

        self.x += x_offset
        self.y += y_offset
        self.right_edge = self.x + self.width
        self.bottom = self.y + self.height
        for blk in blocks:
            blk.x += x_offset
            blk.y += y_offset
        if falling_tet is not None:
            falling_tet.x += x_offset
            falling_tet.y += y_offset
            for blk in falling_tet.body:
                blk.x += x_offset
                blk.y += y_offset


class Block:
    def __init__(self, x, y, tet_type=''):
        self.x = int(x)
        self.y = int(y)
        self.width = grid.x_unit
        self.height = grid.y_unit
        self.locked = False
        self.color = white
        self.drop = 0
        self.type = tet_type
        self.grid_pos = [0, 0]
        self.shadow = False

    def draw(self):
        accent0 = [self.color[0] * 0.2, self.color[1] * 0.2, self.color[2] * 0.2]
        accent1 = [self.color[0] * 0.4, self.color[1] * 0.4, self.color[2] * 0.4]
        accent2 = [self.color[0] * 0.6, self.color[1] * 0.6, self.color[2] * 0.6]
        accent3 = [self.color[0] * 0.8, self.color[1] * 0.8, self.color[2] * 0.8]
        pygame.draw.rect(screen, accent0, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, accent1, (self.x + 1, self.y + 1, self.width - 2, self.height - 2))
        pygame.draw.rect(screen, accent2, (self.x + 3, self.y + 3, self.width - 6, self.height - 6))
        pygame.draw.rect(screen, accent3, (self.x + 4, self.y + 4, self.width - 8, self.height - 8))
        if not self.shadow:
            pygame.draw.rect(screen, self.color, (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
        else:
            pygame.draw.rect(screen, accent2, (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
            pygame.draw.rect(screen, accent1, (self.x + 6, self.y + 6, self.width - 12, self.height - 12))
            pygame.draw.rect(screen, accent0, (self.x + 8, self.y + 8, self.width - 16, self.height - 16))
            pygame.draw.rect(screen, black, (self.x + 10, self.y + 10, self.width - 20, self.height - 20))

    def lock(self):
        if not self.locked:
            self.change_color()
            self.locked = True
            row_pos = grid.rows - int((self.y - grid.y) / grid.y_unit)
            col_pos = int((self.x - grid.x) / grid.x_unit) + 1
            if 1 <= row_pos <= grid.rows and 1 <= col_pos <= grid.cols:
                for blk in blocks:
                    if blk is not self and blk.grid_pos == self.grid_pos:
                        return
            self.grid_pos = [row_pos, col_pos]

    def unlock(self):
        if self.locked:
            self.locked = False

    def clear(self):
        global cleared_blocks_count
        for blk in blocks:
            if blk.locked and blk.x == self.x and blk.y < self.y:
                blk.drop += 1
        cleared_blocks_count += 1
        blocks.pop(blocks.index(self))

    def change_color(self, change=None):
        if change is None:
            if self.type in tet_color_dict:
                self.color = tet_color_dict[self.type]
            else:
                self.color = pink
        else:
            self.color = change


class Tet:
    def __init__(self, x, y, kind):
        if kind in tet_color_dict:
            tet_color = tet_color_dict[kind]
        else:
            tet_color = white
        self.x = int(x)
        self.y = int(y)
        self.rotation = 0
        self.body = []
        self.locked = False
        self.influence = -1
        self.type = kind
        self.color = tet_color

    def move_x(self, x_offset):
        edge = False
        for blk in self.body:
            if blk.x + x_offset >= grid.right_edge or \
                    blk.x + x_offset < grid.x:
                edge = True
                break
        if self.collide_block(x_mod=x_offset):
            edge = True
        if not edge:
            for blk in self.body:
                blk.x += x_offset
            self.x += x_offset

    def move_y(self, y_offset):
        if not self.collide_y(y_offset):
            for blk in self.body:
                blk.y += y_offset
            self.y += y_offset

    def update_pos(self, new_x=None, new_y=None):
        if new_x is None:
            new_x = self.x
        if new_y is None:
            new_y = self.y

        for blk in self.body:
            blk.x = new_x + (blk.x - self.x)
            blk.y = new_y + (blk.y - self.y)

        self.x = new_x
        self.y = new_y

    def shadow_drop(self):
        if self.collide_y(grid.y_unit):
            return
        else:
            self.y += grid.y_unit
            for blk in self.body:
                blk.y += grid.y_unit
            self.shadow_drop()

    def collide_y(self, y_offset):
        collide = False
        for self_blk in self.body:
            if self_blk.y + y_offset >= grid.bottom:
                collide = True
                break
            for blk in blocks:
                if self_blk.y + y_offset == blk.y and \
                        self_blk.x == blk.x:
                    collide = True
                    break
        if collide:
            return True
        else:
            return False

    def collide_block(self, x_mod=0, y_mod=0):
        for self_blk in self.body:
            for blk in blocks:
                if self_blk.x + x_mod == blk.x and \
                        self_blk.y + y_mod == blk.y:
                    return True

    def correct_off_screen_x(self):
        off_screen = None
        for blk in self.body:
            if blk.x >= grid.right_edge:
                off_screen = 'right'
                break
            elif blk.x < grid.x:
                off_screen = 'left'
                break
        if off_screen == 'right':
            for blk in self.body:
                blk.x -= grid.x_unit
            self.correct_off_screen_x()
        elif off_screen == 'left':
            for blk in self.body:
                blk.x += grid.x_unit
            self.correct_off_screen_x()

    def correct_off_screen_y(self):
        off_screen = False
        for blk in self.body:
            if blk.y >= grid.bottom:
                off_screen = True
                break
        if off_screen:
            for blk in self.body:
                blk.y -= grid.y_unit
            self.correct_off_screen_y()

    def lock_blocks(self):
        if self.locked and self.influence == 0 and self.y >= grid.y:
            for i in range(len(self.body)):
                blocks.append(self.body[i])
                blocks[len(blocks) - 1].lock()
            for i in range(len(self.body) - 1, 0):
                self.body.pop(i)
        elif self.locked and self.influence == 0 and self.y < grid.y:
            round_over()

    def change_block_colors(self, new_color=None):
        if new_color is None:
            new_color = self.color
        else:
            self.color = new_color

        for blk in self.body:
            blk.change_color(new_color)

    def shadow_blocks(self):
        self.change_block_colors()
        for blk in self.body:
            blk.shadow = True


class TBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y, 'TBlock')
        self.body.append(Block(self.x + grid.x_unit, self.y, self.type))
        self.body.append(Block(self.x, self.y + grid.y_unit, self.type))
        self.body.append(Block(self.x + grid.x_unit, self.y + grid.y_unit, self.type))
        self.body.append(Block(self.x + grid.x_unit * 2, self.y + grid.y_unit, self.type))

    def rotate(self, cw=False):
        if cw:
            if self.rotation == 0:
                self.body[0].x -= grid.x_unit
                self.body[0].y += grid.y_unit
                self.body[1].x += grid.x_unit
                self.body[1].y += grid.y_unit
                self.body[3].x -= grid.x_unit
                self.body[3].y -= grid.y_unit
                self.rotation += 1
            elif self.rotation == 1:
                self.body[0].x += grid.x_unit
                self.body[1].x += grid.x_unit
                self.body[1].y -= grid.y_unit * 2
                self.body[2].y -= grid.y_unit
                self.body[3].x -= grid.x_unit
                self.rotation += 1
            elif self.rotation == 2:
                self.body[1].x -= grid.x_unit * 2
                self.body[2].x -= grid.x_unit
                self.body[2].y += grid.y_unit
                self.body[3].y += grid.y_unit * 2
                self.rotation += 1
            elif self.rotation == 3:
                self.body[0].y -= grid.y_unit
                self.body[1].y += grid.y_unit
                self.body[2].x += grid.x_unit
                self.body[3].x += grid.x_unit * 2
                self.body[3].y -= grid.y_unit
                self.rotation = 0
        else:
            if self.rotation == 1:
                self.body[0].x += grid.x_unit
                self.body[0].y -= grid.y_unit
                self.body[1].x -= grid.x_unit
                self.body[1].y -= grid.y_unit
                self.body[3].x += grid.x_unit
                self.body[3].y += grid.y_unit
                self.rotation -= 1
            elif self.rotation == 2:
                self.body[0].x -= grid.x_unit
                self.body[1].x -= grid.x_unit
                self.body[1].y += grid.y_unit * 2
                self.body[2].y += grid.y_unit
                self.body[3].x += grid.x_unit
                self.rotation -= 1
            elif self.rotation == 3:
                self.body[1].x += grid.x_unit * 2
                self.body[2].x += grid.x_unit
                self.body[2].y -= grid.y_unit
                self.body[3].y -= grid.y_unit * 2
                self.rotation -= 1
            elif self.rotation == 0:
                self.body[0].y += grid.y_unit
                self.body[1].y -= grid.y_unit
                self.body[2].x -= grid.x_unit
                self.body[3].x -= grid.x_unit * 2
                self.body[3].y += grid.y_unit
                self.rotation = 3

        if self.collide_block() and self.y > 0:
            self.rotate(not cw)
        self.correct_off_screen_x()
        self.correct_off_screen_y()


class JBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y, 'JBlock')
        self.body.append(Block(self.x, self.y, self.type))
        self.body.append(Block(self.x, self.y + grid.y_unit, self.type))
        self.body.append(Block(self.x + grid.x_unit, self.y + grid.y_unit, self.type))
        self.body.append(Block(self.x + grid.x_unit * 2, self.y + grid.y_unit, self.type))

    def rotate(self, cw=False):
        if cw:
            if self.rotation == 0:
                self.body[0].y += grid.y_unit * 2
                self.body[1].x += grid.x_unit
                self.body[1].y += grid.y_unit
                self.body[3].x -= grid.x_unit
                self.body[3].y -= grid.y_unit
                self.rotation += 1
            elif self.rotation == 1:
                self.body[0].x += grid.x_unit * 2
                self.body[0].y -= grid.y_unit
                self.body[1].x += grid.x_unit
                self.body[1].y -= grid.y_unit * 2
                self.body[2].y -= grid.y_unit
                self.body[3].x -= grid.x_unit
                self.rotation += 1
            elif self.rotation == 2:
                self.body[0].x -= grid.x_unit
                self.body[0].y -= grid.y_unit
                self.body[1].x -= grid.x_unit * 2
                self.body[2].x -= grid.x_unit
                self.body[2].y += grid.y_unit
                self.body[3].y += grid.y_unit * 2
                self.rotation += 1
            elif self.rotation == 3:
                self.body[0].x -= grid.x_unit
                self.body[1].y += grid.y_unit
                self.body[2].x += grid.x_unit
                self.body[3].x += grid.x_unit * 2
                self.body[3].y -= grid.y_unit
                self.rotation = 0
        else:
            if self.rotation == 1:
                self.body[0].y -= grid.y_unit * 2
                self.body[1].x -= grid.x_unit
                self.body[1].y -= grid.y_unit
                self.body[3].x += grid.x_unit
                self.body[3].y += grid.y_unit
                self.rotation -= 1
            elif self.rotation == 2:
                self.body[0].x -= grid.x_unit * 2
                self.body[0].y += grid.y_unit
                self.body[1].x -= grid.x_unit
                self.body[1].y += grid.y_unit * 2
                self.body[2].y += grid.y_unit
                self.body[3].x += grid.x_unit
                self.rotation -= 1
            elif self.rotation == 3:
                self.body[0].x += grid.x_unit
                self.body[0].y += grid.y_unit
                self.body[1].x += grid.x_unit * 2
                self.body[2].x += grid.x_unit
                self.body[2].y -= grid.y_unit
                self.body[3].y -= grid.y_unit * 2
                self.rotation -= 1
            elif self.rotation == 0:
                self.body[0].x += grid.x_unit
                self.body[1].y -= grid.y_unit
                self.body[2].x -= grid.x_unit
                self.body[3].x -= grid.x_unit * 2
                self.body[3].y += grid.y_unit
                self.rotation = 3

        if self.collide_block() and self.y > 0:
            self.rotate(not cw)
        self.correct_off_screen_x()
        self.correct_off_screen_y()


class LBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y, 'LBlock')
        self.body.append(Block(self.x + grid.x_unit * 2, self.y, self.type))
        self.body.append(Block(self.x, self.y + grid.y_unit, self.type))
        self.body.append(Block(self.x + grid.x_unit, self.y + grid.y_unit, self.type))
        self.body.append(Block(self.x + grid.x_unit * 2, self.y + grid.y_unit, self.type))

    def rotate(self, cw=False):
        if cw:
            if self.rotation == 0:
                self.body[0].x -= grid.x_unit * 2
                self.body[1].x += grid.x_unit
                self.body[1].y += grid.y_unit
                self.body[3].x -= grid.x_unit
                self.body[3].y -= grid.y_unit
                self.rotation += 1
            elif self.rotation == 1:
                self.body[0].y += grid.y_unit
                self.body[1].x += grid.x_unit
                self.body[1].y -= grid.y_unit * 2
                self.body[2].y -= grid.y_unit
                self.body[3].x -= grid.x_unit
                self.rotation += 1
            elif self.rotation == 2:
                self.body[0].x += grid.x_unit
                self.body[0].y += grid.y_unit
                self.body[1].x -= grid.x_unit * 2
                self.body[2].x -= grid.x_unit
                self.body[2].y += grid.y_unit
                self.body[3].y += grid.y_unit * 2
                self.rotation += 1
            elif self.rotation == 3:
                self.body[0].x += grid.x_unit
                self.body[0].y -= grid.y_unit * 2
                self.body[1].y += grid.y_unit
                self.body[2].x += grid.x_unit
                self.body[3].x += grid.x_unit * 2
                self.body[3].y -= grid.y_unit
                self.rotation = 0
        else:
            if self.rotation == 1:
                self.body[0].x += grid.x_unit * 2
                self.body[1].x -= grid.x_unit
                self.body[1].y -= grid.y_unit
                self.body[3].x += grid.x_unit
                self.body[3].y += grid.y_unit
                self.rotation -= 1
            elif self.rotation == 2:
                self.body[0].y -= grid.y_unit
                self.body[1].x -= grid.x_unit
                self.body[1].y += grid.y_unit * 2
                self.body[2].y += grid.y_unit
                self.body[3].x += grid.x_unit
                self.rotation -= 1
            elif self.rotation == 3:
                self.body[0].x -= grid.x_unit
                self.body[0].y -= grid.y_unit
                self.body[1].x += grid.x_unit * 2
                self.body[2].x += grid.x_unit
                self.body[2].y -= grid.y_unit
                self.body[3].y -= grid.y_unit * 2
                self.rotation -= 1
            elif self.rotation == 0:
                self.body[0].x -= grid.x_unit
                self.body[0].y += grid.y_unit * 2
                self.body[1].y -= grid.y_unit
                self.body[2].x -= grid.x_unit
                self.body[3].x -= grid.x_unit * 2
                self.body[3].y += grid.y_unit
                self.rotation = 3

        if self.collide_block() and self.y > 0:
            self.rotate(not cw)
        self.correct_off_screen_x()
        self.correct_off_screen_y()


class IBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y, 'IBlock')
        self.body.append(Block(self.x, self.y, self.type))
        self.body.append(Block(self.x + grid.x_unit, self.y, self.type))
        self.body.append(Block(self.x + grid.x_unit * 2, self.y, self.type))
        self.body.append(Block(self.x + grid.x_unit * 3, self.y, self.type))

    def rotate(self, cw=None):
        if cw:
            pass
        if self.rotation == 0:
            self.body[1].x -= grid.x_unit
            self.body[1].y += grid.y_unit
            self.body[2].x -= grid.x_unit * 2
            self.body[2].y += grid.y_unit * 2
            self.body[3].x -= grid.x_unit * 3
            self.body[3].y += grid.y_unit * 3
            self.rotation += 1
        elif self.rotation == 1:
            self.body[1].x += grid.x_unit
            self.body[1].y -= grid.y_unit
            self.body[2].x += grid.x_unit * 2
            self.body[2].y -= grid.y_unit * 2
            self.body[3].x += grid.x_unit * 3
            self.body[3].y -= grid.y_unit * 3
            self.rotation = 0

        if self.collide_block() and self.y > 0:
            self.rotate()
        self.correct_off_screen_x()
        self.correct_off_screen_y()


class OBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y, 'OBlock')
        self.body.append(Block(self.x, self.y, self.type))
        self.body.append(Block(self.x, self.y + grid.y_unit, self.type))
        self.body.append(Block(self.x + grid.x_unit, self.y, self.type))
        self.body.append(Block(self.x + grid.x_unit, self.y + grid.y_unit, self.type))

    def rotate(self, cw=None):
        pass


class SBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y, 'SBlock')
        self.body.append(Block(self.x, self.y + grid.y_unit, self.type))
        self.body.append(Block(self.x + grid.x_unit, self.y + grid.y_unit, self.type))
        self.body.append(Block(self.x + grid.x_unit, self.y, self.type))
        self.body.append(Block(self.x + grid.x_unit * 2, self.y, self.type))

    def rotate(self, cw=None):
        if cw:
            pass
        if self.rotation == 0:
            self.body[0].y += grid.y_unit
            self.body[0].x += grid.x_unit
            self.body[2].x -= grid.x_unit
            self.body[2].y += grid.y_unit
            self.body[3].x -= grid.x_unit * 2
            self.rotation += 1
        elif self.rotation == 1:
            self.body[0].y -= grid.y_unit
            self.body[0].x -= grid.x_unit
            self.body[2].x += grid.x_unit
            self.body[2].y -= grid.y_unit
            self.body[3].x += grid.x_unit * 2
            self.rotation = 0

        if self.collide_block() and self.y > 0:
            self.rotate()
        self.correct_off_screen_x()
        self.correct_off_screen_y()


class ZBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y, 'ZBlock')
        self.body.append(Block(self.x, self.y, self.type))
        self.body.append(Block(self.x + grid.x_unit, self.y, self.type))
        self.body.append(Block(self.x + grid.x_unit, self.y + grid.y_unit, self.type))
        self.body.append(Block(self.x + grid.x_unit * 2, self.y + grid.y_unit, self.type))

    def rotate(self, cw=None):
        # only here to avoid pycharm warning
        if cw:
            pass

        if self.rotation == 0:
            self.body[0].y += grid.y_unit
            self.body[0].x += grid.x_unit
            self.body[2].x -= grid.x_unit
            self.body[2].y += grid.y_unit
            self.body[3].x -= grid.x_unit * 2
            self.rotation += 1
        elif self.rotation == 1:
            self.body[0].y -= grid.y_unit
            self.body[0].x -= grid.x_unit
            self.body[2].x += grid.x_unit
            self.body[2].y -= grid.y_unit
            self.body[3].x += grid.x_unit * 2
            self.rotation = 0

        if self.collide_block() and self.y > 0:
            self.rotate()
        self.correct_off_screen_x()
        self.correct_off_screen_y()


def draw_bg_grid(div_color=None):
    if div_color is None:
        div_color = grid_color
    for i in range(0, grid.cols + 1):
        pygame.draw.rect(screen, div_color, (grid.x_unit * i + grid.x, grid.y, 1, grid.y_unit * grid.rows))
    for i in range(0, grid.rows + 1):
        pygame.draw.rect(screen, div_color, (grid.x, grid.y_unit * i + grid.y, grid.x_unit * grid.cols, 1))


def fall_tet():
    global falling_tet

    if falling_tet is not None:
        falling_tet.move_y(grid.y_unit)


def lock_tet():
    global falling_tet

    if falling_tet is not None:
        if not falling_tet.locked and falling_tet.collide_y(grid.y_unit):
            falling_tet.locked = True
            falling_tet.influence = lock_delay
        if falling_tet.influence > 0 and falling_tet.collide_y(grid.y_unit):
            falling_tet.influence -= 1
        elif falling_tet.influence > 0 and not falling_tet.collide_y(grid.y_unit):
            falling_tet.locked = False
            falling_tet.influence = -1
        elif falling_tet.influence == 0 and falling_tet.collide_y(grid.y_unit):
            falling_tet.lock_blocks()
            falling_tet = None
            spawn_random_tet()


def player_move_tet():
    global falling_tet

    if falling_tet is not None:
        if move_left:
            falling_tet.move_x(-grid.x_unit)
        elif move_right:
            falling_tet.move_x(grid.x_unit)


def drop_blocks():
    for blk in blocks:
        if blk.drop > 0:
            blk.unlock()
            blk.y += grid.y_unit * blk.drop
            blk.lock()
            blk.drop = 0


def clear_blocks():
    temp_array = []
    temp_block_array = []
    for blk in blocks:
        if blk.locked and blk.x != 0:
            temp_array.append(blk.grid_pos[0])
            temp_block_array.append(blk)
    # strings = []
    for i in range(1, grid.rows + 1):
        if temp_array.count(i) == grid.cols:
            for z in range(len(temp_array)):
                if temp_array[z] == i:
                    temp_block_array[z].clear()
    #     string = 'r' + str(i) + ':' + str(temp_array.count(i))
    #     strings.append(string)
    # print(strings)


def spawn_random_tet(ran_pos=False):
    global falling_tet
    global last_spawned_tet

    if falling_tet is None and allow_spawn:
        i = random.randint(0, len(tet_array) - 1)
        # Prevent same block 3 times in a row
        if tet_array_str[i] == last_spawned_tet[0] and tet_array_str[i] == last_spawned_tet[1]:
            spawn_random_tet()
            return
        # 2/3 chance to re-roll if same block as last
        elif tet_array_str[i] == last_spawned_tet[1]:
            roll = random.randint(0, 2)
            if roll > 0:
                last_spawned_tet = [last_spawned_tet[1], tet_array_str[i]]
                spawn_random_tet()
                return
        if ran_pos:
            ran_x = random.randint(grid.x, grid.x_unit * grid.cols)
        else:
            ran_x = (grid.x_unit * grid.cols) / 2 - grid.x_unit * 2
            if tet_array_str[i] == 'OBlock':
                ran_x += grid.x_unit
        ran_x = int(ran_x - (ran_x % grid.x_unit))

        falling_tet = tet_array[i](grid.x + ran_x, grid.y + -grid.y_unit * 2)

        last_spawned_tet = [last_spawned_tet[1], tet_array_str[i]]


def round_over():
    global blocks
    global falling_tet
    global round_frame_timer
    global rounds_played_count
    global cleared_blocks_count
    global spawn_timer
    global allow_spawn

    num_active = int(len(blocks))
    num_clear = int(cleared_blocks_count / grid.cols)

    blocks = []
    falling_tet = None
    cleared_blocks_count = 0

    if num_active != 0:
        rounds_played_count += 1
        print('########################################################################################')
        print('')
        print('cleared rows: ' + str(num_clear) + ', active blocks: ' + str(num_active) +
              ', round frames: ' + str(round_frame_timer) + ', global frames: ' + str(global_frame_timer) +
              ', round: ' + str(rounds_played_count))
        print('')
        print('########################################################################################')
    round_frame_timer = 0
    allow_spawn = False
    spawn_timer = frame_rate * 4


def mouse_click():
    global mouse_pos
    mouse_pos = pygame.mouse.get_pos()

    # Move game grid to mouse pos
    grid.move_pos(mouse_pos[0] - grid.x, mouse_pos[1] - grid.y)


def shadow_tet():
    global shadow

    # Create or destroy shadow
    if shadow is None and falling_tet is not None:
        shadow = tet_array[tet_array_str.index(falling_tet.type)](falling_tet.x, falling_tet.y)
        shadow.shadow_blocks()
    elif shadow is not None and (falling_tet is None or falling_tet.type != shadow.type):
        shadow = None

    # Cast shadow from falling tet
    if shadow is not None and falling_tet is not None:
        # Reset shadow pos
        shadow.update_pos(falling_tet.x, falling_tet.y)

        # Match rotation
        if shadow.rotation != falling_tet.rotation:
            shadow.rotate()
            if shadow.rotation != falling_tet.rotation:
                shadow.rotate(True)
                shadow.rotate(True)

        shadow.shadow_drop()
        for blk in shadow.body:
            blk.draw()


# Game grid
grid_rows = 15
grid_cols = 10
grid_width = 400
grid_height = 600
grid = GameGrid(120, 69, grid_width, grid_height, grid_rows, grid_cols)

# Delays and cool downs
fall_cool_down = frame_rate / 2
lock_delay = frame_rate / 2
hold_delay = frame_rate / 5

# Game data
shadow = None
blocks = []
last_spawned_tet = ['', '']
falling_tet = None
tet_color_dict = {'TBlock': purple, 'JBlock': blue, 'LBlock': orange, 'IBlock': cyan, 'OBlock': yellow,
                  'SBlock': green, 'ZBlock': red}
tet_array = [TBlock, JBlock, LBlock, IBlock, OBlock, SBlock, ZBlock]
tet_array_str = ['TBlock', 'JBlock', 'LBlock', 'IBlock', 'OBlock', 'SBlock', 'ZBlock']

# Control variables
quick_drop = False
move_left = False
move_right = False
allow_spawn = False
mouse_hold = False

# Timers and counters
move_delay_timer = 0
fall_cool_down_timer = 0
round_frame_timer = 0
global_frame_timer = 0
spawn_timer = 0
rounds_played_count = 0
cleared_blocks_count = 0

running = True
paused = False

while running:
    screen.fill(black)
    if paused:
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
                if falling_tet is None:
                    falling_tet = JBlock((grid.x_unit * grid.cols) / 2 - grid.x_unit, grid.y - grid.y_unit * 2)
            # Spawn LBlock
            if keys[K_l]:
                if falling_tet is None:
                    falling_tet = LBlock((grid.x_unit * grid.cols) / 2 - grid.x_unit, grid.y - grid.y_unit * 2)
            # Spawn IBlock
            if keys[K_i]:
                if falling_tet is None:
                    falling_tet = IBlock((grid.x_unit * grid.cols) / 2 - grid.x_unit, grid.y - grid.y_unit * 2)
            # Spawn OBlock
            if keys[K_o]:
                if falling_tet is None:
                    falling_tet = OBlock((grid.x_unit * grid.cols) / 2 - grid.x_unit, grid.y - grid.y_unit * 2)
            # Spawn SBlock
            if keys[K_s]:
                if falling_tet is None:
                    falling_tet = SBlock((grid.x_unit * grid.cols) / 2 - grid.x_unit, grid.y - grid.y_unit * 2)
            # Spawn ZBlock
            if keys[K_z]:
                if falling_tet is None:
                    falling_tet = ZBlock((grid.x_unit * grid.cols) / 2 - grid.x_unit, grid.y - grid.y_unit * 2)
            # Spawn TBlock
            if keys[K_t]:
                if falling_tet is None:
                    falling_tet = TBlock((grid.x_unit * grid.cols) / 2 - grid.x_unit, grid.y - grid.y_unit * 2)
            # Rotate falling block
            if keys[K_r]:
                if falling_tet is not None:
                    falling_tet.rotate()
            elif keys[K_e]:
                if falling_tet is not None:
                    falling_tet.rotate(True)
            # Move falling block right
            if keys[K_RIGHT] and not move_right:
                move_right = True
                player_move_tet()
                move_delay_timer = hold_delay
            # Move falling block left
            if keys[K_LEFT] and not move_left:
                move_left = True
                player_move_tet()
                move_delay_timer = hold_delay
            # Turn on quick drop
            if keys[K_DOWN] and not quick_drop:
                quick_drop = True
            # Generate random block
            if keys[K_SPACE]:
                allow_spawn = True
                spawn_random_tet()
            # Pause
            if keys[K_p] and not paused:
                paused = True
            elif keys[K_p] and paused:
                paused = False

        # Key up events
        if event.type == pygame.KEYUP:
            # Turn off quick drop
            if not keys[K_DOWN] and quick_drop:
                quick_drop = False
            # Stop move falling block right
            if not keys[K_RIGHT] and move_right:
                move_delay_timer = 0
                move_right = False
            # Stop move falling block left
            if not keys[K_LEFT] and move_left:
                move_delay_timer = 0
                move_left = False

        # Mouse down event
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_hold = True
                mouse_pos = pygame.mouse.get_pos()
                grid.move_pos(mouse_pos[0] - grid.x, mouse_pos[1] - grid.y)

        # Mouse up event
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_hold = False

        # Window resize event
        if event.type == pygame.VIDEORESIZE:
            screen_width = event.w
            screen_height = event.h
            screen = pygame.display.set_mode((screen_width, screen_height), RESIZABLE)

    # Mouse actions
    if mouse_hold:
        mouse_click()

    # Block updates
    shadow_tet()
    spawn_random_tet()
    if not paused:
        if fall_cool_down_timer == 0 or quick_drop:
            drop_blocks()
            fall_tet()
            clear_blocks()
            fall_cool_down_timer = fall_cool_down
        elif fall_cool_down_timer > 0:
            fall_cool_down_timer -= 1
        lock_tet()
        if move_delay_timer == 0:
            player_move_tet()
        elif move_delay_timer > 0:
            move_delay_timer -= 1
        if spawn_timer > 1:
            spawn_timer -= 1
        elif spawn_timer == 1:
            allow_spawn = True
            spawn_timer = 0

    # Draw blocks
    for block in blocks:
        block.draw()
    if falling_tet is not None:
        for block in falling_tet.body:
            block.draw()

    if not paused:
        round_frame_timer += 1
    global_frame_timer += 1

    clock.tick(frame_rate)
    pygame.display.flip()

pygame.display.quit()
pygame.quit()
