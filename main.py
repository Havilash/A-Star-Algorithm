# LEFT CLICK = set tile
# RIGHT CLICK = delete tile
# SPACE = start algorithm
# C = clear

import pygame
from queue import PriorityQueue

FPS = float(60)

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

# types
NORMAL_TYPE = 0b000
BARRIER_TYPE = 0b001
START_TYPE = 0b010
END_TYPE = 0b011
OPEN_TYPE = 0b100
CLOSE_TYPE = 0b101
PATH_TYPE = 0b110

pygame.init()

SIZE = 800, 800
GRID_SIZE = 50, 50
GRID_SPACING = SIZE[0] // GRID_SIZE[0], SIZE[1] // GRID_SIZE[1]
WIN = pygame.display.set_mode(SIZE)
TITLE = "A* Algorithm"

pygame.display.set_caption(TITLE + " (Drawmode)")


class Tile:
    size = GRID_SPACING

    def __init__(self, grid_pos):
        self.grid_pos = grid_pos
        self.pos = grid_pos[0] * self.size[0], grid_pos[1] * self.size[1]
        self._type = 0b000
        self.color = WHITE

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, t):
        self._type = t

        if self.type == NORMAL_TYPE:
            self.color = WHITE
        elif self.type == BARRIER_TYPE:
            self.color = BLACK
        elif self.type == START_TYPE:
            self.color = BLUE
        elif self.type == END_TYPE:
            self.color = PURPLE
        elif self.type == OPEN_TYPE:
            self.color = GREEN
        elif self.type == CLOSE_TYPE:
            self.color = RED
        elif self.type == PATH_TYPE:
            self.color = TURQUOISE

    def draw(self, win: pygame.Surface):
        pygame.draw.rect(win, self.color, (*self.pos, *self.size))

    def __lt__(self, other):
        return False


def get_neighbors(tile, grid):
    x, y = tile.grid_pos
    neighbors = [
        grid[i][j]
        for i, j in [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
        if 0 <= i < GRID_SIZE[0]
        and 0 <= j < GRID_SIZE[1]
        and grid[i][j].type != BARRIER_TYPE
    ]
    return neighbors


# def get_neighbors(tile, grid):
#     x, y = tile.grid_pos
#     neighbors = [
#         grid[x + dx][y + dy]
#         for dx in (-1, 0, 1)
#         for dy in (-1, 0, 1)
#         if (dx != 0 or dy != 0)
#         and 0 <= x + dx < GRID_SIZE[0]
#         and 0 <= y + dy < GRID_SIZE[1]
#         and grid[x + dx][y + dy].type != BARRIER_TYPE
#     ]
#     return neighbors


def manhatten_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return abs(x1 - x2) + abs(y1 - y2)  # manhatten distance


def euclidean_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2

    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5  # euclidean distance


h = manhatten_distance


def reconstruct_path(came_from, current, start, end, draw):
    while current in came_from:
        current = came_from[current]
        if current not in [start, end]:
            current.type = PATH_TYPE
            draw()


def astar_algorithm(start, end, grid, draw):
    pygame.display.set_caption(TITLE)
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    open_set_hash = {start}

    came_from = {}

    g_score = {tile: float("inf") for row in grid for tile in row}
    g_score[start] = 0
    f_score = {tile: float("inf") for row in grid for tile in row}
    f_score[start] = 0 + h(start.grid_pos, end.grid_pos)

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        current = open_set.get()[2]
        if current == end:
            return reconstruct_path(came_from, current, start, end, draw)

        open_set_hash.remove(current)
        for neighbor in get_neighbors(current, grid):
            tentative_g_score = g_score[current] + 1
            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + h(
                    neighbor.grid_pos, end.grid_pos
                )
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    if neighbor not in [start, end]:
                        neighbor.type = OPEN_TYPE

        if current not in [start, end]:
            current.type = CLOSE_TYPE

        draw()

    return False


def get_clicked_pos(pos):
    return pos[0] // GRID_SPACING[0], pos[1] // GRID_SPACING[1]


def create_grid():
    grid = []
    for x in range(GRID_SIZE[0]):
        grid.append([])
        for y in range(GRID_SIZE[1]):
            grid[x].append(Tile((x, y)))
    return grid


def draw_grid_lines(win):
    for i in range(GRID_SIZE[0]):
        pygame.draw.line(
            win, GREY, (GRID_SPACING[0] * i, 0), (GRID_SPACING[0] * i, SIZE[1])
        )
    for i in range(GRID_SIZE[1]):
        pygame.draw.line(
            win, GREY, (0, GRID_SPACING[1] * i), (SIZE[0], GRID_SPACING[1] * i)
        )


def draw(win: pygame.Surface, grid):
    win.fill(WHITE)

    for row in grid:
        for tile in row:
            tile.draw(win)
    draw_grid_lines(win)

    pygame.display.update()


def main():
    grid = create_grid()

    start = None
    end = None

    astar_started = False

    run = True
    clock = pygame.time.Clock()
    while run:
        time_passed = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
                    break

            if astar_started:
                continue

            if pygame.mouse.get_pressed()[0]:  # left click
                mpos = pygame.mouse.get_pos()
                x, y = get_clicked_pos(mpos)
                tile = grid[x][y]
                if start is None and tile is not end:
                    start = tile
                    start.type = START_TYPE
                elif end is None and tile is not start:
                    end = tile
                    end.type = END_TYPE
                elif (
                    start is not None
                    and end is not None
                    and tile is not start
                    and tile is not end
                ):
                    tile.type = BARRIER_TYPE

            if pygame.mouse.get_pressed()[2]:  # right click
                mpos = pygame.mouse.get_pos()
                x, y = get_clicked_pos(mpos)
                tile = grid[x][y]
                tile.type = NORMAL_TYPE
                if tile == start:
                    start = None
                if tile == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not astar_started and start and end:
                    for row in grid:
                        for tile in row:
                            if tile.type in [PATH_TYPE, OPEN_TYPE, CLOSE_TYPE]:
                                tile.type = NORMAL_TYPE
                    astar_algorithm(start, end, grid, lambda: draw(WIN, grid))
                    pygame.display.set_caption(TITLE + " (Drawmode)")

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = create_grid()

        draw(WIN, grid)

    pygame.quit()


if __name__ == "__main__":
    main()
