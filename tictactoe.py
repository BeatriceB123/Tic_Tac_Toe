import numpy as np
import pygame, sys
from pygame.locals import *

WINDOWWIDTH = 1280  # size of window's width in pixels
WINDOWHEIGHT = 720  # size of windows' height in pixels
BOXSIZE = 200       # size of box height & width in pixels
MARGIN = 60         # size of gap between boxes in pixels
LINE_WIDTH = 7      # For odd width values, the thickness of each line grows with the original line being in the cent
DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

#                 #  R    G    B
BACKGROUND_COLOR = (153, 255, 153)
LINE_COLOR       = (  0,   0, 255)
HIGHLIGHTCOLOR   = ( 60,  60, 100)
player1_image = pygame.image.load("emoji1.png")
player2_image = pygame.image.load("emoji2.png")


class ProblemState:
    def __init__(self):
        self.square = np.zeros((3,3))
        self.moves_next = 1

    def __eq__(self, other):
        return self.moves_next == other.moves_next


def is_final_state(state):
    if who_completed_a_line(state) != 0:
        return True  # someone managed to make a complete line
    if 0 not in state.square:
        return True  # filled up
    return False


def who_completed_a_line(state):
    for j in range(2):
        if state.square[j][0] != 0 and state.square[j][0] == state.square[j][1] and state.square[j][0] == state.square[j][2]:
            return state.square[j][0], 1   # s-a completat o linie
        if state.square[0][j] != 0 and state.square[0][j] == state.square[1][j] and state.square[0][j] == state.square[2][j]:
            return state.square[0][j], 2   # s-a completat o coloana
    if state.square[0][0] != 0 and state.square[0][0] == state.square[1][1] and state.square[0][0] == state.square[2][2]:
        return state.square[0][0], 3       # diagonala principala
    if state.square[2][0] != 0 and state.square[2][0] == state.square[1][1] and state.square[2][0] == state.square[0][2]:
        return state.square[2][0], 4       # diagonala secundara
    return 0  # nu exista linii complete in tabela  <=> un fel de remiza


def is_valid_transition(state, pozi, pozj):
    if pozi and pozj not in [0, 1, 2]:
        return False
    if state.square[pozi][pozj] != 0:
        return False
    return True


def make_transition(state, pozi, pozj):
    state.square[pozi, pozj] = state.moves_next
    state.moves_next = - state.moves_next


def play_no_interface(s):
    while not is_final_state(s):
        print("It's " + str(s.moves_next) + " turn ")
        # choose i, j from posible transitions
        x = int(input())
        y = int(input())
        if is_valid_transition(s, x, y):
            make_transition(s, x, y)
            print(s)
        else:
            print("Reenter valid parameters")

    print("End of game: " + str(who_completed_a_line(s)) + " win ")


def display_board():
    pygame.init()
    pygame.display.set_caption('TIC-TAC-TOE')
    DISPLAYSURF.fill(BACKGROUND_COLOR)
    for line in range(0, 3 * BOXSIZE + 1, BOXSIZE):
        pygame.draw.line(DISPLAYSURF, LINE_COLOR, (MARGIN + line, MARGIN), (MARGIN + line, MARGIN + 3 * BOXSIZE), LINE_WIDTH)
        pygame.draw.line(DISPLAYSURF, LINE_COLOR, (MARGIN, MARGIN + line), (MARGIN + 3 * BOXSIZE, MARGIN + line), LINE_WIDTH)


def play(s):
    display_board()
    #  (Handles events. Updates the game state.  Draws the game state to the screen.)
    while True:
        while not is_final_state(s):  # main game loop
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == MOUSEBUTTONUP:
                    coordx, coordy = event.pos
                    coordx, coordy, i, j = process_the_event(coordx, coordy)
                    if process_the_event:
                        if is_valid_transition(s, i, j):
                            make_transition(s, i, j)
                            if s.moves_next == -1:
                                DISPLAYSURF.blit(player1_image, (coordx, coordy))
                            else:
                                DISPLAYSURF.blit(player2_image, (coordx, coordy))
                    else:
                        print("Invalid")
            pygame.display.update()
        if is_final_state(s):
            print("a castigat " + str(who_completed_a_line(s)))


def process_the_event(pozx, pozy):
    x = pozx
    y = pozy
    cari = 3
    carj = 3
    if x and y in range(MARGIN, MARGIN + 3 * BOXSIZE+1):  # in square
        for k in range(3, 0, -1):
            if pozx < MARGIN + k * BOXSIZE:
                x = MARGIN + (k-1) * BOXSIZE
                carj = k - 1 # daca e pe linia
            if pozy < MARGIN + k * BOXSIZE:
                y = MARGIN + (k-1) * BOXSIZE
                cari = k - 1
        return x + LINE_WIDTH, y + LINE_WIDTH, cari, carj
    return None


if __name__ == '__main__':
    s = ProblemState()
    want_to_play = True
    while want_to_play:
        play(s)
        want_to_play = False


