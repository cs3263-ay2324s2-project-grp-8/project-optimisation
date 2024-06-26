from utils import Graph, Node
import numpy as np
from copy import deepcopy
import math
from mamcts_agent_fixed_hire import MultiAgentController
from node import AgentNode
import sys
import time
import argparse
from itertools import product

INITIAL_BUDGET = 10000

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
VISITED = 8

REWARD = 9
BUDGET_USED = 10
BUDGET_LEFT = 11

# SITE Accessors
IS_SIGHTED = 3
ACCESSED = 4

def print_state(state):
    for i, worker in enumerate(state):
        if (i < 9):
            print(f"Worker {i + 1}'s state : {worker}")
        elif (i == 9):
            print(f"Rewards Extracted So Far : {state[9]}")
        elif (i == 10):
            print(f"Budget Used : {state[10]}")
        elif (i == 11):
            print(f"Budget Left : {state[11]}")
        else:
            print(f"Reward Site : {state[i]}")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--graph_idx', type=int, default=0, help='Graph index')
    
    args = parser.parse_args()

    log = True
    graph_idx = args.graph_idx
    log_file = None
    log_filename = f'test_{graph_idx}.log.txt'
    
    filename : str = f"../graphs/graph{graph_idx}.json"
    graph = Graph(filename)
    timestamp : int = 0
    origin = graph.get_Origin()
    
    if log:
        log_file = open(log_filename, "w")
        sys.stdout = log_file
    
    o = []
    a = [0, 1, 2, 3]
    b = [0, 1, 2]
    c = [0, 1, 2, 3, 4]
    tgt = list(product(a, b, c))
    
    for conf in tgt:
        d = []
        d.extend([1] * conf[0])
        d.extend([0] * (3 - conf[0]))
        d.extend([1] * conf[1])
        d.extend([0] * (2 - conf[1]))
        d.extend([1] * conf[2])
        d.extend([0] * (4 - conf[2]))
        o.append(deepcopy(d))

    for setup_idx, s in enumerate(o):
        st = time.time()
        state = list()

        for i in range(1, 10):
            type_worker = 1 if 1 <= i <= 3 else 2 if i in [4, 5] else 3
            state.append([origin.get_x_coordinate(), origin.get_y_coordinate(), type_worker, False, False, False, 0, 1, [origin.get_coordinate()]])

        state.extend([0, 0, INITIAL_BUDGET])
            
        """
        Retrieves the sites of type 1, 2, 3 and appends them to the state
        """
        def append_sites_of_type(site_type):
            for site in graph.retrieve_all_sites_of_type(site_type + 1):
                state.append([site.get_x_coordinate(), site.get_y_coordinate(), site_type, False, False])

        for site_type in range(1, 4):
            append_sites_of_type(site_type)
        '''
        Initialise fixed workers to be hired
        '''
        for i in range(9):
            state[i][IS_HIRED] = s[i]
        
        """
        Initialization for MCTS
        """
        controller : MultiAgentController = MultiAgentController(graph=graph)
        root : AgentNode = AgentNode(parent=None, state=state, idx=-1)

        for i in range(9 * 20):
            next_node: AgentNode = controller.search(root)
            if next_node is None:
                # print(f"Final State : {root.state}")
                break
            # print(f"NEXT STATE : {next_node.state}")
            root = next_node

        et = time.time()
        print(f'Workers Config {setup_idx+1}: {s}, Time: {et-st:.2f} seconds, Profit: {root.state[9] - root.state[10]:.0f}')
        # print(f"Final State: {root.state}")
        # print(f"Root type : {root.idx}")
        sys.stdout.flush()
    if log:
        log_file.close()
        sys.stdout = sys.__stdout__

    # from time import time
    # overall_start = time()

    # for timestamp in range(20):
        
    #     start = time()
        
    #     print('\n===============================')
    #     print(f"Timestamp {timestamp+1}") if LOG_BASIC else None
    #     montecarlo.simulate(50)
    #     print(f"Simulation done for TS {timestamp+1}") if LOG_BASIC else None
    #     new_tree_node : TreeNode = montecarlo.make_choice()
    #     montecarlo.root_node = new_tree_node

    #     print(f"Time taken for TS {timestamp+1} : {time() - start}") if LOG_TIME_TAKEN else None
    
    # print(f"Overall Time taken : {time() - overall_start}") if LOG_TIME_TAKEN else None
    # print("Finished Running MCTS") if LOG_BASIC else None
    # print_state(montecarlo.root_node.state) if LOG_BASIC else None
