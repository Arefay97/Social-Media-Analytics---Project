import networkx as nx
import numpy as np
import random

"""Make sure that the graph is connected."""
    
class Louvain_algo:
    def __init__(self,G):
        self.G = G
        self.m = G.number_of_edges()
        self.degree = G.degree()
        self.com = {}
        self.com_inv = {}
        self.change = True
        self.hypergraph = None
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
        nodes = list(self.G.nodes())
        random.seed(2)
        random.shuffle(nodes)
        changes = 0
        for v in nodes:
            original = "original"
            #delete v from its community:
            if v in self.com_inv.keys():
                com_index = self.com_inv[v]
                del self.com_inv[v]
                self.com[com_index].remove(v)
                original = com_index 
            #Find the neighbor with highest modularity gain
            #print("com_inv",com_inv)
            gains = []
            for neighbor in self.G[v]:
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
            if com_index!=original:
                changes+=1
        print("changes",changes)
        if changes>1:
            self.change = True

    def construct_community_graph(self,com,G,node_degrees):
        # Initialize empty graph
        community_graph = nx.Graph()
        print("start calculating total degrees")
        # Add nodes for each community and calculate total degrees
        total_degrees = {}
        for community, members in com.items():
            community_graph.add_node(community, size=len(members))
            total_degrees[community] = sum(node_degrees[node] for node in members)
        # Add total degree as node attribute
        nx.set_node_attributes(community_graph, total_degrees, 'total_degree')
        print("total degrees calculated")
        
        # Add edges between community nodes and calculate shared degrees
        for community1, members1 in com.items():
            for community2, members2 in com.items():
                if community1 < community2:
                    shared_edges = sum(len(set(G.neighbors(node)).intersection(members2)) for node in members1)
                    #shared_edges = sum(1 for edge in self.G.edges() if edge[0] in members1 and edge[1] in members2)
                    #print(shared_degree)
                    if shared_edges > 0:
                        community_graph.add_edge(community1, community2, shared_degree=2*shared_edges)
        print("done with shared degrees")    

        
        return community_graph
    
    def generate_hyper(self, com,G,node_degrees,com_inv):
        """Generates new coarse grain graph with each community as a single
        node.

        Weights between nodes are the sum of all weights between respective
        communities and self loops are added for the weights of he internal
        edges.
        """
        new_graph = nx.Graph()
        total_degrees = {}
        # Create nodes for each community.
        for community, members in com.items():
            if len(members)==0:
                continue
            new_graph.add_node(community)
            total_degrees[community] = sum(node_degrees[node] for node in members)
        nx.set_node_attributes(new_graph, total_degrees, 'total_degree')
        # Create the combined edges from the individual old edges.
        for u, v, w in G.edges(data="shared_degree", default=1):
            c1 = com_inv[u]
            c2 = com_inv[v]
            new_weight = w
            if new_graph.has_edge(c1, c2):
                new_weight += new_graph[c1][c2].get("shared_degree", 1)
            new_graph.add_edge(c1, c2, shared_degree=new_weight)
        return new_graph


    def modularity_gain_hyper(self,hyper_graph,node,neighbor,com,com_inv):
        di = hyper_graph.nodes[node].get('total_degree')
        dj = hyper_graph.nodes[neighbor].get('total_degree')
        #di = hyper_graph[node][node]['shared_degree']
        #dj = hyper_graph[neighbor][neighbor]['shared_degree']
        if neighbor not in com_inv:
            shared_degree = hyper_graph[node][neighbor]['shared_degree']
            return 1/(2*self.m)*(shared_degree-di*dj/self.m)
        else:
            com_index = com_inv[neighbor]
            members = com[com_index]
            shared_degree = 0
            for n in hyper_graph.neighbors(node):
                if n in members:
                    shared_degree +=hyper_graph[node][neighbor]['shared_degree']
            #print("shared_dergee",shared_degree)
            return 1/(2*self.m)*(shared_degree-di*dj/self.m)


 
    def second_passage(self,hyper_graph,hyper_com,hyper_com_inv):
        changes = 0
        for v in hyper_graph.nodes():
            original = "original"
            #delete v from its community:
            if v in hyper_com_inv.keys():
                hyper_com_index = hyper_com_inv[v]
                del hyper_com_inv[v]
                hyper_com[hyper_com_index].remove(v)
                original = hyper_com_index  
            #Find the neighbor with highest modularity gain
            #print("com_inv",com_inv)
            gains = []
            for neighbor in hyper_graph.neighbors(v):
                if v!=neighbor:
                   gains.append((self.modularity_gain_hyper(hyper_graph,v,neighbor,hyper_com,hyper_com_inv),neighbor))
            closest_node = max(gains)[1]
            #print("closest_node of",v,"is",closest_node)
            #print(hyper_com_inv)
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
            if hyper_com_index!=original:
                changes+=1
        print("changes",changes)
        if changes>1:
            self.change = True

    
    def combine_com(self,com,hypercom):
        final_com = {}
        for hyper,hyper_val in hypercom.items():
            if len(hyper_val)==0:
                continue
            final_com[hyper] = {node for node_set in hyper_val for node in com[node_set]} # [item for sublist in nested_list for item in sublist]
        return(final_com)
    

    def run(self,number_of_passages=2):
        print("passage 1")
        while self.change==True:
            self.change = False
            print("start iteration")
            self.passage()
            #modularity = nx.community.modularity(self.G,list(self.com.values()))
            #print("modularity = ",modularity)
        print("There were", len(self.com), "communities detected in passage 1.")
        print("com_inv",self.com_inv)
        print("com",self.com)
        first_modularity = nx.community.modularity(self.G,list(self.com.values()))
        print("modularity",first_modularity)
        print("passage 2")
        print("creating hypergraph")
        hypergraph = self.generate_hyper(self.com,self.G,self.degree,self.com_inv)
        #nx.draw(hypergraph,with_labels=True)
        hyper_com = {}
        hyper_com_inv = {}
        self.change=True
        iter = 0
        while self.change==True:
            self.change=False
            print("start iteration")
            self.second_passage(hypergraph,hyper_com,hyper_com_inv)
            modularity = nx.community.modularity(hypergraph,list(hyper_com.values()))
            print("modularity = ",modularity)
            iter+=1
            if iter>10:
                break
        print("The number of communities was reduced to ",len(hyper_com))
        print("hyper_com",hyper_com)        
        final_communities = self.combine_com(self.com,hyper_com)
        new_modularity = nx.community.modularity(self.G,list(final_communities.values()))
        print("new_modularity:",new_modularity)
        if new_modularity<first_modularity:
            print("did it happen?")
            return self.com
        print("passage 3")
        print("creating hypergraph")
        hypergraph = self.generate_hyper(hyper_com,hypergraph,hypergraph.degree,hyper_com_inv)
        hyper_hyper_com = {}
        hyper_hyper_com_inv = {}
        self.change=True
        iter = 0
        while self.change==True:
            self.change = False
            print("start iteration")
            self.second_passage(hypergraph,hyper_hyper_com,hyper_hyper_com_inv)
            modularity = nx.community.modularity(hypergraph,list(hyper_hyper_com.values()))
            print("modularity = ",modularity)
            iter+=1
            if iter>5:
                break
        print("The number of communities was reduced to ",len(hyper_hyper_com))
        old_modularity = new_modularity
        final_hyper_communities = self.combine_com(hyper_com,hyper_hyper_com)
        final_final_communities = self.combine_com(self.com,final_hyper_communities)
        new_modularity = nx.community.modularity(self.G,list(final_final_communities.values()))
        print("new_modularity:",new_modularity)
        if new_modularity<old_modularity:
            return final_communities
        
        
        return final_final_communities
        

