import pygame
from pygame.locals import *


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
grid_color = [50, 50, 50]
# Font
font_size = 25
font_face = "Helvetica"
main_font = pygame.font.SysFont(font_face, font_size)


class Block:
    def __init__(self, x, y, block_color=None):
        if block_color is None:
            block_color = white
        self.x = x
        self.y = y
        self.width = grid_size
        self.height = grid_size
        self.locked = False
        self.color = block_color
        self.index = None
        self.cleared = False
        self.drop = 0

    def draw(self):
        if not self.cleared:
            pygame.draw.rect(screen, grid_color, (self.x, self.y, self.height, self.width))
            pygame.draw.rect(screen, self.color, (self.x + 1, self.y + 1, self.height - 1, self.width - 1))

    def lock(self):
        if not self.locked:
            self.color = blue
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

    def update_x(self, x_offset):
        if self.x + x_offset < 0:
            return
        elif self.x + x_offset > screen_width - grid_size:
            return
        for blk in blocks:
            if not blk.locked or blk.influence > 0 or blk.cleared:
                continue
            if self.x + x_offset == blk.x:
                return
        self.x += x_offset


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
            if falling_blocks[self.body[i]].x + x_offset > screen_width - 1 or \
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
            if falling_blocks[self.body[i]].y + grid_size >= screen_height:
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

    def lock(self):
        if self.locked and self.influence == 0:
            for i in range(len(self.body)):
                blocks.append(falling_blocks[self.body[i]])
                blocks[len(blocks) - 1].lock()
            self.body.sort(reverse=True)
            for i in range(len(self.body)):
                falling_blocks.pop(self.body[i])
            tet_s.pop(0)


class JBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y + grid_size))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y + grid_size))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 2, self.y + grid_size))

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
        off_screen = 0
        for i in range(len(self.body)):
            if falling_blocks[self.body[i]].x > screen_width - 1:
                off_screen = 1
                break
            elif falling_blocks[self.body[i]].x < 0:
                off_screen = -1
                break
        if off_screen == 1:
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].x -= grid_size
        elif off_screen == -1:
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].x += grid_size


class LBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 2, self.y))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y + grid_size))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y + grid_size))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 2, self.y + grid_size))

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
        off_screen = 0
        for i in range(len(self.body)):
            if falling_blocks[self.body[i]].x > screen_width - 1:
                off_screen = 1
                break
            elif falling_blocks[self.body[i]].x < 0:
                off_screen = -1
                break
        if off_screen == 1:
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].x -= grid_size
        elif off_screen == -1:
            for i in range(len(self.body)):
                falling_blocks[self.body[i]].x += grid_size


class IBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 2, self.y))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size * 3, self.y))

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

        def correct_off_screen():
            off_screen = 0
            for i in range(len(self.body)):
                if falling_blocks[self.body[i]].x > screen_width - 1:
                    off_screen = 1
                    break
                elif falling_blocks[self.body[i]].x < 0:
                    off_screen = -1
                    break
            if off_screen == 1:
                for i in range(len(self.body)):
                    falling_blocks[self.body[i]].x -= grid_size
                correct_off_screen()
            elif off_screen == -1:
                for i in range(len(self.body)):
                    falling_blocks[self.body[i]].x += grid_size
                correct_off_screen()

        correct_off_screen()


class OBlock(Tet):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x, self.y + grid_size))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y))
        self.body.append(len(falling_blocks))
        falling_blocks.append(Block(self.x + grid_size, self.y + grid_size))

    def rotate(self):
        pass


grid_cols = 10
grid_size = int(screen_width / grid_cols)
grid_array = []
for r in range(0, int(screen_width / grid_size)):
    for c in range(0, int(screen_height / grid_size)):
        grid_array.append(0)


def bg_grid():
    for i in range(0, int(screen_width / grid_size)):
        pygame.draw.rect(screen, grid_color, (grid_size * i, 0, 1, screen_height))
    for i in range(0, int(screen_height / grid_size)):
        pygame.draw.rect(screen, grid_color, (0, grid_size * i, screen_width, 1))


def fall_tet():
    for tet in tet_s:
        if not tet.locked:
            tet.update_y(grid_size)


def lock_tet():
    for tet in tet_s:
        if not tet.locked and tet.collide_y():
            tet.locked = True
            tet.influence = lock_delay
        if tet.influence > 0 and tet.collide_y():
            tet.influence -= 1
        elif tet.influence > 0 and not tet.collide_y():
            tet.locked = False
            tet.influence = -1
        elif tet.influence == 0 and tet.collide_y():
            tet.lock()


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


fall_cool_down_timer = 0
fall_cool_down = frame_rate / 2
influence = False
lock_delay = frame_rate / 2
blocks = []
falling_blocks = []
tet_s = []
running = True
while running:
    screen.fill(black)
    bg_grid()
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
                if len(tet_s) == 0:
                    tet_s.append(JBlock(0, 0))
            # Spawn LBlock
            if keys[K_l]:
                if len(tet_s) == 0:
                    tet_s.append(LBlock(0, 0))
            # Spawn IBlock
            if keys[K_i]:
                if len(tet_s) == 0:
                    tet_s.append(IBlock(0, 0))
            # Spawn OBlock
            if keys[K_o]:
                if len(tet_s) == 0:
                    tet_s.append(OBlock(0, 0))
            # Move falling block right
            if keys[K_RIGHT]:
                if len(tet_s) != 0:
                    tet_s[0].update_x(grid_size)
            # Move falling block left
            if keys[K_LEFT]:
                if len(tet_s) != 0:
                    tet_s[0].update_x(-grid_size)
            # Rotate falling block
            if keys[K_r]:
                if len(tet_s) != 0:
                    tet_s[0].rotate()

        # Key up events
        if event.type == pygame.KEYUP:
            pass

    # Block updates
    if fall_cool_down_timer == 0:
        drop_blocks()
        fall_tet()
        clear_blocks()
        fall_cool_down_timer = fall_cool_down
    elif fall_cool_down_timer != 0:
        fall_cool_down_timer -= 1
    lock_tet()
    # Draw blocks
    for block in blocks:
        block.draw()
    for block in falling_blocks:
        block.draw()

    clock.tick(frame_rate)
    pygame.display.flip()


pygame.display.quit()
pygame.quit()
