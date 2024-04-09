from copy import deepcopy
from utils import Graph, Node

MOVE_NORTH = 0
MOVE_SOUTH = 1
MOVE_EAST = 2
MOVE_WEST = 3
MOVE_NORTH_EAST = 4
MOVE_NORTH_WEST = 5
MOVE_SOUTH_EAST = 6
MOVE_SOUTH_WEST = 7
HIRE = 8
EXTRACT = 9
IDLE = 10
FIRE = 11

# Attribute Accessors:
X = 0
Y = 1
TYPE = 2
IS_HIRED = 3
IS_FIRED_BEFORE = 4
IS_EXTRACTING = 5
EXTRACT_TIME_LEFT = 6
TIMESTAMP = 7
REWARD_EXTRACTED = 8

# SITE Accessors
IS_SIGHTED = 3
ACCESSED = 4

def move_immutable(agent_state: list, graph : Graph,  move : int):
    new_state = deepcopy(agent_state)
    new_state[TIMESTAMP] += 1
    rewards_extracted, cost_incurred = 0, 0
    moves_dict = {
        MOVE_NORTH: (0, 1),
        MOVE_SOUTH: (0, -1),
        MOVE_EAST: (1, 0),
        MOVE_WEST: (-1, 0),
        MOVE_NORTH_EAST: (1, 1),
        MOVE_NORTH_WEST: (-1, 1),
        MOVE_SOUTH_EAST: (1, -1),
        MOVE_SOUTH_WEST: (-1, -1)
    }
    
    if move in moves_dict:
        dx, dy = moves_dict[move]
        new_state[X] += dx
        new_state[Y] += dy
    elif move == IDLE:
        pass
    elif move == HIRE:
        new_state[IS_HIRED] = True
    elif move == FIRE:
        new_state[IS_HIRED] = False
        new_state[IS_FIRED_BEFORE] = True
    elif move == EXTRACT:
        if (new_state[IS_EXTRACTING]):
            new_state[EXTRACT_TIME_LEFT] -= 1
            if (new_state[EXTRACT_TIME_LEFT] == 0):
                new_state[IS_EXTRACTING] = False
                node : Node = graph.get_Node(new_state[X], new_state[Y])
                rewards_extracted += node.get_reward()
        else:
            new_state[IS_EXTRACTING] = True
            node: Node = graph.get_Node(new_state[X], new_state[Y])
            new_state[EXTRACT_TIME_LEFT] = node.get_type() - 1
            
    """
    adds cost of extractin for each worker type
    """
    if move not in [FIRE, HIRE, IDLE]:
        cost_incurred += 500 if new_state[TYPE] == 3 else 100 * new_state[TYPE]

    return new_state, cost_incurred, rewards_extracted
    
'''
Immutable
Uses actions on each worker 
AND thus update the reward sites
Total cost of actions assumed to be within budget

returns new state
'''
def step_state(state, actions, graph: Graph):
    REWARD_START_IDX = 12
    REWARD_EXTRACTED_IDX = 9
    BUDGET_USED_IDX = 10
    BUDGET_LEFT_IDX = 11
    state_ = deepcopy(state)
    rwd_stites_under_extraction = list()
    # Move the Workers
    for i in range(0, 9):
        print(f'step_state {i} {actions}') if len(actions) != 9 else None
        state_[i], cost_incurred, reward_extracted = move_immutable(state_[i], graph, actions[i])
        state_[REWARD_EXTRACTED_IDX] += reward_extracted
        state_[BUDGET_USED_IDX] += cost_incurred
        state_[BUDGET_LEFT_IDX] -= cost_incurred
        if (state_[i][IS_EXTRACTING]):
            rwd_stites_under_extraction.append((state_[i][X], state_[i][Y]))
    # Update the Reward Sites
    for j in range(REWARD_START_IDX, REWARD_START_IDX + 9):
        if (state_[j][ACCESSED]):
            continue
        elif (not state_[j][ACCESSED] and (state_[j][X], state_[j][Y]) in rwd_stites_under_extraction):
            state_[j][ACCESSED] = True
        else:
            continue
    return state_

def check_move_ok(state: list, move_combi, graph: Graph) -> bool:
    REWARD_START_IDX = 12
    REWARD_EXTRACTED_IDX = 9
    BUDGET_USED_IDX = 10
    BUDGET_LEFT_IDX = 11
    state_ = deepcopy(state)
    
    for i in range(0, 9):
        print(f'check {i} {move_combi}') if len(move_combi) != 9 else None
        state_[i], cost_incurred, reward_extracted = move_immutable(state_[i], graph, move_combi[i])
        state_[REWARD_EXTRACTED_IDX] += reward_extracted
        state_[BUDGET_USED_IDX] += cost_incurred
        state_[BUDGET_LEFT_IDX] -= cost_incurred
        if (state_[BUDGET_LEFT_IDX] < 0):
            return False
        
    # check if > 1 worker is going to extract the site
    for i in range(REWARD_START_IDX, REWARD_START_IDX + 9):
        rws_state = state_[i]
        num_worker_extracting = 0
        x_, y_, type,  is_sighted, has_been_accessed = rws_state
        for j in range(0, 9):
            worker_ = state_[j]
            w_x, w_y = worker_[X], worker_[Y]
            if (w_x == x_ and w_y == y_ and worker_[IS_EXTRACTING]):
                num_worker_extracting += 1
            if (num_worker_extracting > 1):
                return False
    return True

def check_state_ok(state: list):
    REWARD_START_IDX = 12
    REWARD_EXTRACTED_IDX = 9
    BUDGET_USED_IDX = 10
    BUDGET_LEFT_IDX = 11
    if (state[BUDGET_LEFT_IDX] < 0):
        return False
    for  i in range(REWARD_START_IDX, REWARD_START_IDX + 9):
        rwd_site = state[i]
        count = 0
        for j in range(9):
            worker = state[j]
            if (worker[IS_EXTRACTING] and rwd_site[0] == worker[0] and rwd_site[1] == worker[1]):
                count += 1
            if (count > 1):
                return False
    return True