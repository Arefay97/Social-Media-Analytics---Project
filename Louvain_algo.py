import networkx as nx
import numpy as np
import random
import time

"""Make sure that the graph is connected."""
    
class Louvain_algo:
    def __init__(self,G,res):
        self.G = G
        self.m = G.number_of_edges()
        self.degree = G.degree()
        self.com = {}
        self.com_inv = {}
        self.change = True
        self.hypergraph = None
        self.res = res
        if nx.is_connected(G)==False:
            print("Please use a connected component of your graph.")
    
    def init_dict(self,G):
        com = {}
        com_inv = {}
        for node in G.nodes:
            com[node] = {node}
            com_inv[node] = node
        return com,com_inv
    
    def modularity_gain(self,node,neighbor):
        di = self.degree(node)
        #dj = self.degree(neighbor)

        com_index = self.com_inv[neighbor]
        members = self.com[com_index]
        shared_degree = 0
        dj = 0
        for member in members:
            dj+=self.degree(member)
            if member in self.G.neighbors(node):
                shared_degree +=2
        return 1/(2*self.m)*(shared_degree-self.res*di*dj/self.m)
    
    def passage(self):
        nodes = list(self.G.nodes())
        #random.seed(2)
        #random.shuffle(nodes)
        changes = 0
        for v in nodes:
            original = "original"
            #delete v from its community:
            com_index = self.com_inv[v]
            del self.com_inv[v]
            self.com[com_index].remove(v)
            original = com_index 
            #Find the neighbor with highest modularity gain
            #print("com_inv",com_inv)
            gains = {}
            visited_communities = set()
            for neighbor in self.G[v]:
                #Just in case the original graph has selfloops.
                if v==neighbor:
                    continue
                neighbors_com = self.com_inv[neighbor]
                if neighbors_com in visited_communities:
                    continue
                gains[self.modularity_gain(v,neighbor)] = neighbors_com
                visited_communities.add(neighbors_com)
            best_mod = max(gains.keys())
            closest_com = gains[best_mod]
            if best_mod<1e-07:
                com_index = original
                self.com[com_index].add(v)
                self.com_inv[v] = com_index
            else:
                com_index = closest_com
                # Add v to the same community as the closest_node
                self.com_inv[v]=com_index
                self.com[com_index].add(v)

            if com_index!=original:
                changes+=1
        print("changes",changes)
        if changes>0:
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
        for u, v, w in G.edges(data="shared_degree", default=2):
            c1 = com_inv[u]
            c2 = com_inv[v]
            new_weight = w
            if c1!=c2:
                if new_graph.has_edge(c1, c2):
                    new_weight += new_graph[c1][c2].get("shared_degree")
                new_graph.add_edge(c1, c2, shared_degree=new_weight)
        return new_graph
    

    def modularity_gain_hyper(self, hyper_graph, node, neighbor, com, com_inv):
        di = hyper_graph.nodes[node].get('total_degree')
        com_index = com_inv[neighbor]
        members = com[com_index]
        
        # Sum the total degrees of nodes in the community represented by neighbor
        dj = sum(hyper_graph.nodes[member].get('total_degree') for member in members)

        # Compute shared degree only for neighbors within the community
        shared_degree = sum(hyper_graph[node][member]['shared_degree'] for member in hyper_graph.neighbors(node) if member in members)

        return 1 / (2 * self.m) * (shared_degree - self.res*di * dj / self.m)

    """

    def modularity_gain_hyper(self,hyper_graph,node,neighbor,com,com_inv):
        di = hyper_graph.nodes[node].get('total_degree')
        dj = 0
        #di = hyper_graph[node][node]['shared_degree']
        #dj = hyper_graph[neighbor][neighbor]['shared_degree']
        dj = 0
        
        com_index = com_inv[neighbor]
        members = com[com_index]
        shared_degree = 0
        for member in members:
            dj+=hyper_graph.nodes[member].get('total_degree')
            if member in hyper_graph.neighbors(node):
                shared_degree +=hyper_graph[node][member]['shared_degree']
            #print("di,dj,shared_degree",di,dj,shared_degree)
        #print("shared_dergee",shared_degree)

        return 1/(2*self.m)*(shared_degree-di*dj/self.m)
    """

 
    def second_passage(self,hyper_graph,hyper_com,hyper_com_inv):
        changes = 0
        nodes = list(hyper_graph.nodes())
        #random.seed(2)
        #random.shuffle(nodes)
        for v in nodes:
            #delete v from its community:
            hyper_com_index = hyper_com_inv[v]
            del hyper_com_inv[v]
            hyper_com[hyper_com_index].remove(v)
            #To keep track of changes
            original = hyper_com_index  
            #print("hyper_com_inv after",hyper_com_inv)
            #print(hyper_com)
            #print("did it remove node",v,"?")
            #Find the neighbor with highest modularity gain
            #print("com_inv",com_inv)
            #print("for node",v, "there the neighbors:", list(hyper_graph.neighbors(v)))
            gains = {}
            visited_communities = set()
            for neighbor in hyper_graph.neighbors(v):
                #print("yes2")
                if v!=neighbor:
                    neighbor_com = hyper_com_inv[neighbor]
                    if neighbor_com in visited_communities:
                        continue
                    gains[self.modularity_gain_hyper(hyper_graph,v,neighbor,hyper_com,hyper_com_inv)]=neighbor_com
                    visited_communities.add(neighbor_com)           
            #print("gains",gains)
            best_mod = max(gains.keys())
            closest_com = gains[best_mod]
            if best_mod<1e-07:
                hyper_com_index = original
                hyper_com[hyper_com_index].add(v)
                hyper_com_inv[v] = hyper_com_index
            else:
                hyper_com_index = closest_com
                hyper_com_inv[v]=hyper_com_index
                hyper_com[hyper_com_index].add(v)
                
            #print(original,hyper_com_index)
            if hyper_com_index!=original:
                changes+=1
        print("changes",changes)
        if changes>=1:
            self.change = True

    
    def combine_com(self,com,hypercom):
        final_com = {}
        for hyper,hyper_val in hypercom.items():
            if len(hyper_val)==0:
                continue
            final_com[hyper] = {node for node_set in hyper_val for node in com[node_set]} # [item for sublist in nested_list for item in sublist]
        return(final_com)
    
    def remove_empty(self,com):
        new_com = {}
        new_com_inv = {}
        index = 0
        for old_index, nodes in com.items():
            if len(nodes)>0:
                new_com[index] = nodes
                for node in nodes:
                    new_com_inv[node] = index
                index+=1
        return(new_com,new_com_inv)
    

    def run(self,number_of_passages=2):
        print("passage 1")
        start_time = time.time()
        self.com,self.com_inv = self.init_dict(self.G)
        #print(self.com)
        while self.change==True:
            self.change = False
            print("start iteration")
            self.passage()
            #modularity = nx.community.modularity(self.G,list(self.com.values()))
            #print("modularity = ",modularity)
        self.com,self.com_inv = self.remove_empty(self.com)
        print("There were", len(self.com), "communities detected in passage 1.")
        #print("com_inv",self.com_inv)
        #print("com",self.com)
        first_modularity = nx.community.modularity(self.G,list(self.com.values()))
        print("modularity",first_modularity)
        time_step = time.time()
        print("end of passage 1",time_step-start_time)

        print("passage 2")
        print("creating hypergraph")
        hypergraph = self.generate_hyper(self.com,self.G,self.degree,self.com_inv)
        """ checking the hypergraph 
        labels = nx.get_edge_attributes(hypergraph,"shared_degree")
        nx.draw(hypergraph,with_labels=True)
        for node, attr in hypergraph.nodes(data=True):
            weight = attr['total_degree']
            print("node",node,"weight",weight)
        for u,v , attr in hypergraph.edges(data=True):
            weight = attr['shared_degree']
            print("node",(u,v),"weight",weight)

        """
        print("hypergraph created",time.time()-time_step)
        time_step = time.time()
        hyper_com, hyper_com_inv = self.init_dict(hypergraph)
        self.change=True
        mod=0
        while self.change==True:
            self.change=False
            print("start iteration")
            self.second_passage(hypergraph,hyper_com,hyper_com_inv)
            modularity = nx.community.modularity(hypergraph,list(hyper_com.values()))
            print("modularity = ",modularity)
            if modularity<mod:
                print("stopped")
                break
            mod = modularity
        print("The number of communities was reduced to ",len(hyper_com))
        print("hyper_com",hyper_com)        
        final_communities = self.combine_com(self.com,hyper_com)
        new_modularity = nx.community.modularity(self.G,list(final_communities.values()))
        print("new_modularity:",new_modularity)
        if (new_modularity-first_modularity)<0.01:
            if new_modularity<first_modularity:
                return self.com
            else:
                return final_communities
        print("end of passage 2",time.time()-time_step)
        time_step = time.time()
        
        print("passage 3")
        print("creating hypergraph")
        hypergraph = self.generate_hyper(hyper_com,hypergraph,hypergraph.degree,hyper_com_inv)
        """Checking hypergraph
        nx.draw(hypergraph,with_labels=True)
        for node, attr in hypergraph.nodes(data=True):
            weight = attr['total_degree']
            print("node",node,"weight",weight)
        for u,v , attr in hypergraph.edges(data=True):
            weight = attr['shared_degree']
            print("node",(u,v),"weight",weight)
        """

        hyper_hyper_com,hyper_hyper_com_inv = self.init_dict(hypergraph)
        self.change=True
        mod = 0
        while self.change==True:
            self.change = False
            print("start iteration")
            self.second_passage(hypergraph,hyper_hyper_com,hyper_hyper_com_inv)
            modularity = nx.community.modularity(hypergraph,list(hyper_hyper_com.values()))
            print("modularity = ",modularity)
            if modularity<mod:
                print("stopped")
                break
            mod = modularity
        print("The number of communities was reduced to ",len(hyper_hyper_com))
        old_modularity = new_modularity
        final_hyper_communities = self.combine_com(hyper_com,hyper_hyper_com)
        final_final_communities = self.combine_com(self.com,final_hyper_communities)
        new_modularity = nx.community.modularity(self.G,list(final_final_communities.values()))
        print("new_modularity:",new_modularity)
        if new_modularity<old_modularity:
            print("the old one was better")
            return final_communities
        


        print("passage 4")
        print("creating hypergraph")
        hypergraph = self.generate_hyper(hyper_com,hypergraph,hypergraph.degree,hyper_com_inv)
        """Checking hypergraph
        nx.draw(hypergraph,with_labels=True)
        for node, attr in hypergraph.nodes(data=True):
            weight = attr['total_degree']
            print("node",node,"weight",weight)
        for u,v , attr in hypergraph.edges(data=True):
            weight = attr['shared_degree']
            print("node",(u,v),"weight",weight)
        """

        hyper_hyper_hyper_com,hyper_hyper_hyper_com_inv = self.init_dict(hypergraph)
        self.change=True
        mod = 0
        while self.change==True:
            self.change = False
            print("start iteration")
            self.second_passage(hypergraph,hyper_hyper_hyper_com,hyper_hyper_hyper_com_inv)
            modularity = nx.community.modularity(hypergraph,list(hyper_hyper_hyper_com.values()))
            print("modularity = ",modularity)
            if modularity<mod:
                print("stopped")
                break
            mod = modularity
        print("The number of communities was reduced to ",len(hyper_hyper_hyper_com))
        old_modularity = new_modularity
        final_hyper_hyper_communities = self.combine_com(hyper_hyper_com,hyper_hyper_hyper_com)
        final_hyper_hyper_communities = self.combine_com(hyper_com,final_hyper_hyper_communities)
        final_final_final_communities = self.combine_com(self.com,final_hyper_communities)
        new_modularity = nx.community.modularity(self.G,list(final_final_final_communities.values()))
        print("new_modularity:",new_modularity)
        if new_modularity<old_modularity:
            print("the old one was better")
            return final_final_communities

        
        return final_final_final_communities
        

