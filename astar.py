import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("Pathfinding Visualizer")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)

#keep track of state with color
#white -> not yet used
#red -> alr used
#black -> barrier
#orange -> start node
#turquoise -> end node 


class Node:
	#NOTE TO SELF: The self parameter doesn’t have to be named “self,” as you can call it by any other name. However, the self parameter must always be the first parameter of any class function, regardless of the name chosen.
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE


	#Method we call to draw each square
	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))


	# Check adjacent squares, see if barriers or not, if not add them into neighbours list
	def update_neighbors(self, grid):
		self.neighbors = []

		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])
		
		#REVISITED SECTION
		if (self.col > 0 and self.row >0)  and not grid[self.row-1][self.col - 1].is_barrier(): # upper left
			self.neighbors.append(grid[self.row-1][self.col - 1])	
		if (self.row < self.total_rows-1 and self.col >0)  and not grid[self.row+1][self.col - 1].is_barrier(): # upper right
				self.neighbors.append(grid[self.row+1][self.col - 1])	
		if (self.col < self.total_rows-1 and self.row >0)  and not grid[self.row-1][self.col + 1].is_barrier(): # lower left
				self.neighbors.append(grid[self.row-1][self.col + 1])
		if (self.col < self.total_rows-1 and self.row <self.total_rows-1)  and not grid[self.row+1][self.col + 1].is_barrier(): # lower right
				self.neighbors.append(grid[self.row+1][self.col + 1])	

#How we handle when we compare two spots together
	def __lt__(self, other):
		return False

 
#heuristic function 
#using taxicab distance (use distance measured with component lengths)
def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x2 - x1) + abs(y2 - y1)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False

#Generates 2D Lists to form grid
def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Node(i, j, gap, rows)
			grid[i].append(spot)

	return grid

#draw the grid to the screen
def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


#BEEG draw function
def draw(win, grid, rows, width):
	win.fill(WHITE)

	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()

#decide what cube to pick depending on mouse position
def get_clicked_pos(pos, rows, square_width):
	gap = square_width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def main(win, width):
	ROWS = 40
	grid = make_grid(ROWS, width)

	start = None
	end = None

	run = True
	#CENTRAL GAME LOOP
	while run:
		draw(win, grid, ROWS, width)

		#loop through all events and check what they are *** needs review?
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False

			if pygame.mouse.get_pressed()[0]: # LEFT MOUSE BUTTON
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, width)
				spot = grid[row][col]

				#Make the first square the start square
				if not start and spot != end:
					start = spot
					start.make_start()

				#Make the second square the end square
				elif not end and spot != start:
					end = spot
					end.make_end()

				#Make all following squares barriers
				elif spot != end and spot != start:
					spot.make_barrier()

			# elif pygame.mouse.get_pressed()[2]: # RIGHT MOUSE BUTTON
			# 	pos = pygame.mouse.get_pos()
			# 	row, col = get_clicked_pos(pos, ROWS, width)
			# 	spot = grid[row][col]
			# 	spot.reset()
			# 	if spot == start:
			# 		start = None
			# 	elif spot == end:
			# 		end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)
					
					#anonymous function lambda *** WHAT
					algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, width)

	pygame.quit()

main(WIN, WIDTH)