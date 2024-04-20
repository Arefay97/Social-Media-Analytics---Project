import networkx as nx
import numpy as np

"""Make sure that the graph is connected."""
    
class Louvain_algo:
    def __init__(self,G):
        self.G = G
        self.m = G.number_of_edges()
        self.degree = G.degree()
        self.com = {}
        self.com_inv = {}
        if nx.is_connected(G)==False:
            print("Please use a connected component of your graph.")
    
    def modularity_gain(self,node,neighbor):
        di = self.degree(node)
        dj = self.degree(neighbor)
        if neighbor not in self.com_inv:
            return 1/(2*self.m)*(2-di*dj/self.m)
        else:
            com_index = self.com_inv[neighbor]
            members = self.com[com_index]
            shared_degree = 0
            for m in members:
                if m in self.G.neighbors(node):
                    shared_degree +=2
            return 1/(2*self.m)*(shared_degree-di*dj/self.m)
        
    def passage(self):
        for v in self.G.nodes():
            #delete v from its community:
            if v in self.com_inv.keys():
                com_index = self.com_inv[v]
                del self.com_inv[v]
                self.com[com_index].remove(v) 
            #Find the neighbor with highest modularity gain
            #print("com_inv",com_inv)
            gains = []
            for neighbor in self.G.neighbors(v):
                gains.append((self.modularity_gain(v,neighbor),neighbor))
            closest_node = max(gains)[1]
            # Add v to the same community as the closest_node
            #check if closest node is already in a community:
            if closest_node in self.com_inv.keys():
                com_index = self.com_inv[closest_node]
                self.com_inv[v]=com_index
                self.com[com_index].add(v)
            else:
                #Add v and neighbor in a new created community
                com_index = len(self.com)
                self.com_inv[v]=com_index
                self.com_inv[closest_node]= com_index
                self.com[com_index] = {v,closest_node}

    def construct_community_graph(self,com,G,node_degrees):
        # Initialize empty graph
        community_graph = nx.Graph()
        print("start calculating total degrees")
        # Add nodes for each community and calculate total degrees
        total_degrees = {}
        for community, members in com.items():
            community_graph.add_node(community, size=len(members))
            total_degrees[community] = sum(node_degrees[node] for node in members)
        print("total degrees calculated")
        
        # Add edges between community nodes and calculate shared degrees
        for community1, members1 in com.items():
            for community2, members2 in com.items():
                if community1 != community2:
                    shared_degree = sum(len(set(G.neighbors(node)).intersection(members2)) for node in members1)
                    #print(shared_degree)
                    if shared_degree > 0:
                        community_graph.add_edge(community1, community2, shared_degree=shared_degree)
        print("done with shared degrees")    
        # Add total degree as node attribute
        nx.set_node_attributes(community_graph, total_degrees, 'total_degree')
        
        return community_graph


    def modularity_gain_hyper(self,hyper_graph,node,neighbor,com,com_inv):
        di = hyper_graph.nodes[node].get('total_degree')
        dj = hyper_graph.nodes[neighbor].get('total_degree')
        if neighbor not in com_inv:
            shared_degree = hyper_graph[node][neighbor]['shared_degree']
            return 1/(2*self.m)*(2*shared_degree-di*dj/self.m)
        else:
            com_index = com_inv[neighbor]
            members = com[com_index]
            shared_degree = 0
            for n in hyper_graph.neighbors(node):
                if n in members:
                    shared_degree +=2*hyper_graph[node][neighbor]['shared_degree']
            #print("shared_dergee",shared_degree)
            return 1/(2*self.m)*(shared_degree-di*dj/self.m)


 
    def second_passage(self,hyper_graph):
        hyper_com = {}
        hyper_com_inv = {}
     
        for v in hyper_graph.nodes():
            #delete v from its community:
            if v in hyper_com_inv.keys():
                hyper_com_index = hyper_com_inv[v]
                del hyper_com_inv[v]
                hyper_com[hyper_com_index].remove(v) 
            #Find the neighbor with highest modularity gain
            #print("com_inv",com_inv)
            gains = []
            for neighbor in hyper_graph.neighbors(v):
                gains.append((self.modularity_gain_hyper(hyper_graph,v,neighbor,hyper_com,hyper_com_inv),neighbor))
            
            closest_node = max(gains)[1]
            #print(max(gains)[0])
    
            # Add v to the same community as the closest_node
            #check if closest node is already in a community:
            if closest_node in hyper_com_inv.keys():
                hyper_com_index = hyper_com_inv[closest_node]
                hyper_com_inv[v]=hyper_com_index
                hyper_com[hyper_com_index].add(v)
            else:
                #Add v and neighbor in a new created community
                hyper_com_index = len(hyper_com)
                hyper_com_inv[v]=hyper_com_index
                hyper_com_inv[closest_node]= hyper_com_index
                hyper_com[hyper_com_index] = {v,closest_node}
            #print(original,hyper_com_index)
        return hyper_com
    
    def combine_com(self,com,hypercom):
        final_com = {}
        for hyper,hyper_val in hypercom.items():
            final_com[hyper] = {node for node_set in hyper_val for node in com[node_set]} # [item for sublist in nested_list for item in sublist]
        return(final_com)
    

    def run(self):
        print("passage 1")
        self.passage()
        print("There were", len(self.com), "communities detected.")
        print("creating hypergraph")
        hypergraph = self.construct_community_graph(self.com,self.G,self.degree)
        print("passage 2")
        h = self.second_passage(hypergraph)
        print("The number of communities was reduced to ",len(h))
        final_communities = self.combine_com(self.com,h)
        return final_communities
        

