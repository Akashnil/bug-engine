positions = []
coords_pos = {}

SZ = 2

for i in range(-SZ, SZ+1):
	for j in range(-SZ, SZ+1):
		k = -i-j
		if k >= -SZ and k <= SZ:
			positions.append((i, j, k))
			coords_pos[(i, j, k)] = len(positions)-1

N = len(positions)
neighbors = [[] for i in positions]

for i in range(-SZ, SZ+1):
	for j in range(-SZ, SZ+1):
		k = -i-j
		if k >= -SZ and k <= SZ:
			first = coords_pos[(i, j, k)]
			for (u, v) in [(0,1), (1,0), (0,-1), (-1,0), (1,-1), (-1,1)]:
				neb = (i+u, j+v, k-u-v)
				if neb in coords_pos:
					second = coords_pos[neb]
					neighbors[first].append(second)

# board is a tuple: player#, tiles: 0 (empty), 1 (p1), 2 (p2), -1 (growing)
tiles = {-1: '[+]', 0: ' : ', 1: '[O]', 2: '[X]'}

def get_disp_coords(p):
	i, j, k = positions[p]
	u = (i + SZ) * 2 + 1
	v = j - k + 2 * SZ
	return u, v

def str_board(position, values = [], my_value = None, my_position = None):
	player, board = position
	# a sequence of tiles
	grid = [['   ' for i in range(SZ*4+4)] for j in range(SZ*4+1)]
	for p in range(N):
		u, v = get_disp_coords(p)
		grid[v][u] = tiles[board[p]]
	for x, p in values:
		u, v = get_disp_coords(p)
		grid[v][u] = ('+' if x >= 0 else '-') + str(abs(x)).rjust(2)
	if my_position is not None:
		u, v = get_disp_coords(my_position)
		assert (grid[v][u - 1] == '   ')
		assert (grid[v][u + 1] == '   ')
		grid[v][u - 1] = '  ('
		grid[v][u + 1] = ')  '

	header = 'Current Player: ' + tiles[player] + (' Position Value: ' + str(my_value) if my_value is not None else '')
	
	return '\n'.join([header] + [''.join(x) for x in grid])

def subtract(x, y):
	return (x[0]-y[0], x[1]-y[1], x[2]-y[2])

def rotate(x, r):
	sign = int(r/6)
	perm = r%6
	dict = {
		0:(x[0],x[1],x[2]),
		1:(x[1],x[2],x[0]),
		2:(x[2],x[0],x[1]),
		3:(x[0],x[2],x[1]),
		4:(x[2],x[1],x[0]),
		5:(x[1],x[0],x[2])
		}
	ret = dict[perm]
	if sign == 0:
		return ret
	else:
		return (-ret[0], -ret[1], -ret[2])

def get_position_order(r):
	return [coords_pos[rotate(positions[p], r)] for p in range(N)]

reorders = [get_position_order(r) for r in range(12)]

def get_shape(board, idx, shapes_board = None):
	tile = board[idx]
	que = [idx]
	i = 0
	poss = []
	while len(que) > i:
		pos = que[i]
		if board[pos] != tile or pos in poss:
			i += 1
			continue
		poss.append(pos)
		for jdx in neighbors[pos]:
			que.append(jdx)
		i += 1
	size = len(poss)
	assert (size > 0)
	rotated_coords = []
	if size == 1:
		shape = [size, [(0,0,0)]]
	elif size == 2:
		shape = [size, [(0,0,0), (1,-1,0)]]
	else:
		for rot in range(6 if size == 3 else 12):
			rcoords = [rotate(positions[x], rot) for x in poss]
			min_coord = min(rcoords)
			rotated_coords.append(sorted([subtract(x, min_coord) for x in rcoords]))
		shape = [size, min(rotated_coords)]
	if shapes_board is not None:
		for p in poss:
			shapes_board[p] = [idx, shape]
	return shape

def children(position):
	player, board = position
	ret = []
	bonus_grow = (-1 in board)
	shapes_board = [None]*N
	max_size = 0
	for p in range(N):
		if board[p] != 0 and shapes_board[p] == None:
			size, shape = get_shape(board, p, shapes_board)
			if max_size < size:
				max_size = size
	for p in range(N):
		if board[p] != 0:
			continue
		if bonus_grow and -1 not in [board[q] for q in neighbors[p]]:
			continue
		my_neighbors = [q for q in neighbors[p] if board[q] == -1 or board[q] == player]
		joins_shapes = False
		if len(my_neighbors) > 0:
			for idx in my_neighbors[1:]:
				if shapes_board[idx] != shapes_board[my_neighbors[0]]:
					joins_shapes = True
		if joins_shapes:
			continue
		if not bonus_grow and len(my_neighbors) > 0 and shapes_board[my_neighbors[0]][1][0] >= max_size:
			continue
		board_ = board[:]
		shapes_board_ = shapes_board[:]
		if bonus_grow:
			assert (len(my_neighbors) > 0)
			for q in range(N):
				if shapes_board[q] == shapes_board[my_neighbors[0]]:
					board_[q] = player
		board_[p] = player
		get_shape(board_, p, shapes_board_)
		if -1 in board_:
			ret.append((p, (player, board_)))
			continue
		eating_dict = {} # dict from blob to list of blobs
		for q in range(N):
			if board_[q] != player and board_[q] != -1:
				continue
			for r in neighbors[q]:
				if board_[r] != 3-player:
					continue
				if shapes_board_[q][1] != shapes_board_[r][1]:
					continue
				if shapes_board_[q][0] not in eating_dict:
					eating_dict[shapes_board_[q][0]] = set()
				eating_dict[shapes_board_[q][0]].add(shapes_board_[r][0])
		legit_eaters = set()
		legit_eaten = set()
		for eater in eating_dict:
			board__ = board_[:]
			shapes_board__ = shapes_board_[:]
			for q in range(N):
				if board__[q] == 3-player and shapes_board__[q][0] in eating_dict[eater]:
					board__[q] = 0
					shapes_board__[q] = None
			can_grow = False
			for q in range(N):
				if board__[q] != 0:
					continue
				my_neighbors = set([shapes_board__[r][0] for r in neighbors[q] if board__[r] == player])
				if len(my_neighbors) == 1 and eater in my_neighbors:
					can_grow = True
					break
			if can_grow:
				legit_eaters.add(eater)
				for eaten in eating_dict[eater]:
					legit_eaten.add(eaten)
		for q in range(N):
			if board_[q] != 0 and shapes_board_[q][0] in legit_eaters:
				assert(board_[q] == player)
				board_[q] = -1
			if board_[q] != 0 and shapes_board_[q][0] in legit_eaten:
				assert(board_[q] == 3-player)
				board_[q] = 0
				# shapes_board_[q] = None
		ret.append((p, (player if -1 in board_ else 3-player, board_)))
	return ret

import random

value_dict = {}

import pickle

def read_dict(path = 'bug_83_.pickle'):
	global value_dict
	with open(path, 'rb') as handle:
		value_dict = pickle.load(handle)

from os import path
if path.exists("bug_51148504_.pickle"):
	read_dict("bug_51148504_.pickle")

def write_dict():
	global value_dict
	with open('bug_' + str(len(value_dict)) + '_.pickle', 'wb') as handle:
		pickle.dump(value_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

def canonical_position(position):
	player, board = position
	if player == 2:
		board = [3-x if x > 0 else x for x in board]
	return tuple(min([[board[reorders[r][idx]] for idx in range(N)] for r in range(12)]))

def less_than(val1, val2):
	if val1 == val2:
		return False
	if val1 <= 0 and val2 >= 0:
		return True
	if val1 >= 0 and val2 <= 0:
		return False
	return val1 > val2

def get_best_val(values, player):
	if len(values) == 0:
		return 1 if player == 1 else -1
	ret = values[0][0]
	for x in values[1:]:
		if (player == 1) != less_than(x[0], ret):
			ret = x[0]
	return ret

p63 = 2**63-25
def tuple_hash(board, base = 4, bias = 1):
	ret = 0
	for x in board:
		ret *= base
		ret += x + bias
	return ret

def evaluate_position(position):
	player, _ = position
	canon = canonical_position(position)
	hash_canon = tuple_hash(canon)
	if hash_canon in value_dict:
		canon_val = value_dict[hash_canon]
		return canon_val if player == 1 else -canon_val
	child_vals = []
	for p, pos in children(position):
		val = evaluate_position(pos)
		if pos[0] != player:
			val += 1 if val > 0 else -1
		child_vals.append((val, p))
	best_val = get_best_val(child_vals, player)
	value_dict[hash_canon] = best_val if player == 1 else -best_val
	if len(value_dict) % 10000 == 0:
		print (str_board(position, child_vals))
		print (len(value_dict))
	if len(value_dict) % 10000000 == 0:
		write_dict()
	return best_val

def simulate(position, p1_god = True, p2_god = True):
	player, board = position
	childs = children(position)
	child_vals = []
	for p, pos in childs:
		child_vals.append((evaluate_position(pos), p))
	if not child_vals:
		print(str_board(position, child_vals, evaluate_position(position)))
		return
	is_god = p1_god if player == 1 else p2_god
	move = -1
	if not is_god:
		move = random.choice([x[1] for x in child_vals])
	else:
		best_val = get_best_val(child_vals, player)
		best_moves = [x[1] for x in child_vals if x[0] == best_val]
		move = random.choice(best_moves)
	assert (move >= 0)
	print(str_board(position, child_vals, evaluate_position(position), move))
	for p, pos in childs:
		if p == move:
			simulate(pos, p1_god, p2_god)
			return

print(evaluate_position((1, [0]*N)))


# write_dict()


simulate((1, [0]*N), True, True)
print ('----')

simulate((1, [0]*N), True, False)
print ('----')

simulate((1, [0]*N), False, True)
print ('----')
