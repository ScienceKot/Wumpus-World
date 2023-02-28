# Importing all needed modules.
from copy import deepcopy
import random

# The main class implementing the agent logic.
class Agent:
    def __init__(self):
        # Building the initial representation of the cave.
        self.cave = [["" for i in range(4)] for j in range(4)]

        # Setting up the wumpus information.
        self.wumpus_alive = True
        self.wumpus_location = [None, None]

        # Setting up the agent initial location.
        self.agent_location = [0, 0]

        # Setting up the arrows and gold information.
        self.arrows = 1
        self.grabbed_gold = False

        # Setting up the move configuration.
        self.dif2move = {
            (1, 0) : "up",
            (0, -1) : "right",
            (-1, 0) : "down",
            (0, 1) : "left"
        }
        self.history = []

    def update_view(self, cell_info : dict) -> None:
        '''
            This function updates the information about the cave based on the information from cave.
        :param cell_info: dict
            The information of senses returned by cave, which is a dictionary with binary values of the following form.
                {
                    "breeze" - if the breeze is perceived in the cell.
                    "stench" - if the stench is perceived in the cell.
                    "glitter" - if the glitter is perceived in the cell.
                    "scream" - if the wumpus was killed.
                    "bump" - if the agent tryed to move in a wall.
                }
        :return: None
        '''
        # Creating a temporal copy of the cave.
        copy_cave = deepcopy(self.cave)
        # Adding the letter "b" in the agents location if the breeze is perceived.
        if cell_info["breeze"] and "b" not in copy_cave[self.agent_location[0]][self.agent_location[1]]:
            copy_cave[self.agent_location[0]][self.agent_location[1]] += "b"
        # Adding the letter "s" in the agents location if the stench is perceived.
        if cell_info["stench"] and "s" not in copy_cave[self.agent_location[0]][self.agent_location[1]]:
            copy_cave[self.agent_location[0]][self.agent_location[1]] += "s"
        # Adding the letter "g" in the agents location if the glitter is perceived.
        if cell_info["glitter"] and "g" not in copy_cave[self.agent_location[0]][self.agent_location[1]]:
            copy_cave[self.agent_location[0]][self.agent_location[1]] += "g"
        # Making an assumption about possible pits.
        if "?P" in copy_cave[self.agent_location[0]][self.agent_location[1]] and "p" not in copy_cave[self.agent_location[0]][self.agent_location[1]]:
            copy_cave[self.agent_location[0]][self.agent_location[1]] = copy_cave[self.agent_location[0]][self.agent_location[1]].replace("?P", "")
        # Making an assumption about possible wumpus location.
        if "?W" in copy_cave[self.agent_location[0]][self.agent_location[1]] and "w" not in copy_cave[self.agent_location[0]][self.agent_location[1]]:
            copy_cave[self.agent_location[0]][self.agent_location[1]] = copy_cave[self.agent_location[0]][self.agent_location[1]].replace("?W", "")
        # Placing "OK" if the agent location is safe.
        if "OK" not in copy_cave[self.agent_location[0]][self.agent_location[1]]:
            copy_cave[self.agent_location[0]][self.agent_location[1]] += "OK"
        # Updating the wumpus status if the "scream" is perceived.
        if cell_info["scream"]:
            self.wumpus_alive = False
            for i in range(len(copy_cave)):
                for j in range(len(copy_cave[i])):
                    if "w" in copy_cave[i][j]:
                        copy_cave[i][j] = copy_cave[i][j].replace("w", "OK")
        # Getting the neighbors coordinates.
        neighbors = self.get_neighbors(self.agent_location[0], self.agent_location[1])

        # Updating the neighbors information based on perceived information.
        for neighbor in neighbors:
            temp = copy_cave[neighbor[0]][neighbor[1]]
            pos_pit = cell_info["breeze"]
            pos_wumbus = cell_info["stench"]
            pos_gold = cell_info["glitter"]
            if pos_pit and "OK" not in copy_cave[neighbor[0]][neighbor[1]] and "p" not in copy_cave[neighbor[0]][neighbor[1]]:
                temp += "?P"
            if pos_wumbus and "OK" not in copy_cave[neighbor[0]][neighbor[1]] and self.wumpus_alive and "w" not in copy_cave[neighbor[0]][neighbor[1]] and not all(self.wumpus_location):
                temp += "?W"
            if pos_gold and "OK" not in copy_cave[neighbor[0]][neighbor[1]]:
                temp += "?G"
            copy_cave[neighbor[0]][neighbor[1]] = temp
        # Updating the agent's view of the cave.
        self.cave = self.additional_processing(copy_cave)

    def additional_processing(self, cave : list) -> list:
        '''
            The additional processing of the agent's view of cave.
        :param cave: list, 2d
            The agent's representation of the cave
        :return: list, 2d
            The new agent's representation of the cave.
        '''
        # Setting up the wumpus and pits.
        replace_possible_wumpus = False
        replace_possible_pits = False

        # Making a copy of the cave.
        cave_copy = deepcopy(cave)
        for i in range(len(cave_copy)):
            for j in range(len(cave_copy[i])):
                if cave_copy[i][j].count("?W") > 1:
                    # Replacing the "?W" to "W".
                    cave_copy[i][j] = cave_copy[i][j].replace("?W" * cave_copy[i][j].count("?W"), "w")
                    replace_possible_wumpus = True
                    self.wumpus_location = [i, j]
                if cave_copy[i][j].count("?P") > 1:
                    # Replacing the "?P" to "P".
                    cave_copy[i][j] = cave_copy[i][j].replace("?P" * cave_copy[i][j].count("?P"), "p")
                    replace_possible_pits = True
                if cave_copy[i][j].count("?G") > 1:
                    # Replacing the "?G" to "G".
                    cave_copy[i][j] = cave_copy[i][j].replace("?G" * cave_copy[i][j].count("?G"), "G")
                # Getting the coordinates of the neighbors.
                neighbors = self.get_neighbors(i, j)
                # Checking for possible locations of the Wumpus among neighbors.
                neighbors_pos_wumpus = [True for neighbor in neighbors if "s" in cave_copy[neighbor[0]][neighbor[1]]]
                if neighbors_pos_wumpus.count(True) >= 2 and "w" not in cave_copy[i][j]:
                    cave_copy[i][j] += "w"
                    self.wumpus_location = [i, j]

                # Checking for possible locations of the Gold among neighbors.
                neighbors_pos_gold = [True for neighbor in neighbors if "g" in cave_copy[neighbor[0]][neighbor[1]]]
                if neighbors_pos_gold.count(True) >= 2 and "G" not in cave_copy[i][j]:
                    cave_copy[i][j] += "G"

                # Checking for possible locations of the Pit among neighbors.
                neighbors_pos_pit = [True for neighbor in neighbors if "b" in cave_copy[neighbor[0]][neighbor[1]]]
                if neighbors_pos_pit.count(True) >= 2 and "p" not in cave_copy[i][j]:
                    cave_copy[i][j] += "p"
                # Grabbing the gold if the Agent is in the same location as the Gold.
                if self.grabbed_gold and "G" in cave_copy[i][j] and "?G" not in cave_copy[i][j]:
                    self.grabbed_gold = False
                    cave_copy[i][j] = cave_copy[i][j].replace("G", "")
        # Updating the wumpus information.
        pos_wumbus_count = 0
        pos_wumbus_places = []
        for i in range(len(cave_copy)):
            for j in range(len(cave_copy[i])):
                if "?W" in cave_copy[i][j]:
                    pos_wumbus_count += 1
                    pos_wumbus_places.append(tuple([i, j]))
        if pos_wumbus_count > 1:
            for pos in pos_wumbus_places:
                neighbors = self.get_neighbors(pos[0], pos[1])
                neighbors_having_stench = [True for neighbor in neighbors if "s" in cave_copy[neighbor[0]][neighbor[1]] and cave_copy[neighbor[0]][neighbor[1]] != ""]
                if neighbors_having_stench.count(True) < 2:
                    cave_copy[pos[0]][pos[1]] = cave_copy[pos[0]][pos[1]].replace("?W", "")
        # Eliminating the possible locations of "?W".
        if replace_possible_wumpus:
            for i in range(len(cave_copy)):
                for j in range(len(cave_copy[i])):
                    cave_copy[i][j] = cave_copy[i][j].replace("?W", "")
        # Eliminating the possible locations of "?P".
        if replace_possible_pits:
            for i in range(len(cave_copy)):
                for j in range(len(cave_copy[i])):
                    cave_copy[i][j] = cave_copy[i][j].replace("?P", "")
        return cave_copy

    def get_neighbors(self, y : int, x : int) -> list:
        '''
            This function returns the coordinates of the cell with the coordinates (x, y).
        :param y: int
            The row index of the cell.
        :param x: int
            The column index of the cell.
        :return: list
            The list of coordinates indexes.
        '''
        neighbors = [
            [y - 1, x], [y, x + 1], [y + 1, x], [y, x - 1]
        ]
        # Validation of neighbors:
        to_keep = []
        for i in range(len(neighbors)):
            if neighbors[i][0] >= 0 and neighbors[i][0] <= 3 and neighbors[i][1] >= 0 and neighbors[i][1] <= 3:
                to_keep.append(i)

        return [neighbors[i] for i in to_keep]

    def get_safe_mask(self, cave : list) -> list:
        '''
            This function generates of the binary mask of the cave representation where True is safe and False is possible dangerous.
        :param cave: list, 2d
            The agent's representation of the cave
        :return: list, 2d
        '''
        # Generating the initial mask.
        safe_mask = [[False for i in range(len(cave))] for j in range(len(cave))]

        # Filling the safe mask.
        for i in range(len(cave)):
            for j in range(len(cave)):
                if cave[i][j] == "" or ("OK" in cave[i][j] or ("?W" not in cave[i][j] and "?P" not in cave[i][j] and "p" not in cave[i][j] and not ("w" in cave[i][j] and self.wumpus_alive))):
                    safe_mask[i][j] = True
        return safe_mask

    def get_next_action(self, cave : list) -> str:
        '''
            This function based on the cave view returns the chosen action.
        :param cave: list, 2d
            The agent's representation of the cave.
        :return: str
        '''
        # Generating the safe mask.
        mask = self.get_safe_mask(cave)

        # Checking if the Gold is in the agent location's.
        if "G" in self.cave[self.agent_location[0]][self.agent_location[1]] and not self.grabbed_gold:
            # Grabbing the gold.
            self.grabbed_gold = True
            return "grab"
        # If the wumpus location is known and is in the same line with the agents location the the agent will shoot.
        elif all(self.wumpus_location) and self.wumpus_alive and self.arrows:
            if self.wumpus_location[0] == self.agent_location[0] or self.wumpus_location[1] == self.agent_location[1]:
                shoot_diretion = self.dif2move[
                    tuple([
                        self.agent_location[0] - self.wumpus_location[0],
                        self.agent_location[1] - self.wumpus_location[1]
                    ])
                ]
                action = f"shoot-{shoot_diretion}"
                self.arrows -= 1
        else:
            # Getting the neighbors coordinates.
            neighbors = self.get_neighbors(self.agent_location[0], self.agent_location[1])

            # Getting the safe neighbors.
            save_neighbors = [neighbor for neighbor in neighbors if mask[neighbor[0]][neighbor[1]]]

            # Choosing a random cell from safe neighbors to move in.
            if len(save_neighbors) <= 0:
                action = random.choice([
                    self.dif2move[tuple([
                        self.agent_location[0] - neighbor[0],
                        self.agent_location[1] - neighbor[1]
                    ])] for neighbor in neighbors
                ])
            else:
                action = None
                # Choosing the neighbor with the gold in it.
                for neighbor in save_neighbors:
                    if "G" in cave[neighbor[0]][neighbor[1]]:
                        action = self.dif2move[
                            tuple([
                                self.agent_location[0] - neighbor[0],
                                self.agent_location[1] - neighbor[1]
                            ])
                        ]
                # Chosing a random cell to move in.
                if not action:
                    action = random.choice([
                        self.dif2move[tuple([
                            self.agent_location[0] - neighbor[0],
                            self.agent_location[1] - neighbor[1]
                        ])] for neighbor in save_neighbors
                    ])
        return action

    def get_action(self, cell_info : dict, agent_position : list=None, gold : bool = None, dead : bool = None) -> str:
        '''
            This function returns the agent's action based on the cave information.
        :param cell_info: dict
            The information of senses returned by cave, which is a dictionary with binary values of the following form.
                {
                    "breeze" - if the breeze is perceived in the cell.
                    "stench" - if the stench is perceived in the cell.
                    "glitter" - if the glitter is perceived in the cell.
                    "scream" - if the wumpus was killed.
                    "bump" - if the agent tried to move in a wall.
                }
        :param agent_position: list
            The location of the agent in the cave.
        :param gold: bool, default = None
            The boolean value used to inform the agent about gold.
        :param dead: bool, default = None
            The boolean value used to inform if the agent is dead or not.
        :return: str
        '''
        # Updating the agent location
        if agent_position:
            self.agent_location = agent_position
        # Making a temporary copy of the cave.
        temp_cave = deepcopy(self.cave)

        # Updating the cave with the users location.
        temp_cave[self.agent_location[0]][self.agent_location[1]] += "A"

        # Printing the winning state.
        if gold:
            print("ACTION -> win")
            return "win"
        elif gold:
            # Canceling the assumption of possible Gold.
            self.cave[self.agent_location[0]][self.agent_location[1]] = self.cave[self.agent_location[0]][self.agent_location[1]].replace("?G", "")
        elif self.grabbed_gold and not gold:
            # Canceling the assumption of possible Gold.
            self.cave[self.agent_location[0]][self.agent_location[1]] = self.cave[self.agent_location[0]][self.agent_location[1]].replace("?G", "")
            self.grabbed_gold = False
        if dead:
            print("DEAD")
            return "dead"
        print(self.agent_location)
        print(self.history)
        if tuple(self.agent_location) not in self.history:
            # Updating the cave view based on the cell information.
            self.update_view(cell_info)

            # Updating the history.
            self.history.append(tuple(self.agent_location))

        # Getting the next action.
        action = self.get_next_action(self.cave)
        print(f"ACTION -> {action}")
        return action