# Franklin Hu
import heapq
import sys

GRID_MAX = [
  1, # X MIN
  6, # X MAX
  1, # Y MIN
  6, # Y MAX
]

X_MIN = 0
X_MAX = 1
Y_MIN = 2
Y_MAX = 3

class CarState:
  def __init__(self, name, length, x, y, orientation):
    self.name = name
    self.length = int(length)
    self.x = int(x)
    self.y = int(y)
    self.orientation = orientation.lower()

  def get_child_states(self):
    child_states = []

    x_min, x_max, y_min, y_max = GRID_MAX

    if self.orientation == "up":
      if self.y - self.length > y_min - 1:
        child_states.append(self.get_clone(self.x, self.y-1))
      if self.y < y_max:
        child_states.append(self.get_clone(self.x, self.y+1))
    elif self.orientation == "down":
      if self.y > y_min:
        child_states.append(self.get_clone(self.x, self.y-1))
      if self.y + self.length < y_max + 1:
        child_states.append(self.get_clone(self.x, self.y+1))
    elif self.orientation == "left":
      if self.x < x_max:
        child_states.append(self.get_clone(self.x+1, self.y))
      if self.x - self.length > x_min - 1:
        child_states.append(self.get_clone(self.x-1, self.y))
    elif self.orientation == "right":
      if self.x > x_min:
        child_states.append(self.get_clone(self.x-1, self.y))
      if self.x + self.length < x_max + 1:
        child_states.append(self.get_clone(self.x+1, self.y))
    else:
      raise RuntimeException("Invalid orientation")
    return child_states

  def get_clone(self, x, y):
    state = CarState(self.name, self.length, x, y, self.orientation)
    if x > self.x:
      state.move = "right"
    elif x < self.x:
      state.move = "left"
    elif y > self.y:
      state.move = "down"
    elif y < self.y:
      state.move = "up"
    else:
      raise RuntimeExeception("Invalid Clone for Move")
    return state

  def get_coordinates(self):
    if self.orientation == "up":
      return [(self.x, y) for y in xrange(self.y, self.y-self.length, -1)]
    elif self.orientation == "down":
      return [(self.x, y) for y in xrange(self.y, self.y+self.length, 1)]
    elif self.orientation == "left":
      return [(x, self.y) for x in xrange(self.x, self.x-self.length, -1)]
    elif self.orientation == "right":
      return [(x, self.y) for x in xrange(self.x, self.x+self.length, 1)]

  def __str__(self):
    return "%s:(%s,%s)" % (self.name, self.x, self.y)

  def id(self):
    return hash(self.__str__())

class SearchState:
  def __init__(self):
    self.states = {}
    self.moves = []

  def add(self, car_state):
    self.states[car_state.name] = car_state

  def is_valid(self):
    grid = {}
    for car_state in self.states.values():
      coords = car_state.get_coordinates()
      for coord in coords:
        if coord in grid:
          return False
        else:
          grid[coord] = 1
    return True

  def get_clone(self, car_state):
    clone = SearchState()
    clone.states = dict(self.states)
    clone.states[car_state.name] = car_state
    clone.moves = list(self.moves)
    clone.moves.append((car_state.name, 1, car_state.move))
    return clone

  def get_moves(self):
    return self.moves

  def get_child_states(self):
    child_states = []
    for car_state in self.states.values():
      for car_child_state in car_state.get_child_states():
        clone = self.get_clone(car_child_state)
        if clone.is_valid():
          child_states.append(clone)
    return child_states

  def is_goal_state(self):
    s_state = self.states['S']
    for coord in s_state.get_coordinates():
      x,y = coord
      if x <= 6 - s_state.length:
        return False
    return True

  def __str__(self):
    states = self.states.values()
    output = []
    for state in states:
      output.append("%s:(%d,%d)" % (state.name, state.x, state.y))
    output.sort()
    return ";".join(output)

def in_grid(x, y):
  return x > 0 and x < 7 and y > 0 and y < 7

def heuristic(state):
  score = 0
  s_state = state.states['S']
  rightmost_x = 0
  for coord in s_state.get_coordinates():
    x,y = coord
    if in_grid(x, y):
      score += 1
    if x > rightmost_x:
      rightmost_x = x

  for car_state in state.states.values():
    if not car_state.name == 'S':
      for coord in car_state.get_coordinates():
        x,y = coord
        if (y == 3) and (x > rightmost_x):
          score += 10

  leftmost_x = rightmost_x - s_state.length + 1
  score += (6 - leftmost_x) * 10
  return score

def aStar(root_state):
  visited_states = set([])
  queue = []
  heapq.heappush(queue, (0, root_state))

  g = {}
  h = {}
  f = {}

  g[root_state] = 0
  h[root_state] = heuristic(root_state)
  f[root_state] = g[root_state] + h[root_state]

  while len(queue) != 0:
    score,x = heapq.heappop(queue)
    if x.is_goal_state():
      return x.get_moves()

    visited_states.add(x)
    for child in x.get_child_states():
      if child in visited_states:
        continue

      score = g[x] + 1
      update = False
      push = False
      if child not in queue:
        push = True
        update = True
      elif score < g[child]:
        update = True
      
      if update:
        g[child] = score
        h[child] = heuristic(child)
        f[child] = g[child] + h[child]

      if push:
        heapq.heappush(queue, (f[child], child))

def aggregate_moves(moves):
  buf = list(moves[0])
  output = []
  for move in moves[1:]:
    if (buf[0] == move[0]) and (buf[2] == move[2]):
      buf[1] += move[1]
    else:
      output.append(buf)
      buf = list(move)
  output.append(buf)
  return output

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print "Usage: python challenge.py <input-file> <output-file>"
    sys.exit(1)
  inputfile = sys.argv[1]
  outputfile = sys.argv[2]
  handle = open(inputfile, 'r')
  car_states = SearchState()
  for row in handle:
    row = row.rstrip("\n").split(" ")
    name, length, start_x_y, orientation = row
    start_x_y = start_x_y.split(",")
    x, y = int(start_x_y[0]), int(start_x_y[1])
    car_states.add(CarState(name, length, x, y, orientation))
  handle.close()

  optimal_moves = aStar(car_states)
  optimal_moves = aggregate_moves(optimal_moves)
  handle = open(outputfile, 'w')
  for i in xrange(len(optimal_moves)):
    move = optimal_moves[i]
    handle.write("%d %s %d %s\n" % (i+1, move[0], move[1], move[2]))
  handle.close()
  print "Successfully wrote output to: %s" % outputfile
