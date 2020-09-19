import pygame
from pygame.locals import *
import random


pygame.init()

# Screen default
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
small_font = pygame.font.SysFont(font_face, 15)


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
        self.color = grid_color

    def new_pos(self, new_x, new_y):
        x_offset = new_x - self.x
        y_offset = new_y - self.y
        self.x += x_offset
        self.y += y_offset
        self.right_edge = self.x + self.width
        self.bottom = self.y + self.height
        for blk in blocks:
            blk.x += x_offset
            blk.y += y_offset
        if falling_tet is not None:
            falling_tet.new_pos(falling_tet.x + x_offset, falling_tet.y + y_offset)
        if falling_tet_shadow is not None:
            # noinspection PyUnresolvedReferences
            falling_tet_shadow.new_pos(falling_tet_shadow.x + x_offset, falling_tet_shadow.y + y_offset)
        if next_tet is not None:
            # noinspection PyUnresolvedReferences
            next_tet.new_pos(next_tet.x + x_offset, next_tet.y + y_offset)

    def draw(self, div_color=None):
        if div_color is None:
            div_color = self.color
        # Draw vertical lines
        for i in range(0, self.cols + 1):
            pygame.draw.rect(screen, div_color, (self.x + self.x_unit * i, self.y, 1, self.y_unit * self.rows))
        # Draw horizontal lines
        for i in range(0, self.rows + 1):
            pygame.draw.rect(screen, div_color, (self.x, self.y + self.y_unit * i, self.x_unit * self.cols, 1))


class Block:
    def __init__(self, x, y, tet_type=''):
        self.x = int(x)
        self.y = int(y)
        self.width = grid.x_unit
        self.height = grid.y_unit
        self.locked = False
        self.color = default_block_color
        self.drop = 0
        self.type = tet_type
        self.grid_pos = (-1, -1)
        self.shadow = False
        self.kill_me = False

    def draw(self):
        accent0 = [self.color[0] * 0.2, self.color[1] * 0.2, self.color[2] * 0.2]
        accent1 = [self.color[0] * 0.4, self.color[1] * 0.4, self.color[2] * 0.4]
        accent2 = [self.color[0] * 0.6, self.color[1] * 0.6, self.color[2] * 0.6]
        accent3 = [self.color[0] * 0.8, self.color[1] * 0.8, self.color[2] * 0.8]
        pygame.draw.rect(screen, accent0, (self.x + 1, self.y + 1, self.width - 1, self.height - 1))
        pygame.draw.rect(screen, accent1, (self.x + 2, self.y + 2, self.width - 4, self.height - 4))
        pygame.draw.rect(screen, accent2, (self.x + 4, self.y + 4, self.width - 8, self.height - 8))
        pygame.draw.rect(screen, accent3, (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
        if not self.shadow:
            pygame.draw.rect(screen, self.color, (self.x + 6, self.y + 6, self.width - 12, self.height - 12))
        else:
            pygame.draw.rect(screen, accent2, (self.x + 6, self.y + 6, self.width - 12, self.height - 12))
            pygame.draw.rect(screen, accent1, (self.x + 7, self.y + 7, self.width - 14, self.height - 14))
            pygame.draw.rect(screen, accent0, (self.x + 9, self.y + 9, self.width - 18, self.height - 18))
            pygame.draw.rect(screen, black, (self.x + 11, self.y + 11, self.width - 22, self.height - 22))

    def drop_row(self):
        if self.drop > 0 and self.grid_pos[0] != -1:
            if len(row_state[self.grid_pos[0]]) > 0:
                row_state[self.grid_pos[0]].pop(0)
            self.grid_pos = (self.grid_pos[0] - self.drop, self.grid_pos[1])
            row_state[self.grid_pos[0]].append(1)
            self.y += grid.y_unit * self.drop

            self.drop = 0

    def lock(self):
        row_pos = grid.rows - int((self.y - grid.y) / grid.y_unit) - 1
        col_pos = int((self.x - grid.x) / grid.x_unit)

        if 0 <= row_pos <= grid.rows - 1:
            pass
        else:
            row_pos = -1
        if 0 <= col_pos <= grid.cols - 1:
            pass
        else:
            col_pos = -1

        self.grid_pos = (row_pos, col_pos)
        row_state[self.grid_pos[0]].append(1)
        self.change_color()
        self.locked = True

    def unlock(self):
        if len(row_state[self.grid_pos[0]]) > 0:
            row_state[self.grid_pos[0]].pop(0)
        self.locked = False

    def clear(self):
        global cleared_blocks_count

        for blk in blocks:
            if blk.grid_pos[0] > self.grid_pos[0] and blk.grid_pos[1] == self.grid_pos[1]:
                blk.drop += 1

        self.grid_pos = (-1, -1)
        self.y = -1000
        self.kill_me = True

        cleared_blocks_count += 1

    def change_color(self, change=None):
        if change is None:
            if self.type in tet_colors:
                self.color = tet_colors[self.type]
            else:
                self.color = pink
        else:
            self.color = change

    def show_coord(self):
        coord = small_font.render(str(self.grid_pos), True, black)
        screen.blit(coord, (self.x + 6, self.y + 6))


class Tet:
    def __init__(self, x, y, kind=''):
        if kind in tet_colors:
            tet_color = tet_colors[kind]
        else:
            tet_color = default_block_color
        self.x = int(x)
        self.y = int(y)
        self.rotation = 0
        self.body = []
        self.locked = False
        self.death_timer = -1
        self.type = kind
        self.color = tet_color
        if kind == '':
            self.body.append(Block(self.x, self.y))
        elif kind in tet_offsets:
            for i in range(len(tet_offsets[kind][0])):
                x_offset = grid.x_unit * tet_offsets[kind][0][i][0]
                y_offset = grid.y_unit * tet_offsets[kind][0][i][1]
                self.body.append(Block(self.x + x_offset, self.y + y_offset, self.type))

    def move_x(self, x_offset):
        edge = False
        for blk in self.body:
            if blk.x + x_offset >= grid.right_edge or \
                    blk.x + x_offset < grid.x:
                edge = True
                break
        if self.check_collide_block(x_mod=x_offset):
            edge = True
        if not edge:
            for blk in self.body:
                blk.x += x_offset
            self.x += x_offset

    def move_y(self, y_offset):
        if not self.check_collide_drop():
            for blk in self.body:
                blk.y += y_offset
            self.y += y_offset

    def new_pos(self, new_x=None, new_y=None):
        if new_x is None:
            new_x = self.x
        if new_y is None:
            new_y = self.y

        for blk in self.body:
            blk.x = new_x + (blk.x - self.x)
            blk.y = new_y + (blk.y - self.y)

        self.x = new_x
        self.y = new_y

    def insta_drop(self):
        if self.check_collide_drop():
            return
        else:
            self.move_y(grid.y_unit)
            self.insta_drop()

    def check_collide_drop(self):
        for self_blk in self.body:
            if self_blk.y + grid.y_unit >= grid.bottom:
                return True
            for blk in blocks:
                if self_blk is not blk:
                    if self_blk.y + grid.y_unit == blk.y and self_blk.x == blk.x:
                        return True
        return False

    def check_collide_block(self, x_mod=0, y_mod=0):
        for self_blk in self.body:
            for blk in blocks:
                if self_blk.x + x_mod == blk.x and \
                        self_blk.y + y_mod == blk.y:
                    return True
        return False

    def correct_off_grid_x(self):
        off_screen = None
        for blk in self.body:
            if blk.x >= grid.right_edge:
                off_screen = 'right'
                break
            elif blk.x < grid.x:
                off_screen = 'left'
                break
        if off_screen == 'right':
            self.x -= grid.x_unit
            for blk in self.body:
                blk.x -= grid.x_unit
            self.correct_off_grid_x()
        elif off_screen == 'left':
            self.x += grid.x_unit
            for blk in self.body:
                blk.x += grid.x_unit
            self.correct_off_grid_x()

    def correct_below_grid(self):
        off_screen = False
        for blk in self.body:
            if blk.y >= grid.bottom:
                off_screen = True
                break
        if off_screen:
            self.y -= grid.y_unit
            for blk in self.body:
                blk.y -= grid.y_unit
            self.correct_below_grid()

    def lock_blocks(self):
        if self.y >= grid.y:
            for i in range(len(self.body)):
                blocks.append(self.body[i])
                blocks[len(blocks) - 1].lock()
        elif self.y < grid.y:
            round_over()

    def change_block_colors(self, new_color=None):
        if new_color is None:
            new_color = self.color
        else:
            self.color = new_color

        for blk in self.body:
            blk.change_color(new_color)

    def shadow_blocks(self, do=True):
        if do:
            self.change_block_colors()
            for blk in self.body:
                blk.shadow = True
        else:
            self.change_block_colors(default_block_color)
            for blk in self.body:
                blk.shadow = False

    def rotate(self, reverse=False, jump=None):
        if jump is not None:
            if 0 <= jump <= len(tet_offsets[self.type]) - 1:
                for i in range(len(tet_offsets[self.type])):
                    x_offset = grid.x_unit * tet_offsets[self.type][jump][i][0]
                    y_offset = grid.y_unit * tet_offsets[self.type][jump][i][1]
                    self.body[i].x = self.x + x_offset
                    self.body[i].y = self.y + y_offset
                self.rotation = jump
        else:
            if reverse:
                if self.rotation - 1 < 0:
                    self.rotation = len(tet_offsets[self.type]) - 1
                else:
                    self.rotation -= 1
            else:
                if self.rotation + 1 > len(tet_offsets[self.type]) - 1:
                    self.rotation = 0
                else:
                    self.rotation += 1

            for i in range(len(tet_offsets[self.type])):
                x_offset = grid.x_unit * tet_offsets[self.type][self.rotation][i][0]
                y_offset = grid.y_unit * tet_offsets[self.type][self.rotation][i][1]
                self.body[i].x = self.x + x_offset
                self.body[i].y = self.y + y_offset

            if self.check_collide_block():
                self.rotate(not reverse)

        self.correct_off_grid_x()
        self.correct_below_grid()

    def draw(self):
        for blk in self.body:
            blk.draw()

    def needs_to_die(self):
        if not self.locked and self.check_collide_drop():
            self.locked = True
            self.death_timer = lock_delay
        if self.death_timer > 0 and self.check_collide_drop():
            self.death_timer -= 1
        elif self.death_timer > 0 and not self.check_collide_drop():
            self.locked = False
            self.death_timer = -1
        elif self.death_timer == 0 and self.check_collide_drop():
            self.lock_blocks()
            clear_rows()
            return True
        return False


def player_move_tet():
    global falling_tet

    if falling_tet is not None:
        if move_left:
            falling_tet.move_x(-grid.x_unit)
        elif move_right:
            falling_tet.move_x(grid.x_unit)


def shadow_tet():
    global falling_tet_shadow

    # Create or destroy shadow
    if falling_tet_shadow is None and falling_tet is not None:
        falling_tet_shadow = Tet(falling_tet.x, falling_tet.y, falling_tet.type)
        falling_tet_shadow.shadow_blocks()
    elif falling_tet_shadow is not None and (falling_tet is None or falling_tet.type != falling_tet_shadow.type):
        falling_tet_shadow = None

    # Cast shadow from falling tet
    if falling_tet_shadow is not None and falling_tet is not None:
        # Reset shadow pos
        falling_tet_shadow.new_pos(falling_tet.x, falling_tet.y)

        # Match rotation
        if falling_tet.rotation != falling_tet_shadow.rotation:
            falling_tet_shadow.rotate(jump=falling_tet.rotation)

        falling_tet_shadow.insta_drop()


def spawn_next_tet(ran_pos=False):
    global falling_tet
    global last_spawned_tet
    global next_tet

    if next_tet is None:
        new_tet = random.choice(list(tet_offsets.keys()))
        # Prevent same block 3 times in a row
        if new_tet == last_spawned_tet[0] and new_tet == last_spawned_tet[1]:
            spawn_next_tet()
            return
        # 2/3 chance to re-roll if same block as last
        elif new_tet == last_spawned_tet[1]:
            roll = random.randint(0, 2)
            if roll != 0:
                last_spawned_tet = [last_spawned_tet[1], new_tet]
                spawn_next_tet()
                return

        next_tet = Tet(grid.right_edge + 15, grid.y, new_tet)
        next_tet.change_block_colors()
        last_spawned_tet = [last_spawned_tet[1], new_tet]

    elif next_tet is not None and falling_tet is None and allow_spawn:
        new_tet = random.choice(list(tet_offsets.keys()))
        # Prevent same block 3 times in a row
        if new_tet == last_spawned_tet[0] and new_tet == last_spawned_tet[1]:
            spawn_next_tet()
            return
        # 2/3 chance to re-roll if same block as last
        elif new_tet == last_spawned_tet[1]:
            roll = random.randint(0, 2)
            if roll != 0:
                last_spawned_tet = [last_spawned_tet[1], new_tet]
                spawn_next_tet()
                return
        if ran_pos:
            ran_x = random.randint(grid.x, grid.x_unit * grid.cols)
        else:
            ran_x = (grid.x_unit * grid.cols) / 2 - grid.x_unit * 2

        ran_x = int(ran_x - (ran_x % grid.x_unit))

        falling_tet = next_tet
        next_tet = Tet(grid.right_edge + 10, grid.y, new_tet)
        next_tet.change_block_colors()
        falling_tet.change_block_colors(default_block_color)
        falling_tet.new_pos(grid.x + ran_x, grid.y + -grid.y_unit * 4)
        last_spawned_tet = [last_spawned_tet[1], new_tet]


def clear_rows():
    for r in range(len(row_state)):
        if len(row_state[r]) >= grid.cols:
            row_state[r] = []
            for blk in blocks:
                if blk.grid_pos[0] == r:
                    blk.clear()
    to_kill = []
    for blk in blocks:
        if blk.kill_me:
            to_kill.append(blocks.index(blk))
        blk.drop_row()

    to_kill.sort(reverse=True)
    for i in range(len(to_kill)):
        blocks.pop(to_kill[i])


def round_over():
    global blocks
    global falling_tet
    global round_frame_timer
    global rounds_played_count
    global cleared_blocks_count
    global next_round_timer
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
    next_round_timer = frame_rate * 4


# Game clock
clock = pygame.time.Clock()
frame_rate = 60

# Game grid
grid_rows = 15
grid_cols = 10
grid_width = 400
grid_height = 600
grid = GameGrid(20, 20, grid_width, grid_height, grid_rows, grid_cols)

# Delays and cool downs
fall_cool_down = frame_rate
lock_delay = frame_rate / 2
hold_delay = frame_rate / 5

# Game data
default_block_color = white
blocks = []
last_spawned_tet = ['', '']
next_tet = None
falling_tet = None
falling_tet_shadow = None
row_state = []
for row in range(grid.rows):
    row_state.append([])

tet_colors = {'TBlock': purple, 'JBlock': blue, 'LBlock': orange, 'IBlock': cyan, 'OBlock': yellow,
              'SBlock': green, 'ZBlock': red}

# 'TetType': [[offsets for rotation 0 = (block0), (block1), ... ], [offsets for rotation 1], ... ]]
# Example: x/y_offset = tet_offsets['TetType'][rotation #][block #][x or y]
tet_offsets = {
    'TBlock': [[(0, 1), (1, 1), (2, 1), (1, 2)],
               [(1, 0), (1, 1), (1, 2), (0, 1)],
               [(2, 2), (1, 2), (0, 2), (1, 1)],
               [(1, 2), (1, 1), (1, 0), (2, 1)]],
    'JBlock': [[(0, 1), (1, 1), (2, 1), (2, 2)],
               [(1, 0), (1, 1), (1, 2), (0, 2)],
               [(2, 2), (1, 2), (0, 2), (0, 1)],
               [(1, 2), (1, 1), (1, 0), (2, 0)]],
    'LBlock': [[(0, 1), (1, 1), (2, 1), (0, 2)],
               [(1, 0), (1, 1), (1, 2), (0, 0)],
               [(2, 2), (1, 2), (0, 2), (2, 1)],
               [(1, 2), (1, 1), (1, 0), (2, 2)]],
    'IBlock': [[(0, 1), (1, 1), (2, 1), (3, 1)],
               [(2, 0), (2, 1), (2, 2), (2, 3)],
               [(0, 2), (1, 2), (2, 2), (3, 2)],
               [(1, 0), (1, 1), (1, 2), (1, 3)]],
    'SBlock': [[(1, 1), (2, 1), (0, 2), (1, 2)],
               [(2, 1), (2, 2), (1, 0), (1, 1)],
               [(1, 1), (0, 1), (2, 0), (1, 0)],
               [(0, 1), (0, 0), (1, 2), (1, 1)]],
    'ZBlock': [[(0, 1), (1, 1), (1, 2), (2, 2)],
               [(2, 0), (2, 1), (1, 1), (1, 2)],
               [(2, 1), (1, 1), (1, 0), (0, 0)],
               [(0, 2), (0, 1), (1, 1), (1, 0)]],
    'OBlock': [[(1, 0), (2, 0), (1, 1), (2, 1)]]
}

# Control variables
quick_drop = False
insta_drop = False
move_left = False
move_right = False
allow_spawn = False
mouse_hold = False
show_coords = False

# Timers and counters
move_delay_timer = 0
fall_cool_down_timer = 0
round_frame_timer = 0
global_frame_timer = 0
next_round_timer = 0
rounds_played_count = 0
cleared_blocks_count = 0

running = True
paused = False
while running:
    screen.fill(black)

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

            # Show block coords
            if keys[K_x] and not show_coords:
                show_coords = True
            elif keys[K_x] and show_coords:
                show_coords = False

            # Spawn TBlock
            if keys[K_t]:
                if falling_tet is None:
                    falling_tet = Tet(grid.x + (grid.x_unit * grid.cols) / 2 - grid.x_unit * 2,
                                      grid.y - grid.y_unit * 2, 'TBlock')
            # Spawn JBlock
            if keys[K_j]:
                if falling_tet is None:
                    falling_tet = Tet(grid.x + (grid.x_unit * grid.cols) / 2 - grid.x_unit * 2,
                                      grid.y - grid.y_unit * 2, 'JBlock')
            # Spawn LBlock
            if keys[K_l]:
                if falling_tet is None:
                    falling_tet = Tet(grid.x + (grid.x_unit * grid.cols) / 2 - grid.x_unit * 2,
                                      grid.y - grid.y_unit * 2, 'LBlock')
            # Spawn IBlock
            if keys[K_i]:
                if falling_tet is None:
                    falling_tet = Tet(grid.x + (grid.x_unit * grid.cols) / 2 - grid.x_unit * 2,
                                      grid.y - grid.y_unit * 2, 'IBlock')
            # Spawn OBlock
            if keys[K_o]:
                if falling_tet is None:
                    falling_tet = Tet(grid.x + (grid.x_unit * grid.cols) / 2 - grid.x_unit * 2,
                                      grid.y - grid.y_unit * 2, 'OBlock')
            # Spawn SBlock
            if keys[K_s]:
                if falling_tet is None:
                    falling_tet = Tet(grid.x + (grid.x_unit * grid.cols) / 2 - grid.x_unit * 2,
                                      grid.y - grid.y_unit * 2, 'SBlock')
            # Spawn ZBlock
            if keys[K_z]:
                if falling_tet is None:
                    falling_tet = Tet(grid.x + (grid.x_unit * grid.cols) / 2 - grid.x_unit * 2,
                                      grid.y - grid.y_unit * 2, 'ZBlock')
            # Spawn single block
            if keys[K_f]:
                if falling_tet is None:
                    falling_tet = Tet(grid.x + (grid.x_unit * grid.cols) / 2 - grid.x_unit * 2,
                                      grid.y - grid.y_unit * 2)

            # Generate random block
            if keys[K_SPACE]:
                allow_spawn = True
                spawn_next_tet()

            # Rotate falling block
            if keys[K_r]:
                if falling_tet is not None and not paused:
                    falling_tet.rotate()
            elif keys[K_e]:
                if falling_tet is not None and not paused:
                    falling_tet.rotate(True)
            # Move falling block right
            if keys[K_RIGHT] and not move_right:
                move_right = True
                if not paused:
                    player_move_tet()
                    move_delay_timer = hold_delay
            # Move falling block left
            if keys[K_LEFT] and not move_left:
                move_left = True
                if not paused:
                    player_move_tet()
                    move_delay_timer = hold_delay
            # Turn on quick drop
            if keys[K_DOWN] and not quick_drop:
                quick_drop = True
            # Turn on insta drop
            if keys[K_UP] and not insta_drop:
                insta_drop = True

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
            # Turn off insta drop
            if not keys[K_UP] and insta_drop:
                insta_drop = False
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
                grid.new_pos(mouse_pos[0] - grid.x, mouse_pos[1] - grid.y)

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
        mouse_pos = pygame.mouse.get_pos()
        grid.new_pos(mouse_pos[0], mouse_pos[1])

    # Block updates
    shadow_tet()
    spawn_next_tet()
    if not paused:
        clear_rows()
        if fall_cool_down_timer == 0:
            if falling_tet is not None:
                falling_tet.move_y(grid.y_unit)
            fall_cool_down_timer = fall_cool_down
        elif fall_cool_down_timer > 0:
            fall_cool_down_timer -= 1

        if falling_tet is not None:
            if quick_drop:
                falling_tet.move_y(grid.y_unit)
            elif insta_drop:
                falling_tet.insta_drop()

        if falling_tet is not None and falling_tet.needs_to_die():
            falling_tet = None
            spawn_next_tet()

        if move_delay_timer == 0:
            player_move_tet()
        elif move_delay_timer > 0:
            move_delay_timer -= 1

        if next_round_timer > 1:
            next_round_timer -= 1
        elif next_round_timer == 1:
            allow_spawn = True
            next_round_timer = 0

    # Draw next round timer
    if next_round_timer > 0:
        next_game = main_font.render(str(next_round_timer), True, white)
        screen.blit(next_game, (10, 10))

    # Draw num of rows cleared
    rows_cleared_txt = main_font.render(str(int(cleared_blocks_count / grid.cols)) + ' cleared rows', True, white)
    screen.blit(rows_cleared_txt, (grid.right_edge + 20, grid.y + grid.y_unit * 5))

    # Draw grid
    if paused:
        grid.draw(pink)
    else:
        grid.draw()

    # Draw blocks
    if next_tet is not None:
        # noinspection PyUnresolvedReferences
        next_tet.draw()
    if falling_tet_shadow is not None:
        # noinspection PyUnresolvedReferences
        falling_tet_shadow.draw()
    if falling_tet is not None:
        falling_tet.draw()
    for block in blocks:
        block.draw()
        if show_coords:
            block.show_coord()

    if not paused:
        round_frame_timer += 1
    global_frame_timer += 1

    clock.tick(frame_rate)
    pygame.display.flip()

pygame.display.quit()
pygame.quit()
