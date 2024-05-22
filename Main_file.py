import utils
import Graph_Exploration
import importlib
import networkx as nx
import Louvain_algo

#loading nodes and edges in dataframes
nodes,edges = utils.Load_data("musae_facebook_target.csv","musae_facebook_edges.csv")

#preprocess edges data
edges = utils.Remove_selfloops(edges)

#create the graph
graph = utils.Create_Graph(nodes,edges)

#check for self loops again
'''Self_Loops = utils.has_diagonal_one(graph)

if Self_Loops == True :
    #preprocess edges data
    edges = utils.Remove_selfloops(edges)
    graph = utils.Create_Graph(nodes,edges)'''

#after removing selfloops there are nodes without any edges
#graph = utils.Reduce_with_min_x_edges(graph,0)

#check graph connectivity
Is_Connected = utils.Graph_connectivity(graph)

#apply some centrality measures to explore the graph
graph, nodes = utils.Calculate_betweenness_centrality(graph,nodes)
graph, nodes = utils.Calculate_closeness_centrality(graph,nodes)

#apply Louvain algorithm
algorithm = Louvain_algo(graph)
Communities = algorithm.run()

#calculate the eigenvalues for Laplacian matrix to estimate the number of communities
top_100_differences = utils.get_eigenvalues_differences(graph)





#

