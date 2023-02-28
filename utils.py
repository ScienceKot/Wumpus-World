def matrix2json(matrix : list, agent_location : list) -> list:
    '''
        This function converts the matrix representation of the cave into a json containing the cell's information.
    :param matrix: list, 2d
        The 2d list representing the cave state.
    :param agent_location: list, 1d
        The agent location in the cave.
    :return: list
    '''
    # Creating the empty dictionary representing the matrix.
    matrix_representation = {}
    # Adding the cell information.
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            matrix_representation[f"{i}{j}"] = {
                "agent" : True if agent_location[0] == i and agent_location[1] == j else False,
                "wumpus" : True if "W" in matrix[i][j] else False,
                "pit" : True if "P" in matrix[i][j] else False,
                "breeze" : True if "b" in matrix[i][j] else False,
                "stench" : True if "s" in matrix[i][j] else False,
                "gold" : True if "G" in matrix[i][j] else False,
                "glitter" : True if "g" in matrix[i][j] else False,
            }
    return matrix_representation
