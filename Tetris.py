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
big_font = pygame.font.SysFont(font_face, 80)

# Tet information
tet_colors = {'TBlock': purple, 'JBlock': blue, 'LBlock': orange, 'IBlock': cyan, 'OBlock': yellow,
              'SBlock': green, 'ZBlock': red}
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


class GameGrid:
    def __init__(self, x, y, width, height, rows=15, cols=10, lock_aspect=''):
        # Lock aspect and preserve width
        if lock_aspect == 'width':
            self.x_unit = int(width / cols)
            self.y_unit = self.x_unit
        # Lock aspect and preserve height
        elif lock_aspect == 'height':
            self.y_unit = int(height / rows)
            self.x_unit = self.y_unit
        else:
            self.x_unit = int(width / cols)
            self.y_unit = int(height / rows)

        self.on = True
        self.x = int(x)
        self.y = int(y)
        self.rows = int(rows)
        self.cols = int(cols)
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
        self.paused = False
        self.quick_drop = False
        self.move_left = False
        self.move_right = False
        self.show_coords = False
        self.drop_rate = frame_rate
        self.default_block_color = white
        self.lock_delay = frame_rate / 2
        self.hold_delay = frame_rate / 5
        self.pressed_keys = []
        for i in range(323):
            self.pressed_keys.append(0)

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
            self.held_tet.new_pos(self.held_tet.x + x_offset, self.held_tet.y + y_offset)
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
                    self.start_round()
                self.next_round_timer = 0

        # Draw next round timer
        if self.next_round_timer > 0:
            next_game_txt = main_font.render(str(self.next_round_timer), True, white)
            screen.blit(next_game_txt, (self.x + 5, self.y + 5))

        # Draw num of rows cleared
        rows_cleared_txt = main_font.render(str(int(self.cleared / self.cols)) + ' cleared rows', True, white)
        screen.blit(rows_cleared_txt, (self.right_edge + 20, self.y + self.y_unit * 5))

        # PAUSED
        if self.paused:
            paused_txt = big_font.render('PAUSED', True, black)
            screen.blit(paused_txt, (self.x + int((self.right_edge - self.x) / 2) - 137,
                                     self.y + int((self.bottom - self.y) / 2) - 147))
            screen.blit(paused_txt, (self.x + int((self.right_edge - self.x) / 2) - 137,
                                     self.y + int((self.bottom - self.y) / 2) - 143))
            screen.blit(paused_txt, (self.x + int((self.right_edge - self.x) / 2) - 133,
                                     self.y + int((self.bottom - self.y) / 2) - 147))
            screen.blit(paused_txt, (self.x + int((self.right_edge - self.x) / 2) - 133,
                                     self.y + int((self.bottom - self.y) / 2) - 143))
            paused_txt = big_font.render('PAUSED', True, pink)
            screen.blit(paused_txt, (self.x + int((self.right_edge - self.x) / 2) - 135,
                                     self.y + int((self.bottom - self.y) / 2) - 145))

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
            if blk.clear:
                for blk2 in self.blocks:
                    if blk is not blk2:
                        if blk2.grid_pos[0] > blk.grid_pos[0] and blk2.grid_pos[1] == blk.grid_pos[1]:
                            blk2.drop += 1

                blk.grid_pos = (-1, -1)
                blk.y = self.y - 1000
                blk.clear = False
                blk.kill_me = True

                self.cleared += 1

    def clear_rows(self):
        for r in range(len(self.row_state)):
            if len(self.row_state[r]) >= self.cols:
                self.row_state[r] = []
                for blk in self.blocks:
                    if blk.grid_pos[0] == r:
                        blk.clear = True
        to_kill = []
        for blk in self.blocks:
            if blk.kill_me:
                to_kill.append(game_grid.blocks.index(blk))
        self.clear_blocks()
        to_kill.sort(reverse=True)
        for i in range(len(to_kill)):
            self.blocks.pop(to_kill[i])

    def start_round(self):
        self.rounds += 1
        self.generate_tets()
        self.generate_tets()

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
            print('######################################################################')
            print('')
            print('cleared rows: ' + str(num_clear) + ', active blocks: ' + str(num_active) +
                  ', round frames: ' + str(self.round_time) + ', round: ' + str(self.rounds))
            print('')
            print('#######################################################################')
        self.round_time = 0
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

        elif isinstance(self.next_tet, Tet) and self.faller is None:
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
            # Hold falling Tet if not currently holding
            if self.held_tet is None:
                self.held_tet = Tet(self, self.right_edge + 15, self.y + self.y_unit * 10, self.faller.type)
                self.held_tet.rotate(self, jump=self.faller.rotation, ignore_checks=True)
                self.held_tet.change_block_colors()

                self.faller = Tet(self, self.faller.x, self.faller.y, self.next_tet.type)

                self.next_tet = None
                self.generate_tets()
            # Swap falling Tet
            elif isinstance(self.held_tet, Tet):
                new_hold = Tet(self, self.held_tet.x, self.held_tet.y, self.faller.type)
                new_hold.rotation = self.faller.rotation

                self.faller = Tet(self, self.faller.x, self.faller.y, self.held_tet.type)
                self.faller.rotate(self, jump=self.held_tet.rotation)
                self.faller.correct_off_grid()

                self.held_tet = Tet(self, new_hold.x, new_hold.y, new_hold.type)
                self.held_tet.rotate(self, jump=new_hold.rotation, ignore_checks=True)
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
                self.shadow.rotate(self, jump=self.faller.rotation)

            self.shadow.insta_drop(self)

    def player_move_faller(self):
        if self.move_delay_timer == 0:
            if isinstance(self.faller, Tet):
                if self.move_left:
                    self.faller.move_x(self, -self.x_unit)
                elif self.move_right:
                    self.faller.move_x(self, self.x_unit)

    def move_lock_tet(self):
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
            if self.faller.dev:
                self.faller = None
            else:
                self.faller = None
                self.generate_tets()

        # Player movements
        self.player_move_faller()

    def play(self):
        if self.on:
            self.cast_shadow()
            if not self.paused:
                self.move_lock_tet()
                self.lock_blocks()
                self.clear_rows()
                self.drop_blocks()
            self.draw()

    def toggle_on(self):
        if self.on:
            self.paused = True
            self.on = False
        else:
            self.on = True

    def key_down(self, keys):
        keys = list(keys)
        for i in range(len(keys)):
            if self.pressed_keys[i] == keys[i]:
                keys[i] = 0
            else:
                self.pressed_keys[i] = keys[i]

        # Test
        if keys[K_q]:
            self.toggle_on()
        if keys[K_w]:
            self.start_round()

        # Spawn TBlock
        if keys[K_t]:
            if isinstance(self.faller, Tet) and isinstance(self.next_tet, Tet):
                self.next_tet = Tet(self, self.right_edge + 15, self.y, 'TBlock')
                self.next_tet.change_block_colors()
                self.last_spawned[1] = self.next_tet.type
            else:
                self.faller = Tet(self, self.x + (self.x_unit * self.cols) / 2 - self.x_unit * 2,
                                  self.y - self.y_unit * 2, 'TBlock')
                self.faller.dev = True
                self.next_round_timer = 0
        # Spawn JBlock
        if keys[K_j]:
            if isinstance(self.faller, Tet) and isinstance(self.next_tet, Tet):
                self.next_tet = Tet(self, self.right_edge + 15, self.y, 'JBlock')
                self.next_tet.change_block_colors()
                self.last_spawned[1] = self.next_tet.type
            else:
                self.faller = Tet(self, self.x + (self.x_unit * self.cols) / 2 - self.x_unit * 2,
                                  self.y - self.y_unit * 2, 'JBlock')
                self.faller.dev = True
                self.next_round_timer = 0
        # Spawn LBlock
        if keys[K_l]:
            if isinstance(self.faller, Tet) and isinstance(self.next_tet, Tet):
                self.next_tet = Tet(self, self.right_edge + 15, self.y, 'LBlock')
                self.next_tet.change_block_colors()
                self.last_spawned[1] = self.next_tet.type
            else:
                self.faller = Tet(self, self.x + (self.x_unit * self.cols) / 2 - self.x_unit * 2,
                                  self.y - self.y_unit * 2, 'LBlock')
                self.faller.dev = True
                self.next_round_timer = 0
        # Spawn IBlock
        if keys[K_i]:
            if isinstance(self.faller, Tet) and isinstance(self.next_tet, Tet):
                self.next_tet = Tet(self, self.right_edge + 15, self.y, 'IBlock')
                self.next_tet.change_block_colors()
                self.last_spawned[1] = self.next_tet.type
            else:
                self.faller = Tet(self, self.x + (self.x_unit * self.cols) / 2 - self.x_unit * 2,
                                  self.y - self.y_unit * 2, 'IBlock')
                self.faller.dev = True
                self.next_round_timer = 0
        # Spawn OBlock
        if keys[K_o]:
            if isinstance(self.faller, Tet) and isinstance(self.next_tet, Tet):
                self.next_tet = Tet(self, self.right_edge + 15, self.y, 'OBlock')
                self.next_tet.change_block_colors()
                self.last_spawned[1] = self.next_tet.type
            else:
                self.faller = Tet(self, self.x + (self.x_unit * self.cols) / 2 - self.x_unit * 2,
                                  self.y - self.y_unit * 2, 'OBlock')
                self.faller.dev = True
                self.next_round_timer = 0
        # Spawn SBlock
        if keys[K_s]:
            if isinstance(self.faller, Tet) and isinstance(self.next_tet, Tet):
                self.next_tet = Tet(self, self.right_edge + 15, self.y, 'SBlock')
                self.next_tet.change_block_colors()
                self.last_spawned[1] = self.next_tet.type
            else:
                self.faller = Tet(self, self.x + (self.x_unit * self.cols) / 2 - self.x_unit * 2,
                                  self.y - self.y_unit * 2, 'SBlock')
                self.faller.dev = True
                self.next_round_timer = 0
        # Spawn ZBlock
        if keys[K_z]:
            if isinstance(self.faller, Tet) and isinstance(self.next_tet, Tet):
                self.next_tet = Tet(self, self.right_edge + 15, self.y, 'ZBlock')
                self.next_tet.change_block_colors()
                self.last_spawned[1] = self.next_tet.type
            else:
                self.faller = Tet(self, self.x + (self.x_unit * self.cols) / 2 - self.x_unit * 2,
                                  self.y - self.y_unit * 2, 'ZBlock')
                self.faller.dev = True
                self.next_round_timer = 0
        # Spawn single block
        if keys[K_f]:
            if isinstance(self.faller, Tet) and isinstance(self.next_tet, Tet):
                self.next_tet = Tet(self, self.right_edge + 15, self.y)
                self.next_tet.change_block_colors()
                self.last_spawned[1] = self.next_tet.type
            else:
                self.faller = Tet(self, self.x + (self.x_unit * self.cols) / 2 - self.x_unit * 2,
                                  self.y - self.y_unit * 2)
                self.faller.dev = True
                self.next_round_timer = 0

        # Show block coords
        if keys[K_x] and not self.show_coords:
            self.show_coords = True
        elif keys[K_x] and self.show_coords:
            self.show_coords = False

        # Start game / pause
        if keys[K_SPACE]:
            if self.faller is None and self.rounds == 0:
                self.start_round()
            else:
                if self.paused:
                    self.paused = False
                else:
                    self.paused = True

        # Pause
        if keys[K_p] and not self.paused:
            self.paused = True
        elif keys[K_p] and self.paused:
            self.paused = False

        # Player inputs
        if not self.paused:
            # Hold current block
            if keys[K_h]:
                self.hold_tet()
            # Rotate held block
            if keys[K_3]:
                if isinstance(self.held_tet, Tet):
                    self.held_tet.rotate(self, reverse=True, ignore_checks=True)
            elif keys[K_4]:
                if isinstance(self.held_tet, Tet):
                    self.held_tet.rotate(self, ignore_checks=True)

            # Rotate falling block
            if keys[K_r]:
                if isinstance(self.faller, Tet):
                    if not self.faller.needs_to_die:
                        self.faller.rotate(self)
            elif keys[K_e]:
                if isinstance(self.faller, Tet):
                    if not self.faller.needs_to_die:
                        self.faller.rotate(self, reverse=True)
            # Move falling block right
            if keys[K_RIGHT] and not self.move_right:
                self.move_right = True
                if not self.paused:
                    self.player_move_faller()
                    self.move_delay_timer = self.hold_delay
            # Move falling block left
            if keys[K_LEFT] and not self.move_left:
                self.move_left = True
                if not self.paused:
                    self.player_move_faller()
                    self.move_delay_timer = self.hold_delay
            # Turn on quick drop
            if keys[K_DOWN] and not self.quick_drop:
                self.quick_drop = True
            # Turn on insta drop
            if keys[K_UP] and isinstance(self.faller, Tet):
                self.faller.insta_drop(self)

    def key_up(self, keys):
        keys = list(keys)
        keys_up = []
        for i in range(len(keys)):
            keys_up.append(0)
        for i in range(len(keys)):
            if self.pressed_keys[i] > keys[i]:
                self.pressed_keys[i] = 0
                keys_up[i] = 1

        # Turn off quick drop
        if keys_up[K_DOWN] and self.quick_drop:
            self.quick_drop = False
        # Stop move falling block right
        if keys_up[K_RIGHT] and self.move_right:
            self.move_delay_timer = 0
            self.move_right = False
        # Stop move falling block left
        if keys_up[K_LEFT] and self.move_left:
            self.move_delay_timer = 0
            self.move_left = False


class Block:
    def __init__(self, grid: GameGrid, x, y, tet_type=''):
        self.x = int(x)
        self.y = int(y)
        self.width = grid.x_unit
        self.height = grid.y_unit
        self.to_lock = False
        self.locked = False
        self.clear = False
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
        self.dev = False
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

    def rotate(self, grid: GameGrid, reverse=False, jump=None, ignore_checks=False):
        # Jump to specific rotation state
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
            self.correct_off_grid()
            if self.check_collide(grid, bottom=False):
                self.new_pos(self.x + self.x_unit)
                if self.check_collide(grid, bottom=False):
                    self.new_pos(self.x - self.x_unit * 2)
                if self.check_collide(grid, bottom=False):
                    self.new_pos(self.x + self.x_unit)
                    self.rotate(grid, not reverse)

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

    def correct_off_grid(self):
        off_screen = None
        for blk in self.body:
            if blk.x >= self.right_edge:
                off_screen = 'right'
                break
            elif blk.x < self.grid_x:
                off_screen = 'left'
                break
            elif blk.y >= self.bottom:
                off_screen = 'bottom'
                break
        if off_screen == 'right':
            self.x -= self.x_unit
            for blk in self.body:
                blk.x -= self.x_unit
            self.correct_off_grid()
        elif off_screen == 'left':
            self.x += self.x_unit
            for blk in self.body:
                blk.x += self.x_unit
            self.correct_off_grid()
        elif off_screen == 'bottom':
            self.y -= self.y_unit
            for blk in self.body:
                blk.y -= self.y_unit
            self.correct_off_grid()


# Game grid
grid_rows = 19
grid_cols = 10
grid_width = 400
grid_height = 600
game_grid = GameGrid(20, 20, grid_width, grid_height, grid_rows, grid_cols, lock_aspect='height')

mouse_hold = False

running = True
while running:
    screen.fill(black)

    # Event loop
    for event in pygame.event.get():
        keys_list = pygame.key.get_pressed()

        # Press close button
        if event.type == pygame.QUIT:
            running = False
            break

        # Key down events
        if event.type == pygame.KEYDOWN:
            # Close window shortcut
            if (keys_list[K_LCTRL] or keys_list[K_RCTRL]) and keys_list[K_w]:
                running = False
                break

            # Send inputs to game_grid
            game_grid.key_down(keys_list)

        # Key up events
        if event.type == pygame.KEYUP:
            # Update pressed keys in game_grid
            game_grid.key_up(keys_list)

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
