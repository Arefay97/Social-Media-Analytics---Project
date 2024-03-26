import utils

def Explore_nodes_data(G):
    '''Function Description'''
    c = 0
    for node in G.nodes():
        if c <5 :
            node_features = G.nodes[node]
            print(f"Node {node}: {node_features}")
        else: 
            pass
        c = c+1

def Calculate_degree_centrality(G, nodes):
    '''Function Decription'''

    #measuring the degree centrality 
    degree_centrality = nx.degree_centrality(G)

    #Insert the centality value for each node to the graph
    for node_id, value in degree_centrality.items():
        if node_id in G.nodes:
            G.nodes[node_id]['degree_centrality'] = value
        
    #Add the centrality values to nodes dataframe
    nodes['degree_centerality'] = nodes['id'].map(degree_centrality)

    #Max_degree_centrality = max(degree_centrality.values())

    return G, nodes


def Calculate_betweenness_centrality(G, nodes):
    '''Function Decription'''

    #calculate betweenness for nodes
    betweenness_centrality = nx.betweenness_centrality(G) 

    #add to the graph for each node its coresponding betweenness value
    for node_id, value in betweenness_centrality.items():
        if node_id in G.nodes:
            G.nodes[node_id]['betweenness_centerality'] = value
    #add values to the nodes dataframe
    nodes['betweenness_centerality'] = nodes['id'].map(betweenness_centrality)

    return G, nodes

def Calculate_closeness_centrality(G,nodes):
    '''Function Description'''

    #calculate closeness centrality for nodes in the graph
    closeness_centrality = nx.closeness_centrality(G)

    #add to the graph for each node its coresponding closeness value
    #nodes.to_csv("nodes with betweenness.csv")
    for node_id, value in closeness_centrality.items():
        if node_id in G.nodes:
            G.nodes[node_id]['closeness_centrality'] = value

    #add values to the nodes dataframe
    nodes['closeness_centrality'] = nodes['id'].map(closeness_centrality)

    return G,nodes