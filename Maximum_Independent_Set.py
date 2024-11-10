import networkx as nx
def find_mirrors(G, v):
    N_v = set(G.neighbors(v))
    N2_v = set(nx.single_source_shortest_path_length(G, v, cutoff=2).keys()) - N_v - {v}
    mirrors = set()
    for u in N2_v:
        N_v_minus_N_u = N_v - set(G.neighbors(u))
        if all(G.has_edge(x, y) for x in N_v_minus_N_u for y in N_v_minus_N_u if x != y):
            mirrors.add(u)
    return mirrors

def fold_node(G, v):
    neighbors = list(G.neighbors(v))
    anti_edges = [(u, w) for i, u in enumerate(neighbors) for w in neighbors[i+1:] if not G.has_edge(u, w)]
   
    # Step 1: Add a new node u_ij for each anti-edge u_i u_j in N(v)
    new_nodes = {}
    for u, w in anti_edges:
        new_node = f"{u}_{w}"
        G.add_node(new_node)
        new_nodes[(u, w)] = new_node
   
    # Step 2: Add edges between each u_ij and the nodes in N(u_i) ∪ N(u_j)
    for (u, w), new_node in new_nodes.items():
        neighbors_u_w = set(G.neighbors(u)).union(set(G.neighbors(w)))
        for neighbor in neighbors_u_w:
            G.add_edge(new_node, neighbor)
   
    # Step 3: Add one edge between each pair of new nodes
    new_node_list = list(new_nodes.values())
    for i in range(len(new_node_list)):
        for j in range(i + 1, len(new_node_list)):
            G.add_edge(new_node_list[i], new_node_list[j])
   
    # Step 4: Remove N[v]
    G.remove_nodes_from(neighbors)
    G.remove_node(v)
   
    return G


def mis(G):
    if G.number_of_nodes() == 0:
        return 0, set()
   
    # Check for components
    if nx.number_connected_components(G) > 1:
        total_mis = 0
        total_nodes = set()
        components = list(nx.connected_components(G))
        for c in components:
            subgraph = G.subgraph(c).copy()
            subgraph_mis, subgraph_nodes = mis(subgraph)
            total_mis += subgraph_mis
            total_nodes.update(subgraph_nodes)
        return total_mis, total_nodes
   
    # Check for node domination
    for v in G.nodes():
        for w in G.nodes():
            if v != w and set(G.neighbors(v)).union({v}).issubset(set(G.neighbors(w)).union({w})):
                H = G.copy()
                print(v,w)
                H.remove_node(w)
                return mis(H)
   
    # Check for foldable node
    for v in G.nodes():
        neighbors = list(G.neighbors(v))
        if len(neighbors) <= 4:
            anti_edges = 0
            for i in range(len(neighbors)):
                for j in range(i + 1, len(neighbors)):
                    if not G.has_edge(neighbors[i], neighbors[j]):
                        anti_edges += 1
            if anti_edges <= 3:
                H = fold_node(G.copy(), v)
                sub_mis, sub_nodes = mis(H)
                return 1 + sub_mis, sub_nodes.union({v})
   
    # Select node of maximum degree
    v = max(G.nodes(), key=G.degree)
    mirrors = find_mirrors(G, v)
    H1 = G.copy()
    H1.remove_node(v)
    H1.remove_nodes_from(mirrors)
    H2 = G.copy()
    H2.remove_node(v)
    H2.remove_nodes_from(list(G.neighbors(v)))
   
    mis1, nodes1 = mis(H1)
    mis2, nodes2 = mis(H2)
   
    if mis1 > 1 + mis2:
        return mis1, nodes1
    else:
        return 1 + mis2, nodes2.union({v})

# Exemple d'utilisation
G = nx.Graph()
G.add_edges_from([(1, 2), (1, 3), (2, 4), (3, 4), (4, 5), (1,6), (7,8)])
mis_size, mis_nodes = mis(G)
nx.draw(G, with_labels=True)
plt.show()
nx.draw(nx.complement(G), with_labels=True)
plt.show()
print("Taille du Maximum Independent Set:", mis_size)
print("Nœuds du Maximum Independent Set:", mis_nodes)

