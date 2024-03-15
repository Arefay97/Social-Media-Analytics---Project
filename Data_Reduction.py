import utils


def Reduce_with_min_x_edges(G , target_degree):
    '''Function Describtion'''



    #nodes with the target degree
    nodes_to_remove = [node for node, degree in dict(G.degree()).items() if degree == target_degree]

    # Remove corresponding edges
    for node in nodes_to_remove:
        neighbors = list(G.neighbors(node))
        for neighbor in neighbors:
            G.remove_edge(node, neighbor)

    # Remove identified nodes
    G.remove_nodes_from(nodes_to_remove)

    # Return the modified version of the graph
    return G