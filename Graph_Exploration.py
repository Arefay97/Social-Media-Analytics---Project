import utils
import networkx as nx
import numpy as np

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


def get_cut_sizes(G):

    # Initializing an empty dictionary to store cut sizes for each community
    cut_sizes = {}

    # Iterating over edges in the graph
    for u, v in G.edges():
        # Checking if the nodes belong to different communities
        community_u = G.nodes[u].get('community_id')
        community_v = G.nodes[v].get('community_id')
        
        if community_u is not None and community_v is not None and community_u != community_v:
            # Updating the cut size for each community
            if community_u in cut_sizes:
                cut_sizes[community_u] += 1
            else:
                cut_sizes[community_u] = 1
            
            if community_v in cut_sizes:
                cut_sizes[community_v] += 1
            else:
                cut_sizes[community_v] = 1

    return cut_sizes

def Graph_connectivity(graph):

    connected_components = list(nx.connected_components(graph))

    if len(connected_components) > 1:
        print("The graph has multiple connected components.")
    else:
        print("The graph is fully connected.")

def Has_Connected_Component(graph):
    L = nx.normalized_laplacian_matrix(graph)
    e = np.linalg.eigvals(L.toarray())
    for arr in e:
        zero_els = np.count_nonzero(arr==0)
    if zero_els == 0:
        return False #graph doesn't have connected components, only one component
    elif zero_els > 0 :
        return True #yes graph has connected components
    
def has_diagonal_one(graph):
    matrix = nx.adjacency_matrix(graph)
    count = 0
    n, _ = matrix.shape
    for i in range(n):
        if matrix[i, i] == 1:
            count += 1
    if count > 0:
        return True #has self loops
    else:
        return False #graph doesn't have selfloops