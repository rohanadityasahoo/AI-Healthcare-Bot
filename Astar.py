# A* Search Algorithm - Romania Style Graph

graph = {
    'arad': {'zerind': 75, 'sibiu': 140, 'timisoara': 118},
    'zerind': {'arad': 75, 'oradea': 71},
    'oradea': {'zerind': 71, 'sibiu': 151},
    'sibiu': {'arad': 140, 'oradea': 151, 'fagaras': 99, 'rimnicu': 80},
    'timisoara': {'arad': 118, 'lugoj': 111},
    'lugoj': {'timisoara': 111, 'mehadia': 70},
    'mehadia': {'lugoj': 70, 'drobeta': 75},
    'drobeta': {'mehadia': 75, 'craiova': 120},
    'craiova': {'drobeta': 120, 'rimnicu': 146, 'pitesti': 138},
    'rimnicu': {'sibiu': 80, 'craiova': 146, 'pitesti': 97},
    'fagaras': {'sibiu': 99, 'bucharest': 211},
    'pitesti': {'rimnicu': 97, 'craiova': 138, 'bucharest': 101},
    'bucharest': {}
}

heuristic = {
    'arad': 366,
    'zerind': 374,
    'oradea': 380,
    'sibiu': 253,
    'timisoara': 329,
    'lugoj': 244,
    'mehadia': 241,
    'drobeta': 242,
    'craiova': 160,
    'rimnicu': 193,
    'fagaras': 176,
    'pitesti': 100,
    'bucharest': 0
}

def a_star(start, goal):

    open_list = [start]
    closed_list = []

    g = {start: 0}
    parent = {start: None}

    while open_list:

        current = min(open_list, key=lambda node: g[node] + heuristic[node])

        if current == goal:
            path = []
            while current:
                path.append(current)
                current = parent[current]
            path.reverse()
            print("Optimal Path:", path)
            print("Total Cost:", g[goal])
            return

        open_list.remove(current)
        closed_list.append(current)

        for neighbour in graph[current]:
            cost = g[current] + graph[current][neighbour]

            if neighbour not in open_list and neighbour not in closed_list:
                open_list.append(neighbour)
                parent[neighbour] = current
                g[neighbour] = cost

            else:
                if cost < g.get(neighbour, float('inf')):
                    g[neighbour] = cost
                    parent[neighbour] = current
                    if neighbour in closed_list:
                        closed_list.remove(neighbour)
                        open_list.append(neighbour)

    print("Path not found")

# Run
a_star('arad', 'bucharest')