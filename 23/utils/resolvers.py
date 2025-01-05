import itertools as it
from pathlib import Path

CONNECTION_SPLITTER = "-"


def _read_and_process_file(filename: Path) -> tuple:
    """Reads and processes the input file containing computer connections.

    Args:
        filename (Path): Path to the input file.

    Returns:
        list: A list of tuples representing connections between computers.
    """
    with open(filename) as f:
        connections_raw = f.read().split()

    connections = [
        tuple(sorted(connection.split(CONNECTION_SPLITTER)))
        for connection in connections_raw
    ]

    return connections

def _find_interconnections_trios(connections: list) -> set:
    """Finds all interconnection trios in the network.

    A trio is a set of three computers where each is directly connected to
    the others.

    Args:
        connections (list): A list of tuples representing connections.

    Returns:
        set: A set of interconnection trios found in the network.
    """
    interconnections = set()
    grouper_ego = it.groupby(sorted(connections), key=lambda x: x[0])
    for computer, ego_graph_generator in grouper_ego:
        ego_graph = list(ego_graph_generator)
        for computer_connection in ego_graph:
            computer_connected = computer_connection[1]
            ego_graph_rest = [
                connection[1]
                for connection in ego_graph
                if connection[1] != computer_connected
            ]

            interconnections_ego = [
                (computer, *connection)
                for connection in connections
                if (
                    connection[0] == computer_connected
                    and connection[1] in ego_graph_rest
                )
            ]


            for interconnection in interconnections_ego:
                interconnections.add(interconnection)

    return interconnections

def _are_all_connected(dict_computers_connections: dict,
                       computers: set) -> bool:
    """Checks if all computers in a given set are connected to each other.

    Args:
        dict_computers_connections (dict): A dictionary mapping each computer
            to its connections.
        computers (set): A set of computers to check.

    Returns:
        bool: True if all computers in the set are interconnected, otherwise False.
    """
    return all(
        computer_b in dict_computers_connections[computer_a]
        for computer_a, computer_b in it.combinations(computers, 2)
    )

def _biggest_lan(computer: str, dict_computers_connections: dict) -> set:
    """Finds the largest fully connected local area network (LAN) starting
    from a given computer.

    Args:
        computer (str): The starting computer.
        dict_computers_connections (dict): A dictionary mapping each computer
            to its connections.

    Returns:
        set: The largest fully connected subset of computers forming a LAN.
    """
    nodes = set(
        [computer]
        + dict_computers_connections[computer]
    )

    for size in range(len(nodes), 0, -1):
        for lan in it.combinations(nodes, size):
            if _are_all_connected(dict_computers_connections, set(lan)):
                return set(lan)

    return set()

def _find_interconnections(connections: list) -> set:
    """Finds the largest interconnected computer network (LAN).

    Args:
        connections (list): A list of tuples representing connections.

    Returns:
        set: The largest interconnected computer network.
    """
    unique_computers = {
        computer
        for connection in connections
        for computer in connection
    }

    dict_computers_connections = {
        computer: [
            computer_b
            for computer_a, computer_b in connections
            if computer_a == computer
        ] + [
            computer_a
            for computer_a, computer_b in connections
            if computer_b == computer
        ]
        for computer in unique_computers
    }

    biggest_lan = set()
    for computer in unique_computers:
        biggest_lan_computer = _biggest_lan(
            computer=computer,
            dict_computers_connections=dict_computers_connections
        )

        if len(biggest_lan_computer) > len(biggest_lan):
            biggest_lan = biggest_lan_computer

    return biggest_lan


def _decrypt_password(connections) -> str:
    """Decrypts a password by identifying the largest interconnected LAN.

    Args:
        connections (list): A list of tuples representing connections.

    Returns:
        str: The decrypted password, consisting of sorted computer names in
            the largest LAN.
    """
    largest_lan = _find_interconnections(connections)

    return ",".join(sorted(largest_lan))

def first_exercise(filename: Path) -> int:
    computers_connections = _read_and_process_file(filename)

    interconnections = _find_interconnections_trios(computers_connections)

    return len({
        interconnection
        for interconnection in interconnections
        if any(computer.startswith("t") for computer in interconnection)
    })

def second_exercise(filename: Path):
    computers_connections = _read_and_process_file(filename)

    return _decrypt_password(computers_connections)
