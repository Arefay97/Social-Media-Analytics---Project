import utils
import Graph_Exploration
import importlib
import networkx as nx

#loading nodes and edges in dataframes
nodes,edges = utils.Load_data("musae_facebook_target.csv","musae_facebook_edges.csv")

#preprocess edges data
edges = utils.Remove_selfloops(edges)
#create the graph
graph = utils.Create_Graph(nodes,edges)

#after removing selfloops there are nodes without any edges
graph = utils.Reduce_with_min_x_edges(graph,0)





#

