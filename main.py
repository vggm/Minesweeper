import sys
from utils import *
from random import randint
import pygame as pg
from time import sleep
from threading import Thread
import os

# matrix dimension
N = 8
M = 8

# mines
N_MINES = 10

# screen sizes
MENU_WIDTH = 480
MENU_HEIGHT = 480
MENU_SIZE = MENU_WIDTH, MENU_HEIGHT


BOARD_WIDTH = 480
BOARD_HEIGHT = 480
BOARD_SIZE = BOARD_WIDTH, BOARD_HEIGHT

SCREEN_WIDTH = BOARD_WIDTH
SCREEN_HEIGHT = BOARD_HEIGHT + PADDING
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT

# cell sizes
CELL_WIDTH = BOARD_WIDTH // M
CELL_HEIGHT = BOARD_HEIGHT // N
CELL_SIZE = CELL_WIDTH, CELL_HEIGHT


def stopwatch():
  global seconds, sumador
  while clock_start:
    sleep(1)
    seconds += sumador


def update_const():
  global BOARD_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_SIZE, CELL_WIDTH, CELL_HEIGHT, CELL_SIZE
  BOARD_SIZE = BOARD_WIDTH, BOARD_HEIGHT

  SCREEN_WIDTH = BOARD_WIDTH
  SCREEN_HEIGHT = BOARD_HEIGHT + PADDING
  SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT

  CELL_WIDTH = BOARD_WIDTH // M
  CELL_HEIGHT = BOARD_HEIGHT // N
  CELL_SIZE = CELL_WIDTH, CELL_HEIGHT


def coord_to_real(i, j):
  return j*(BOARD_WIDTH//M), i*(BOARD_HEIGHT//N) + PADDING


def real_to_coord(x, y):
  return (y - PADDING)//(BOARD_HEIGHT//N), x//(BOARD_WIDTH//M)


def get_image(url):
  img = pg.image.load(url)
  return pg.transform.scale(img, CELL_SIZE)


def gen_mines(first_i, first_j):
  cont = 0

  min_i = max(first_i-1, 0)
  min_j = max(first_j-1, 0)
  max_i = min(first_i+1, N-1)
  max_j = min(first_j+1, M-1)

  init_area = set()
  for i in range(min_i, max_i + 1):
    for j in range(min_j, max_j + 1):
      init_area.add((i, j))

  while cont < N_MINES:
    i = randint(0, N - 1)
    j = randint(0, M - 1)

    if mines_map[i][j] != MINE and ((i, j) not in init_area):

      mines_map[i][j] = MINE
      mines_list.add((i, j))
      cont += 1

      min_i = max(i - 1, 0)
      min_j = max(j - 1, 0)
      max_i = min(i + 1, N - 1)
      max_j = min(j + 1, M - 1)

      for ii in range(min_i, max_i + 1):
        for jj in range(min_j, max_j + 1):
          if mines_map[ii][jj] != MINE:
            mines_map[ii][jj] += 1


def check_flags(i, j):
  flag_cont = 0

  min_i = max(i - 1, 0)
  min_j = max(j - 1, 0)
  max_i = min(i + 1, N - 1)
  max_j = min(j + 1, M - 1)

  for ii in range(min_i, max_i + 1):
    for jj in range(min_j, max_j + 1):
      if visual_map[ii][jj] == FLAG:
        flag_cont += 1

  return flag_cont == mines_map[i][j]


def expand_number(i, j):

  min_i = max(i - 1, 0)
  min_j = max(j - 1, 0)
  max_i = min(i + 1, N - 1)
  max_j = min(j + 1, M - 1)

  for ii in range(min_i, max_i + 1):
    for jj in range(min_j, max_j + 1):
      if mines_map[ii][jj] == MINE and visual_map[ii][jj] != FLAG:
        visual_map[ii][jj] = mines_map[ii][jj]
        return False

  for ii in range(min_i, max_i + 1):
    for jj in range(min_j, max_j + 1):
      if visual_map[ii][jj] == NOT_CLICKED:
        expand_cells(ii, jj)

  return True


def expand_cells(i, j):
  global explored_cells

  if visual_map[i][j] == NOT_CLICKED:
    visual_map[i][j] = mines_map[i][j]

    if visual_map[i][j] != MINE:
      explored_cells += 1

      if visual_map[i][j] == VOID_CELL:
        min_i = max(i - 1, 0)
        min_j = max(j - 1, 0)
        max_i = min(i + 1, N - 1)
        max_j = min(j + 1, M - 1)

        for ii in range(min_i, max_i + 1):
          for jj in range(min_j, max_j + 1):
            if mines_map[ii][jj] != MINE:
              expand_cells(ii, jj)


def print_map():
  for row in mines_map:
    for col in row:
      d = col
      if col in visual_elements:
        d = visual_elements[col]
      print(d, end=' ')
    print()


def wins():
  return explored_cells == (N*M - N_MINES)


def add_zeros(string, num):
  string = str(string)
  if len(string) > num:
    return string[-num:]
  return '0'*(num-len(string)) + string


def draw_cells():
  window.fill(BG_COLOR)

  for i, row in enumerate(visual_map):
    for j, value in enumerate(row):
      window.blit(cell_sprites[value], coord_to_real(i, j))

  flags_cont = digit_font.render(add_zeros(N_MINES - n_flags, 3), True, RED, BLACK)
  clock_font = digit_font.render(add_zeros(minute, 2) +':'+ add_zeros(sec, 2), True, RED, BLACK)
  window.blit(flags_cont, flags_cont_rect)
  window.blit(clock_font, clock_font_rec)


if __name__ == "__main__":
  filepath = os.path.dirname(__file__) + '/'
  
  pg.init()
  pg.display.set_caption('Buscaminas')
  icon = pg.image.load(filepath+'img/icon.png')
  pg.display.set_icon(icon)

  clock = pg.time.Clock()
  window = pg.display.set_mode(MENU_SIZE, vsync=1)

  option_font = pg.font.Font(filepath+'font/opensans_bold.ttf', 45)
  easy_opt = option_font.render('EASY', True, BLACK)
  medium_opt = option_font.render('MEDIUM', True, BLACK)
  hard_opt = option_font.render('HARD', True, BLACK)

  easy_rect = easy_opt.get_rect()
  easy_rect.center = (MENU_WIDTH / 2, MENU_PADDING)

  medium_rect = medium_opt.get_rect()
  medium_rect.center = (MENU_WIDTH / 2, MENU_HEIGHT / 5 + MENU_PADDING)

  hard_rect = hard_opt.get_rect()
  hard_rect.center = (MENU_WIDTH / 2, MENU_HEIGHT / 5 * 2 + MENU_PADDING)

  start = True
  clock_start = True
  choosing_option = True
  while choosing_option:

    mouseX, mouseY = pg.mouse.get_pos()

    for event in pg.event.get():
      if event.type == pg.QUIT:
        start = False
        choosing_option = False
      if event.type == pg.KEYDOWN:
        if event.key == pg.K_ESCAPE:
          start = False
          choosing_option = False
      elif event.type == pg.MOUSEBUTTONUP:
        if event.button == LEFT_CLICK:
          if easy_rect.collidepoint((mouseX, mouseY)):
            N = 8
            M = 8
            N_MINES = 10
            BOARD_WIDTH = 480
            BOARD_HEIGHT = 480
            update_const()
            choosing_option = False
          elif medium_rect.collidepoint((mouseX, mouseY)):
            N = 16
            M = 16
            N_MINES = 45
            BOARD_WIDTH = 640
            BOARD_HEIGHT = 640
            update_const()
            choosing_option = False
          elif hard_rect.collidepoint((mouseX, mouseY)):
            N = 16
            M = 32
            N_MINES = 99
            BOARD_WIDTH = 1280
            BOARD_HEIGHT = 640
            update_const()
            choosing_option = False

    window.fill(BG_COLOR)
    window.blit(easy_opt, easy_rect)
    window.blit(medium_opt, medium_rect)
    window.blit(hard_opt, hard_rect)
    pg.display.flip()
    clock.tick(60)

  window = pg.display.set_mode(SCREEN_SIZE, vsync=1)

  cell_sprites = {
    9: get_image(filepath+'img/mine.png'),
    8: get_image(filepath+'img/8.png'),
    7: get_image(filepath+'img/7.png'),
    6: get_image(filepath+'img/6.png'),
    5: get_image(filepath+'img/5.png'),
    4: get_image(filepath+'img/4.png'),
    3: get_image(filepath+'img/3.png'),
    2: get_image(filepath+'img/2.png'),
    1: get_image(filepath+'img/1.png'),
    0: get_image(filepath+'img/inverted_cell.png'),
    -1: get_image(filepath+'img/cell.png'),
    -2: get_image(filepath+'img/flag.png')
  }

  digit_font = pg.font.Font(filepath+'font/digital.ttf', PADDING)
  font = pg.font.Font(filepath+'font/opensans_bold.ttf', 32)
  
  clock_thread = Thread(target=stopwatch)
  clock_thread.start()

  while start:
    start = False

    mines_map  = [[ 0 for _ in range(M)] for _ in range(N)]
    visual_map = [[-1 for _ in range(M)] for _ in range(N)]
    explored_cells = 0

    n_flags = 0
    mines_list = set()
    flags_list = set()

    flags_cont = digit_font.render(add_zeros(N_MINES - n_flags, 3), True, RED, BLACK)
    flags_cont_rect = flags_cont.get_rect()
    flags_cont_rect.centery = PADDING / 2
    flags_cont_rect.left = 10
    
    clock_font = digit_font.render('00:00', True, RED, BLACK)
    clock_font_rec = clock_font.get_rect()
    clock_font_rec.centery = PADDING / 2
    clock_font_rec.right = SCREEN_WIDTH - 10
    
    minute, sec = 0, 0
    seconds = 0
    sumador = 0

    started = False
    lost = False
    won = False
    end = False
    while not end:

      mouseX, mouseY = pg.mouse.get_pos()

      for event in pg.event.get():
        if event.type == pg.QUIT:
          end = True
        elif event.type == pg.KEYDOWN:
          if event.key == pg.K_ESCAPE:
            end = True
          elif event.key == pg.K_r:
            end = True
            start = True
        elif event.type == pg.MOUSEBUTTONDOWN:

          if mouseY < PADDING:
            break

          i, j = real_to_coord(mouseX, mouseY)

          if event.button == LEFT_CLICK:
            if visual_map[i][j] != FLAG:
              if not started:
                started = True
                gen_mines(i, j)
                sumador = 1
                  
                # print_mines_map()

              if visual_map[i][j] not in (NOT_CLICKED, FLAG):
                if check_flags(i, j):
                  if not expand_number(i, j):
                    lost = True
                    end = True
              else:
                expand_cells(i, j)

              if wins():
                won = True
                end = True

              if visual_map[i][j] == MINE:
                lost = True
                end = True

          elif event.button == RIGHT_CLICK:
            cell_value = visual_map[i][j]
            if cell_value == NOT_CLICKED or cell_value == FLAG:
              if cell_value != FLAG:
                visual_map[i][j] = FLAG
                flags_list.add((i, j))
                n_flags += 1

              else:
                visual_map[i][j] = NOT_CLICKED
                flags_list.remove((i, j))
                n_flags -= 1
                
      if seconds > 0:
        sec = seconds % 60
        minute = seconds // 60

      draw_cells()

      pg.display.flip()
      clock.tick(60)

    if lost:
      msg = font.render('Has perdido :(', True, RED, BLACK)

    if won:
      msg = font.render('Has ganado! :)', True, GREEN, BLACK)

    if won or lost:
      waiting_input = True
      while waiting_input:
        for event in pg.event.get():
          if event.type == pg.QUIT:
            waiting_input = False
          if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
              waiting_input = False
            elif event.key == pg.K_r:
              start = True
              waiting_input = False

        draw_cells()

        if lost:
          for mine_i, mine_j in (mines_list - flags_list):
            window.blit(cell_sprites[mines_map[mine_i][mine_j]], coord_to_real(mine_i, mine_j))

        txtRect = msg.get_rect()
        txtRect.center = (SCREEN_WIDTH/2, BOARD_HEIGHT/2+PADDING)
        window.blit(msg, txtRect)

        pg.display.flip()
        clock.tick(60)

  clock_start = False
  pg.quit()
  sys.exit()
