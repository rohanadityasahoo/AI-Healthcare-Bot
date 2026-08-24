import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Graph
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
    'arad': 366, 'zerind': 374, 'oradea': 380, 'sibiu': 253,
    'timisoara': 329, 'lugoj': 244, 'mehadia': 241,
    'drobeta': 242, 'craiova': 160, 'rimnicu': 193,
    'fagaras': 176, 'pitesti': 100, 'bucharest': 0
}

G = nx.Graph()
for city in graph:
    for neighbor in graph[city]:
        G.add_edge(city, neighbor, weight=graph[city][neighbor])

pos = nx.spring_layout(G, seed=7)

visited_order = []
final_path = []

def a_star(start, goal):
    open_list = [start]
    closed_list = []

    g = {start: 0}
    parent = {start: None}

    while open_list:
        current = min(open_list, key=lambda node: g[node] + heuristic[node])
        visited_order.append(current)

        if current == goal:
            path = []
            while current:
                path.append(current)
                current = parent[current]
            path.reverse()
            return path

        open_list.remove(current)
        closed_list.append(current)

        for neighbor in graph[current]:
            cost = g[current] + graph[current][neighbor]

            if neighbor not in open_list and neighbor not in closed_list:
                open_list.append(neighbor)
                parent[neighbor] = current
                g[neighbor] = cost

            elif cost < g.get(neighbor, float('inf')):
                g[neighbor] = cost
                parent[neighbor] = current
                if neighbor in closed_list:
                    closed_list.remove(neighbor)
                    open_list.append(neighbor)

path = a_star('arad', 'bucharest')
final_path = path

fig, ax = plt.subplots()

def update(frame):
    ax.clear()
    
    colors = []
    for node in G.nodes():
        if node == 'arad':
            colors.append('green')
        elif node == 'bucharest':
            colors.append('red')
        elif node in visited_order[:frame]:
            colors.append('yellow')
        else:
            colors.append('lightblue')

    nx.draw(G, pos, with_labels=True, node_color=colors, node_size=1200, font_size=8, ax=ax)

    if frame >= len(visited_order):
        edges = list(zip(final_path, final_path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='blue', width=3, ax=ax)

ani = animation.FuncAnimation(fig, update, frames=len(visited_order)+5, interval=800, repeat=False)

plt.show()