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

    Max_degree_centrality = max(degree_centrality.values())


def Calculate_betweenness_centrality(G, nodes):
    '''Function Decription'''

    betweenness_centrality = nx.betweenness_centrality(G) 


    for node_id, value in betweenness_centrality.items():
        if node_id in G.nodes:
            G.nodes[node_id]['betweenness_centerality'] = value

    nodes['betweenness_centerality'] = nodes['id'].map(betweenness_centrality)