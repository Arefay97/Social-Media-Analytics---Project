import utils as utils
import Graph_Exploration as Graph_Exploration
import importlib
import networkx as nx
import Louvain_algo as Louvain_algo
import Data_Reduction as Data_Reduction
import time as t
#loading nodes and edges in dataframes
nodes,edges = utils.Load_data("musae_facebook_target.csv","musae_facebook_edges.csv")

#preprocess edges data
edges = Data_Reduction.Remove_selfloops(edges)

#create the graph
graph = utils.Create_Graph(nodes,edges)
print("Graph created")

#after removing selfloops there are nodes without any edges
#graph = utils.Reduce_with_min_x_edges(graph,0)

#check graph connectivity
#Is_Connected = utils.Graph_connectivity(graph)


#apply Louvain algorithm
print("Starting Louvain")
algorithm = Louvain_algo.Louvain_algo(graph)
Communities = algorithm.run()

#add Louvain_id as an attribute to each node in the graph
graph = utils.add_community_ids(graph,list(Communities.values()),'Louvain_id')
print("community id is added to the graph")
#add graph to neo4j



"""

print("starting loading to neo4j, olease modify userName, passWord, and URI")




userName = "neo4j"
passWord = 
URI = 
start = t.time()

utils.Load_to_neo4j(URI, userName, passWord, graph)
print("Graph Loaded To Neo4j")
total_time = t.time() - start
print(f"it takes {total_time} to load the graph to neo4j")
"""
