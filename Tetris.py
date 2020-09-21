import pygame
from pygame.locals import *
import random

pygame.init()
clock = pygame.time.Clock()
frame_rate = 60

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

# Tet information
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


# Need to add collide check on hold swap
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
        self.blocks = []
        self.row_state = []
        for row in range(self.rows):
            self.row_state.append([])
        self.faller = None
        self.shadow = None
        self.next_tet = None
        self.held_tet = None
        self.last_spawned = ['', '']
        self.cleared = 0
        self.rounds = 0
        self.round_time = 0
        self.fall_delay_timer = 0
        self.move_delay_timer = 0
        self.next_round_timer = 0
        self.allow_spawn = False
        self.paused = False
        self.quick_drop = False
        self.move_left = False
        self.move_right = False
        self.show_coords = False
        self.drop_rate = frame_rate
        self.default_block_color = white
        self.lock_delay = frame_rate / 2
        self.hold_delay = frame_rate / 5

    def new_pos(self, new_x, new_y):
        x_offset = new_x - self.x
        y_offset = new_y - self.y
        self.x += x_offset
        self.y += y_offset
        self.right_edge = self.x + self.width
        self.bottom = self.y + self.height
        for blk in self.blocks:
            blk.x += x_offset
            blk.y += y_offset
        if isinstance(self.faller, Tet):
            self.faller.new_pos(self.faller.x + x_offset, self.faller.y + y_offset)
            self.faller.grid_x = self.x
            self.faller.grid_y = self.y
            self.faller.right_edge = self.right_edge
            self.faller.bottom = self.bottom
        if isinstance(self.shadow, Tet):
            self.shadow.new_pos(self.shadow.x + x_offset, self.shadow.y + y_offset)
            self.shadow.grid_x = self.x
            self.shadow.grid_y = self.y
            self.shadow.right_edge = self.right_edge
            self.shadow.bottom = self.bottom
        if isinstance(self.next_tet, Tet):
            self.next_tet.new_pos(self.next_tet.x + x_offset, self.next_tet.y + y_offset)
            self.next_tet.grid_x = self.x
            self.next_tet.grid_y = self.y
            self.next_tet.right_edge = self.right_edge
            self.next_tet.bottom = self.bottom
        if isinstance(self.held_tet, Tet):
            self.held_tet.new_pos(self.next_tet.x + x_offset, self.next_tet.y + y_offset)
            self.held_tet.grid_x = self.x
            self.held_tet.grid_y = self.y
            self.held_tet.right_edge = self.right_edge
            self.held_tet.bottom = self.bottom

    def draw(self, div_color=None):
        if div_color is None:
            div_color = self.color
        # Draw vertical lines
        for i in range(0, self.cols + 1):
            pygame.draw.rect(screen, div_color, (self.x + self.x_unit * i, self.y, 1, self.y_unit * self.rows))
        # Draw horizontal lines
        for i in range(0, self.rows + 1):
            pygame.draw.rect(screen, div_color, (self.x, self.y + self.y_unit * i, self.x_unit * self.cols, 1))
        # Draw locked blocks
        for blk in self.blocks:
            blk.draw()
            if self.show_coords:
                blk.show_coord()
        # Draw tets
        if isinstance(self.shadow, Tet):
            self.shadow.draw()
        if isinstance(self.next_tet, Tet):
            self.next_tet.draw()
        if isinstance(self.held_tet, Tet):
            self.held_tet.draw()
        if isinstance(self.faller, Tet):
            self.faller.draw()

        # Update timers
        if not self.paused:
            self.round_time += 1
            # Delay for quick movement
            if self.move_delay_timer > 0:
                self.move_delay_timer -= 1
            # Fall Delay
            if self.fall_delay_timer > 0:
                self.fall_delay_timer -= 1
            elif self.fall_delay_timer == 0:
                self.fall_delay_timer = self.drop_rate

            # Timer to start next round
            if self.next_round_timer > 1:
                self.next_round_timer -= 1
            elif self.next_round_timer == 1:
                if self.faller is None:
                    self.allow_spawn = True
                self.next_round_timer = 0

        # Draw next round timer
        if self.next_round_timer > 0:
            next_game = main_font.render(str(self.next_round_timer), True, white)
            screen.blit(next_game, (self.x + 5, self.y + 5))

        # Draw num of rows cleared
        rows_cleared_txt = main_font.render(str(int(self.cleared / self.cols)) + ' cleared rows', True, white)
        screen.blit(rows_cleared_txt, (self.right_edge + 20, self.y + self.y_unit * 5))

    def drop_blocks(self):
        for blk in self.blocks:
            if blk.drop > 0 and blk.grid_pos[0] != -1:
                if len(self.row_state[blk.grid_pos[0]]) > 0:
                    self.row_state[blk.grid_pos[0]].pop(0)
                blk.grid_pos = (blk.grid_pos[0] - blk.drop, blk.grid_pos[1])
                # noinspection PyTypeChecker
                self.row_state[blk.grid_pos[0]].append(1)
                blk.y += self.y_unit * blk.drop

                blk.drop = 0

    def lock_blocks(self):
        for blk in self.blocks:
            if blk.to_lock and not blk.locked:
                row_pos = self.rows - int((blk.y - self.y) / self.y_unit) - 1
                col_pos = int((blk.x - self.x) / self.x_unit)

                if 0 <= row_pos <= self.rows - 1:
                    pass
                else:
                    row_pos = -1
                if 0 <= col_pos <= self.cols - 1:
                    pass
                else:
                    col_pos = -1

                blk.grid_pos = (row_pos, col_pos)
                self.row_state[blk.grid_pos[0]].append(1)
                blk.to_lock = False
                blk.locked = True

    def clear_blocks(self):
        for blk in self.blocks:
            if blk.clear_me:
                for blk2 in self.blocks:
                    if blk is not blk2:
                        if blk2.grid_pos[0] > blk.grid_pos[0] and blk2.grid_pos[1] == blk.grid_pos[1]:
                            blk2.drop += 1

                blk.grid_pos = (-1, -1)
                blk.y = self.y - 1000
                blk.clear_me = False
                blk.kill_me = True

                self.cleared += 1

    def clear_rows(self):
        for r in range(len(self.row_state)):
            if len(self.row_state[r]) >= self.cols:
                self.row_state[r] = []
                for blk in self.blocks:
                    if blk.grid_pos[0] == r:
                        blk.clear()
        to_kill = []
        for blk in self.blocks:
            if blk.kill_me:
                to_kill.append(game_grid.blocks.index(blk))
        self.clear_blocks()
        to_kill.sort(reverse=True)
        for i in range(len(to_kill)):
            self.blocks.pop(to_kill[i])

    def end_round(self):
        num_active = int(len(self.blocks))
        num_clear = int(self.cleared / self.cols)

        self.blocks = []
        self.faller = None
        self.shadow = None
        self.next_tet = None
        self.held_tet = None
        self.cleared = 0
        for i in range(len(self.row_state)):
            self.row_state[i] = []

        if num_active != 0:
            self.rounds += 1
            print('######################################################################')
            print('')
            print('cleared rows: ' + str(num_clear) + ', active blocks: ' + str(num_active) +
                  ', round frames: ' + str(self.round_time) + ', round: ' + str(self.rounds))
            print('')
            print('#######################################################################')
        self.round_time = 0
        self.allow_spawn = False
        self.next_round_timer = frame_rate * 4

    def generate_tets(self, ran_pos=False):
        if self.next_tet is None:
            new_tet = random.choice(list(tet_offsets.keys()))
            # Prevent same block 3 times in a row
            if new_tet == self.last_spawned[0] and new_tet == self.last_spawned[1]:
                self.generate_tets()
                return
            # 2/3 chance to re-roll if same block as last
            elif new_tet == self.last_spawned[1]:
                roll = random.randint(0, 2)
                if roll != 0:
                    self.last_spawned = [self.last_spawned[1], new_tet]
                    self.generate_tets()
                    return

            self.next_tet = Tet(self, self.right_edge + 15, self.y, new_tet)
            self.next_tet.change_block_colors()
            self.last_spawned = [self.last_spawned[1], new_tet]

        elif isinstance(self.next_tet, Tet) and self.faller is None and self.allow_spawn:
            new_tet = random.choice(list(tet_offsets.keys()))
            # Prevent same block 3 times in a row
            if new_tet == self.last_spawned[0] and new_tet == self.last_spawned[1]:
                self.generate_tets()
                return
            # 2/3 chance to re-roll if same block as last
            elif new_tet == self.last_spawned[1]:
                roll = random.randint(0, 2)
                if roll != 0:
                    self.last_spawned = [self.last_spawned[1], new_tet]
                    self.generate_tets()
                    return
            if ran_pos:
                ran_x = random.randint(self.x, self.x_unit * self.cols)
            else:
                ran_x = (self.x_unit * self.cols) / 2 - self.x_unit * 2

            ran_x = int(ran_x - (ran_x % self.x_unit))

            self.faller = self.next_tet
            self.next_tet = Tet(self, self.right_edge + 10, self.y, new_tet)
            self.next_tet.change_block_colors()
            self.faller.change_block_colors(self.default_block_color)
            self.faller.new_pos(self.x + ran_x, self.y + -self.y_unit * 4)
            self.last_spawned = [self.last_spawned[1], new_tet]

    def hold_tet(self):
        if isinstance(self.faller, Tet) and isinstance(self.next_tet, Tet):
            if self.held_tet is None:
                self.held_tet = Tet(self, self.right_edge + 15, self.y + self.y_unit * 10, self.faller.type)
                self.held_tet.rotate(jump=self.faller.rotation)
                self.held_tet.change_block_colors()

                self.faller = Tet(self, self.faller.x, self.faller.y, self.next_tet.type)

                self.next_tet = None
                self.generate_tets()
            elif isinstance(self.held_tet, Tet):
                new_hold = Tet(self, self.held_tet.x, self.held_tet.y, self.faller.type)
                new_hold.rotation = self.faller.rotation

                self.faller = Tet(self, self.faller.x, self.faller.y, self.held_tet.type)
                self.faller.rotate(jump=self.held_tet.rotation)

                self.held_tet = Tet(self, new_hold.x, new_hold.y, new_hold.type)
                self.held_tet.rotate(jump=new_hold.rotation)
                self.held_tet.change_block_colors()

    def cast_shadow(self):
        # Create or destroy shadow
        if self.shadow is None and isinstance(self.faller, Tet):
            self.shadow = Tet(self, self.faller.x, self.faller.y, self.faller.type)
            self.shadow.shadow_blocks()
        elif isinstance(self.shadow, Tet) and \
                (self.faller is None or self.faller.type != self.shadow.type):
            self.shadow = None

        # Cast shadow from falling tet
        if isinstance(self.shadow, Tet) and isinstance(self.faller, Tet):
            # Reset shadow pos
            self.shadow.new_pos(self.faller.x, self.faller.y)

            # Match rotation
            if self.faller.rotation != self.shadow.rotation:
                self.shadow.rotate(jump=self.faller.rotation)

            self.shadow.insta_drop(self)

    def player_move_faller(self):
        if self.move_delay_timer == 0:
            if isinstance(self.faller, Tet):
                if self.move_left:
                    self.faller.move_x(self, -self.x_unit)
                elif self.move_right:
                    self.faller.move_x(self, self.x_unit)

    def move_tet(self):
        # Fall Tet
        if isinstance(self.faller, Tet):
            if self.quick_drop:
                self.faller.move_y(self, self.y_unit)
            elif self.fall_delay_timer == 0:
                self.faller.move_y(self, self.y_unit)

            # Check if need to lock or end round
            self.faller.update_state(self)

        # Kill Tet
        if isinstance(self.faller, Tet) and self.faller.needs_to_die:
            self.faller = None
            self.generate_tets()

        # Player movements
        self.player_move_faller()

    def play(self):
        self.generate_tets()
        self.cast_shadow()
        if not game_grid.paused:
            self.move_tet()
            self.lock_blocks()
            self.clear_rows()
            self.drop_blocks()

        # Draw grid
        if game_grid.paused:
            self.draw(pink)
        else:
            self.draw()


class Block:
    def __init__(self, grid: GameGrid, x, y, tet_type=''):
        self.x = int(x)
        self.y = int(y)
        self.width = grid.x_unit
        self.height = grid.y_unit
        self.to_lock = False
        self.locked = False
        self.clear_me = False
        self.kill_me = False
        self.color = grid.default_block_color
        self.drop = 0
        self.type = tet_type
        self.grid_pos = (-1, -1)
        self.shadow = False

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

    def lock(self):
        self.change_color()
        self.to_lock = True

    def clear(self):
        self.clear_me = True

    def change_color(self, change=None):
        if change is None:
            if self.type in tet_colors:
                self.color = tet_colors[self.type]
            else:
                self.color = pink
        else:
            self.color = change

    def show_coord(self):
        coord = small_font.render(str(self.grid_pos[0]) + ', ' + str(self.grid_pos[1]), True, black)
        screen.blit(coord, (self.x + 5, self.y + self.height - 22))


class Tet:
    def __init__(self, grid: GameGrid, x, y, kind=''):
        if kind in tet_colors:
            tet_color = tet_colors[kind]
        else:
            tet_color = grid.default_block_color
        self.x = int(x)
        self.y = int(y)
        self.grid_x = grid.x
        self.grid_y = grid.y
        self.right_edge = grid.right_edge
        self.bottom = grid.bottom
        self.x_unit = grid.x_unit
        self.y_unit = grid.y_unit
        self.rotation = 0
        self.body = []
        self.locked = False
        self.insta = False
        self.death_timer = -1
        self.needs_to_die = False
        self.type = kind
        self.color = tet_color
        if kind == '':
            self.body.append(Block(grid, self.x, self.y))
        elif kind in tet_offsets:
            for i in range(len(tet_offsets[kind][0])):
                x_offset = grid.x_unit * tet_offsets[kind][0][i][0]
                y_offset = grid.y_unit * tet_offsets[kind][0][i][1]
                self.body.append(Block(grid, self.x + x_offset, self.y + y_offset, self.type))

    def move_x(self, grid: GameGrid, x_offset):
        if self.check_collide(grid, x_mod=x_offset, bottom=False):
            return
        # Move blocks
        for blk in self.body:
            blk.x += x_offset
        self.x += x_offset

    def move_y(self, grid: GameGrid, y_offset):
        if not self.check_collide(grid, y_mod=y_offset):
            for blk in self.body:
                blk.y += y_offset
            self.y += y_offset

    def new_pos(self, new_x=None, new_y=None):
        # Move with no collision check
        if new_x is None:
            new_x = self.x
        if new_y is None:
            new_y = self.y

        for blk in self.body:
            blk.x = new_x + (blk.x - self.x)
            blk.y = new_y + (blk.y - self.y)

        self.x = new_x
        self.y = new_y

    def rotate(self, reverse=False, jump=None, ignore_checks=False):
        # Jump to specific rotation state. No collision checks
        if jump is not None:
            if 0 <= jump <= len(tet_offsets[self.type]) - 1:
                for i in range(len(tet_offsets[self.type])):
                    x_offset = self.x_unit * tet_offsets[self.type][jump][i][0]
                    y_offset = self.y_unit * tet_offsets[self.type][jump][i][1]
                    self.body[i].x = self.x + x_offset
                    self.body[i].y = self.y + y_offset
                self.rotation = jump
        else:  # If normal rotation
            # Set new rotation value
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

            # Set blocks to new rotation value
            for i in range(len(tet_offsets[self.type])):
                x_offset = self.x_unit * tet_offsets[self.type][self.rotation][i][0]
                y_offset = self.y_unit * tet_offsets[self.type][self.rotation][i][1]
                self.body[i].x = self.x + x_offset
                self.body[i].y = self.y + y_offset

            # Check for collision. Then check if moving left or right is possible. If not, then undo rotation
            if not ignore_checks:
                if self.check_grid_collide():
                    self.new_pos(self.x + self.x_unit)
                    if self.check_grid_collide():
                        self.new_pos(self.x - self.x_unit * 2)
                    if self.check_grid_collide():
                        self.new_pos(self.x + self.x_unit)
                        self.rotate(not reverse)

    def draw(self):
        for blk in self.body:
            blk.draw()

    def insta_drop(self, grid: GameGrid):
        if self.check_collide(grid, y_mod=self.y_unit):
            self.insta = True
            return
        else:
            self.move_y(grid, self.y_unit)
            self.insta_drop(grid)

    def check_grid_collide(self, x_mod=0, y_mod=0, bottom=True, walls=True):
        for blk in self.body:
            if walls:
                if not self.grid_x <= blk.x + x_mod <= self.right_edge - self.x_unit:
                    return True
            if bottom:
                if blk.y + y_mod >= self.bottom:
                    return True
        return False

    def check_block_collide(self, grid: GameGrid, x_mod=0, y_mod=0):
        for blk in self.body:
            for grid_blk in grid.blocks:
                if blk.x + x_mod == grid_blk.x and blk.y + y_mod == grid_blk.y:
                    return True
        return False

    def check_collide(self, grid: GameGrid, x_mod=0, y_mod=0, bottom=True):
        for blk in self.body:
            if not self.grid_x <= blk.x + x_mod <= self.right_edge - self.x_unit:
                return True
            if bottom:
                if blk.y + y_mod >= self.bottom:
                    return True
            for grid_blk in grid.blocks:
                if blk.x + x_mod == grid_blk.x and blk.y + y_mod == grid_blk.y:
                    return True
        return False

    def update_state(self, grid: GameGrid):
        if not self.locked and self.check_collide(grid, y_mod=self.y_unit):
            self.locked = True
            if self.insta:
                self.death_timer = int(grid.lock_delay * 1.3)
            else:
                self.death_timer = grid.lock_delay
        if self.death_timer > 0 and self.check_collide(grid, y_mod=self.y_unit):
            self.death_timer -= 1
        elif self.death_timer > 0 and not self.check_collide(grid, y_mod=self.y_unit):
            self.locked = False
            self.death_timer = -1
        elif self.death_timer == 0 and self.check_collide(grid, y_mod=self.y_unit):
            self.lock_blocks(grid)
            self.needs_to_die = True

    def lock_blocks(self, grid: GameGrid):
        for blk in self.body:
            if blk.y <= self.grid_y - self.y_unit:
                grid.end_round()
                return
            else:
                grid.blocks.append(blk)
                grid.blocks[len(grid.blocks) - 1].lock()
        self.body = []

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


# Game grid
grid_rows = 15
grid_cols = 10
grid_width = 400
grid_height = 600
game_grid = GameGrid(20, 20, grid_width, grid_height, grid_rows, grid_cols)

mouse_hold = False

running = True
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
            if keys[K_x] and not game_grid.show_coords:
                game_grid.show_coords = True
            elif keys[K_x] and game_grid.show_coords:
                game_grid.show_coords = False

            # Spawn TBlock
            if keys[K_t]:
                if game_grid.faller is None:
                    game_grid.faller = Tet(game_grid,
                                           game_grid.x + (game_grid.x_unit * game_grid.cols) / 2 - game_grid.x_unit * 2,
                                           game_grid.y - game_grid.y_unit * 2, 'TBlock')
                    next_round_timer = 0
                elif isinstance(game_grid.faller, Tet) and isinstance(game_grid.next_tet, Tet):
                    game_grid.next_tet = Tet(game_grid, game_grid.right_edge + 15, game_grid.y, 'TBlock')
                    game_grid.next_tet.change_block_colors()
                    game_grid.last_spawned[1] = game_grid.next_tet.type
            # Spawn JBlock
            if keys[K_j]:
                if game_grid.faller is None:
                    game_grid.faller = Tet(game_grid,
                                           game_grid.x + (game_grid.x_unit * game_grid.cols) / 2 - game_grid.x_unit * 2,
                                           game_grid.y - game_grid.y_unit * 2, 'JBlock')
                    next_round_timer = 0
                elif isinstance(game_grid.faller, Tet) and isinstance(game_grid.next_tet, Tet):
                    game_grid.next_tet = Tet(game_grid, game_grid.right_edge + 15, game_grid.y, 'JBlock')
                    game_grid.next_tet.change_block_colors()
                    game_grid.last_spawned[1] = game_grid.next_tet.type
            # Spawn LBlock
            if keys[K_l]:
                if game_grid.faller is None:
                    game_grid.faller = Tet(game_grid,
                                           game_grid.x + (game_grid.x_unit * game_grid.cols) / 2 - game_grid.x_unit * 2,
                                           game_grid.y - game_grid.y_unit * 2, 'LBlock')
                    next_round_timer = 0
                elif isinstance(game_grid.faller, Tet) and isinstance(game_grid.next_tet, Tet):
                    game_grid.next_tet = Tet(game_grid, game_grid.right_edge + 15, game_grid.y, 'LBlock')
                    game_grid.next_tet.change_block_colors()
                    game_grid.last_spawned[1] = game_grid.next_tet.type
            # Spawn IBlock
            if keys[K_i]:
                if game_grid.faller is None:
                    game_grid.faller = Tet(game_grid,
                                           game_grid.x + (game_grid.x_unit * game_grid.cols) / 2 - game_grid.x_unit * 2,
                                           game_grid.y - game_grid.y_unit * 2, 'IBlock')
                    next_round_timer = 0
                elif isinstance(game_grid.faller, Tet) and isinstance(game_grid.next_tet, Tet):
                    game_grid.next_tet = Tet(game_grid, game_grid.right_edge + 15, game_grid.y, 'IBlock')
                    game_grid.next_tet.change_block_colors()
                    game_grid.last_spawned[1] = game_grid.next_tet.type
            # Spawn OBlock
            if keys[K_o]:
                if game_grid.faller is None:
                    game_grid.faller = Tet(game_grid,
                                           game_grid.x + (game_grid.x_unit * game_grid.cols) / 2 - game_grid.x_unit * 2,
                                           game_grid.y - game_grid.y_unit * 2, 'OBlock')
                    next_round_timer = 0
                elif isinstance(game_grid.faller, Tet) and isinstance(game_grid.next_tet, Tet):
                    game_grid.next_tet = Tet(game_grid, game_grid.right_edge + 15, game_grid.y, 'OBlock')
                    game_grid.next_tet.change_block_colors()
                    game_grid.last_spawned[1] = game_grid.next_tet.type
            # Spawn SBlock
            if keys[K_s]:
                if game_grid.faller is None:
                    game_grid.faller = Tet(game_grid,
                                           game_grid.x + (game_grid.x_unit * game_grid.cols) / 2 - game_grid.x_unit * 2,
                                           game_grid.y - game_grid.y_unit * 2, 'SBlock')
                    next_round_timer = 0
                elif isinstance(game_grid.faller, Tet) and isinstance(game_grid.next_tet, Tet):
                    game_grid.next_tet = Tet(game_grid, game_grid.right_edge + 15, game_grid.y, 'SBlock')
                    game_grid.next_tet.change_block_colors()
                    game_grid.last_spawned[1] = game_grid.next_tet.type
            # Spawn ZBlock
            if keys[K_z]:
                if game_grid.faller is None:
                    game_grid.faller = Tet(game_grid,
                                           game_grid.x + (game_grid.x_unit * game_grid.cols) / 2 - game_grid.x_unit * 2,
                                           game_grid.y - game_grid.y_unit * 2, 'ZBlock')
                    next_round_timer = 0
                elif isinstance(game_grid.faller, Tet) and isinstance(game_grid.next_tet, Tet):
                    game_grid.next_tet = Tet(game_grid, game_grid.right_edge + 15, game_grid.y, 'ZBlock')
                    game_grid.next_tet.change_block_colors()
                    game_grid.last_spawned[1] = game_grid.next_tet.type
            # Spawn single block
            if keys[K_f]:
                if game_grid.faller is None:
                    game_grid.faller = Tet(game_grid,
                                           game_grid.x + (game_grid.x_unit * game_grid.cols) / 2 - game_grid.x_unit * 2,
                                           game_grid.y - game_grid.y_unit * 2)
                    next_round_timer = 0
                elif isinstance(game_grid.faller, Tet) and isinstance(game_grid.next_tet, Tet):
                    game_grid.next_tet = Tet(game_grid, game_grid.right_edge + 15, game_grid.y)
                    game_grid.next_tet.change_block_colors()
                    game_grid.last_spawned[1] = game_grid.next_tet.type

            # Generate random block
            if keys[K_SPACE]:
                game_grid.allow_spawn = True
                game_grid.generate_tets()

            # Hold current block
            if keys[K_h]:
                game_grid.hold_tet()
            # Rotate held block
            if keys[K_3]:
                if isinstance(game_grid.held_tet, Tet):
                    game_grid.held_tet.rotate(reverse=True, ignore_checks=True)
            elif keys[K_4]:
                if isinstance(game_grid.held_tet, Tet):
                    game_grid.held_tet.rotate(ignore_checks=True)

            # Rotate falling block
            if keys[K_r]:
                if isinstance(game_grid.faller, Tet) and not game_grid.paused:
                    if not game_grid.faller.needs_to_die:
                        game_grid.faller.rotate()
            elif keys[K_e]:
                if isinstance(game_grid.faller, Tet) and not game_grid.paused:
                    if not game_grid.faller.needs_to_die:
                        game_grid.faller.rotate(reverse=True)
            # Move falling block right
            if keys[K_RIGHT] and not game_grid.move_right:
                game_grid.move_right = True
                if not game_grid.paused:
                    game_grid.player_move_faller()
                    game_grid.move_delay_timer = game_grid.hold_delay
            # Move falling block left
            if keys[K_LEFT] and not game_grid.move_left:
                game_grid.move_left = True
                if not game_grid.paused:
                    game_grid.player_move_faller()
                    game_grid.move_delay_timer = game_grid.hold_delay
            # Turn on quick drop
            if keys[K_DOWN] and not game_grid.quick_drop:
                game_grid.quick_drop = True
            # Turn on insta drop
            if keys[K_UP] and isinstance(game_grid.faller, Tet):
                game_grid.faller.insta_drop(game_grid)

            # Pause
            if keys[K_p] and not game_grid.paused:
                game_grid.paused = True
            elif keys[K_p] and game_grid.paused:
                game_grid.paused = False

        # Key up events
        if event.type == pygame.KEYUP:
            # Turn off quick drop
            if not keys[K_DOWN] and game_grid.quick_drop:
                game_grid.quick_drop = False
            # Stop move falling block right
            if not keys[K_RIGHT] and game_grid.move_right:
                game_grid.move_delay_timer = 0
                game_grid.move_right = False
            # Stop move falling block left
            if not keys[K_LEFT] and game_grid.move_left:
                game_grid.move_delay_timer = 0
                game_grid.move_left = False

        # Mouse down event
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_hold = True
                mouse_pos = pygame.mouse.get_pos()
                game_grid.new_pos(mouse_pos[0] - game_grid.x, mouse_pos[1] - game_grid.y)

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
        game_grid.new_pos(mouse_pos[0], mouse_pos[1])

    game_grid.play()

    clock.tick(frame_rate)
    pygame.display.flip()

pygame.display.quit()
pygame.quit()
