import utils

def Remove_selfloops(edges):
    '''Function Descrition'''

    
    #deleting 179 self loops
    #list of rows that should be droped
    index_to_drop = []
    #iterate over each row
    for index_, row in edges.iterrows():
        #get source and target values
        source = row['source']
        target = row['target']
        #compare the source and target if they are equal
        if source == target:
            #save the index of each row that should be deleted
            index_to_drop.append(index_)
    
    #drop rows in the list
    edges = edges.drop(edges.index[index_to_drop])

    return edges

#def Remove_reciprocal_edges():
    '''Funcrion Description'''





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