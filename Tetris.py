import pygame
from pygame.locals import *
import random


pygame.init()
clock = pygame.time.Clock()
frame_rate = 60
# Screen
screen_width = 500
screen_height = 600
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
        self.index = None
        self.cleared = False
        self.drop = 0
        self.type = tet_type

    def draw(self):
        if not self.cleared:
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
            self.index = int((self.y / grid_size) * grid_cols + (self.x / grid_size))
            grid_array[self.index] = 1

    def unlock(self):
        if self.locked:
            self.locked = False
            grid_array[self.index] = 0

    def clear(self):
        self.cleared = True
        grid_array[self.index] = 0

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
            for bi in range(len(blocks)):
                if blocks[bi].cleared:
                    continue
                if falling_blocks[self.body[i]].x + x_offset == blocks[bi].x and \
                        falling_blocks[self.body[i]].y == blocks[bi].y:
                    edge = True
                    break
        if not edge:
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].x += x_offset
            self.x += x_offset

    def update_y(self, y_offset):
        edge = self.collide_y()
        if not edge:
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].y += y_offset
            self.y += y_offset

    def collide_y(self):
        collide = False
        for i in range(len(self.body)):
            if falling_blocks[self.body[i]].y + grid_size >= grid_size * grid_rows:
                collide = True
                break
            for bi in range(len(blocks)):
                if blocks[bi].cleared:
                    continue
                if falling_blocks[self.body[i]].y + grid_size == blocks[bi].y and \
                        falling_blocks[self.body[i]].x == blocks[bi].x:
                    collide = True
                    break
        if collide:
            return True
        else:
            return False

    def correct_off_screen_x(self):
        off_screen = 0
        for i in range(len(self.body)):
            if falling_blocks[self.body[i]].x >= grid_size * grid_cols:
                off_screen = 1
                break
            elif falling_blocks[self.body[i]].x < 0:
                off_screen = -1
                break
        if off_screen == 1:
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].x -= grid_size
            self.correct_off_screen_x()
        elif off_screen == -1:
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
        if self.locked and self.influence == 0:
            for i in range(len(self.body)):
                blocks.append(falling_blocks[self.body[i]])
                blocks[len(blocks) - 1].lock()
            self.body.sort(reverse=True)
            for i in range(len(self.body)):
                falling_blocks.pop(self.body[i])
            tet_list.pop(0)


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

    def rotate(self):
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

    def rotate(self):
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

    def rotate(self):
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

    def rotate(self):
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

    def rotate(self):
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

    def rotate(self):
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

    def rotate(self):
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

        self.correct_off_screen_x()
        self.correct_off_screen_y()


grid_rows = 19
grid_size = int(screen_height / grid_rows)
grid_cols = screen_width / grid_size
if grid_cols % 1 >= 0.5:
    grid_cols = int(grid_cols) + 1
else:
    grid_cols = int(grid_cols)
grid_array = []
for r in range(0, grid_cols):
    for c in range(0, grid_rows):
        grid_array.append(0)


def draw_bg_grid():
    for i in range(0, grid_cols + 1):
        pygame.draw.rect(screen, grid_color, (grid_size * i, 0, 1, screen_height))
    for i in range(0, grid_rows + 1):
        pygame.draw.rect(screen, grid_color, (0, grid_size * i, screen_width, 1))


def fall_tet():
    for t in tet_list:
        if not t.locked:
            t.update_y(grid_size)


def lock_tet():
    for t in tet_list:
        if not t.locked and t.collide_y():
            t.locked = True
            t.influence = lock_delay
        if t.influence > 0 and t.collide_y():
            t.influence -= 1
        elif t.influence > 0 and not t.collide_y():
            t.locked = False
            t.influence = -1
        elif t.influence == 0 and t.collide_y():
            t.commit_self_die()
            spawn_random_tet()


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
    for row in range(int(len(grid_array) / grid_cols)):
        temp_list = []
        for col in range(0, grid_cols):
            if grid_array[(row * grid_cols) + col] == 1:
                temp_list.append((row * grid_cols) + col)
            else:
                temp_list = []
            y_threshold = -1
            if len(temp_list) == grid_cols:
                for blk in blocks:
                    if blk.index in temp_list:
                        blk.clear()
                        if blk.y < y_threshold or y_threshold == -1:
                            y_threshold = blk.y
                if y_threshold != -1:
                    for blk in blocks:
                        if not blk.cleared and blk.locked and blk.y < y_threshold:
                            blk.drop += 1
    for blk in blocks:
        if blk.locked and blk.y < 0:
            round_over()


def spawn_random_tet():
    if len(tet_list) == 0:
        tet_array = [TBlock, JBlock, LBlock, IBlock, OBlock, SBlock, ZBlock]
        ran_tet = random.randint(0, len(tet_array) - 1)
        # ran_x = random.randint(0, grid_size * grid_cols)
        ran_x = screen_width / 2
        ran_x = int(ran_x - (ran_x % grid_size)) - grid_size
        tet_list.append(tet_array[ran_tet](ran_x, -grid_size * 2))
        tet_list[len(tet_list) - 1].correct_off_screen_x()


def round_over():
    global score
    global blocks
    global falling_blocks
    global tet_list

    num_clear = 0
    for blk in blocks:
        if blk.cleared:
            num_clear += 1
    num_active = len(blocks) - num_clear
    num_clear /= grid_cols
    score = int(((num_clear * 10) + (num_active * 2)) / 20)
    blocks = []
    falling_blocks = []
    tet_list = []

    for i in range(len(grid_array)):
        grid_array[i] = 0
    if score != 0:
        print(score)


score = 0
fall_cool_down_timer = 0
fall_cool_down = frame_rate / 2
lock_delay = frame_rate / 2
blocks = []
falling_blocks = []
tet_list = []
quick_drop = False
move_left = False
move_right = False
move_delay = 0
running = True
while running:
    screen.fill(black)
    draw_bg_grid()
    # Event loop
    for event in pygame.event.get():
        # Close window
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
            # Move falling block right
            if keys[K_RIGHT] and not move_right:
                move_delay = 0
                move_right = True
                move_tet()
                move_delay = frame_rate / 4
            # Move falling block left
            if keys[K_LEFT] and not move_left:
                move_delay = 0
                move_left = True
                move_tet()
                move_delay = frame_rate / 4
            # Turn on quick drop
            if keys[K_DOWN] and not quick_drop:
                quick_drop = True
            # Generate random block
            if keys[K_SPACE]:
                spawn_random_tet()

        # Key up events
        if event.type == pygame.KEYUP:
            # Turn off quick drop
            if not keys[K_DOWN] and quick_drop:
                quick_drop = False
            # Stop move falling block right
            if not keys[K_RIGHT] and move_right:
                move_right = False
            # Stop move falling block left
            if not keys[K_LEFT] and move_left:
                move_left = False

    # Block updates
    if fall_cool_down_timer == 0 or quick_drop:
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

    clock.tick(frame_rate)
    pygame.display.flip()


pygame.display.quit()
pygame.quit()
