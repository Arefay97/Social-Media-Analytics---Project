import Code.utils as utils
import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

def Explore_nodes_data(G):
    '''this function takes networkx graph G as input and prints n nodes with their attributes'''
    c = 0
    for node in G.nodes():
        if c <5 :
            node_features = G.nodes[node]
            print(f"Node {node}: {node_features}")
        else: 
            pass
        c = c+1

def Calculate_degree_centrality(G, nodes):
    '''this function takes networkx graph G and pandas dataframe nodes as input,
     calculates the betweenness centrality,
      adds the betweenness value to the coresponding node in the graph and the dataframe,
       and returns the graph and the dataframe '''

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
    '''this function takes networkx graph G and pandas dataframe nodes as input,
     calculates the betweenness centrality,
      adds the betweenness value to the coresponding node in the graph and the dataframe,
       and returns the graph and the dataframe '''

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
    '''this function takes networkx graph G and pandas dataframe nodes as input,
     calculates the closeness centrality,
      adds the closeness value to the coresponding node in the graph and the dataframe,
       and returns the graph and the dataframe '''

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


def get_cut_sizes(G,com_id):
    '''this function takes a networkx graph and the attribute name of the community id,
    calculates the cut size of each cluster in the graph,
    returns the cut sizes of each cluster as dictionary'''
    # Initializing an empty dictionary to store cut sizes for each community
    cut_sizes = {}

    # Iterating over edges in the graph
    for u, v in G.edges():
        # Checking if the nodes belong to different communities
        community_u = G.nodes[u].get(com_id)
        community_v = G.nodes[v].get(com_id)
        
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
    '''this function takes a networkx graph as input,
    checks if there are any connected components in the graph,
    and retuens True if it has several connected components or False'''

    connected_components = list(nx.connected_components(graph))

    if len(connected_components) > 1:
        return False
    else:
        return True

    
def has_diagonal_one(graph):
    '''this function takes a graph as input,
    calculates the Adjacency matrix,
    checks if there are 1s in the diagonal representing the self loops,
    and returns true or false'''

    #calculate the Adjacency matrix
    matrix = nx.adjacency_matrix(graph)
    count = 0
    n, _ = matrix.shape
    #loop over the diagonal of the matrix
    for i in range(n):
        #check if the diagonal is 1
        if matrix[i, i] == 1:
            count += 1
    if count > 0:
        return True #has self loops
    else:
        return False #graph doesn't have selfloops

def get_eigenvalues_differences(graph):
    '''this function takes input as a graph,
    calculates the Laplacian matrix,
    gets the eigenvalues of the Laplacian matrix,
    draws the histogram of the eigenvalues in ascending order,
    returns the top 100 differences between nodes'''
    L = nx.normalized_laplacian_matrix(graph)
    e = np.linalg.eigvals(L.toarray())
    e = sorted(e,reverse=False)
    #get the real and imaginary parts
    e= [(z.real, z.imag) for z in e]
    # Extract the first elements from the list of tuples
    values = [t[0] for t in e]
    # Indices for the x-axis
    indices = list(range(len(values)))
    # Plot the histogram as a bar chart
    plt.bar(indices, values)
    # Customize the plot
    plt.xlabel('Index')
    plt.ylabel('Value')
    plt.title('Histogram of Values by Index')
    # Show the plot
    plt.show()

    # Extract the first elements from the list of tuples
    values = [t[0] for t in e]

    # Calculate the differences between consecutive elements
    differences = [(abs(values[i] - values[i - 1]), i - 1, i) for i in range(1, len(values))]

    # Sort the differences by the gap size in descending order
    sorted_differences = sorted(differences, key=lambda x: x[0], reverse=True)

    # Get the top 100 maximum differences
    top_100_differences = differences[:100]

    # Print the results
    '''i=0
    for diff, index1, index2 in top_100_differences:
        print(f"Difference ",i,":", {diff}, "Indices: {index1} and {index2}")
        i+=1'''
    return top_100_differences


def calculate_intra_density(G, community_nodes):
    '''this function calculates the intra-density for each community'''
    subgraph = G.subgraph(community_nodes)
    num_edges_within = subgraph.number_of_edges()
    num_nodes = len(community_nodes)
    total_possible_edges = num_nodes * (num_nodes - 1) / 2
    return num_edges_within / total_possible_edges if total_possible_edges > 0 else 0

'''intra_densities = {}
#print("starting to calculate the densities")
for community, nodes in community_dict.items():
    intra_densities[community] = calculate_intra_density(graph, nodes)
#print(intra_densities)'''