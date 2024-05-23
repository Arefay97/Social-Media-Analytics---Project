import networkx as nx
import numpy as np
import random
import time

"""Make sure that the graph is connected."""
    
class Louvain_algo:
    def __init__(self,G,res=1):
        self.G = G
        self.m = G.number_of_edges()
        self.com = {}
        self.com_inv = {}
        self.degree = G.degree()
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
    
    def random_init(self,G):
        com_inv = {}
        com = {}
        nodes = G.nodes        
        length = len(nodes)
        for node in nodes:
            community_id = random.randint(0,length - 1)
            com_inv[node]=community_id
            if community_id in com.keys():
                com[community_id].add(node)
            else:
                com[community_id] = {node}   
        return com,com_inv 

    def neighbor_based_init(self,G):
        com_inv = {}
        com = {}
        for node in G.nodes:
            # Select a random neighbor
            selected_neighbor = random.choice(list(G.neighbors(node)))

            # Check if the selected neighbor has been assigned to a community
            if selected_neighbor in com_inv:
                community_id = com_inv[selected_neighbor]
                com[community_id].add(node)
            else:
                community_id = len(com)
                com[community_id] = {node}

            com_inv[node] = community_id

        return com, com_inv

    
    def modularity_gain(self,node,com_index):
        di = self.degree(node)
        #dj = self.degree(neighbor)
        members = self.com[com_index]
        dj = sum(self.degree(member) for member in members)
        shared_degree = sum(2 for neighbor in self.G.neighbors(node) if neighbor in members)

        return 1/(2*self.m)*(shared_degree-di*dj/self.m)
    
    
    def modularity_gain2(self,node,com_index,mod_before):
        #add node to test community
        self.com[com_index].add(node)
        new_mod = nx.community.modularity(self.G,list(self.com.values()))
        self.com[com_index].remove(node)
        #print("new",new_mod)
        #print("old",mod_before)
        return new_mod-mod_before


    
    def passage(self):
        nodes = list(self.G.nodes())
        nodes.sort()
        self.change = True
        while self.change==True:
            changes = 0
            for v in nodes:
                #delete v from its community:
                com_index = self.com_inv[v]
                del self.com_inv[v]
                self.com[com_index].remove(v)
                original = com_index 

                #Find the neighbor with highest modularity gain
                gains = {}
                visited_communities = set()
                neighbors = list(self.G[v])
                neighbors.sort()
                for neighbor in neighbors:
                    #Just in case the original graph has selfloops.
                    if v==neighbor:
                        continue
                    neighbors_com = self.com_inv[neighbor]
                    if neighbors_com in visited_communities:
                        continue
                    mod_gain = self.modularity_gain(v,neighbors_com)
                    if mod_gain not in gains.keys():
                        gains[mod_gain] = neighbors_com
            
                    visited_communities.add(neighbors_com)
                
                best_mod = max(gains.keys())
                closest_com = gains[best_mod]
                if best_mod<=1e-07:
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
            #print("changes",changes)
            if changes>0:
                self.change = True
            else:
                self.change = False

    
    def generate_hyper(self, com,G,com_inv):
        """Generates the hypergraph. The total degree is stored in a node label 'total_degree'.
        The shared edges is stored in 'shared_degree' as a weight on the edges.

        First filter out the communities which are empyt. Then create nodes for each community.
        Then iterate over the edges of original graph to get the weight edges.
        """
        new_graph = nx.Graph()
        total_degrees = {}
        #
        keys_to_delete = []
        for community, members in com.items():
            if len(members)==0:
                keys_to_delete.append(community)
        for i in keys_to_delete:
            del com[i]

    
        for community, members in com.items():
            new_graph.add_node(community)
            total_degrees[community] = sum(G.nodes[node].get('total_degree') for node in members)
        nx.set_node_attributes(new_graph, total_degrees, 'total_degree')
        # Create the combined edges from the individual old edges.
        for u, v, w in G.edges(data="shared_degree", default=1):
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

        return 1 / (2 * self.m) * (2*shared_degree - di * dj / self.m)

 
    def second_passage(self,hyper_graph,hyper_com,hyper_com_inv):
        
        nodes = list(hyper_graph.nodes())
        self.change = True
        iteration = 0
        while self.change == True and iteration >= 0:
            changes = 0
            for v in nodes:
                #delete v from its community:
                hyper_com_index = hyper_com_inv[v]
                del hyper_com_inv[v]
                hyper_com[hyper_com_index].remove(v)
                #To keep track of changes
                original = hyper_com_index  

                #Calculate modularity gain for all the neighbor's communities. Visisted set is to avoid calculating twice.
                gains = {}
                visited_communities = set()
                for neighbor in hyper_graph.neighbors(v):
                    if v!=neighbor:
                        neighbor_com = hyper_com_inv[neighbor]
                        if neighbor_com in visited_communities:
                            continue
                        gains[self.modularity_gain_hyper(hyper_graph,v,neighbor,hyper_com,hyper_com_inv)]=neighbor_com
                        visited_communities.add(neighbor_com)           
                
                #Add the node v to the community with the highest modularity gain.
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


                if hyper_com_index!=original:
                    changes+=1
            """
            current_modularity = nx.community.modularity(hyper_graph, list(hyper_com.values()))
            if iteration > 0:
                modularity_change = current_modularity - previous_modularity

            previous_modularity = current_modularity

            print("mod inside passage2",current_modularity)
            """
            #print("changes",changes)
            iteration+=1
            if changes>0:
                self.change = True
            else:
                self.change = False
        return hyper_com, hyper_com_inv

    
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
    
    def recursive_passage(self,G,com,com_inv):
        before_modularity = nx.community.modularity(G,list(com.values()))
        #print("before",before_modularity)
        hypergraph = self.generate_hyper(com,G,com_inv)
        hyper_com, hyper_com_inv = self.init_dict(hypergraph)
        hyper_com, hyper_com_inv = self.second_passage(hypergraph,hyper_com,hyper_com_inv)
        final = self.combine_com(com,hyper_com)
        after_modularity = nx.community.modularity(G,list(final.values()))
        #print("after",after_modularity)
        hyper_modularity = nx.community.modularity(hypergraph,list(hyper_com.values()))
        #print("mod",hyper_modularity)
        #print("the number of communities is",sum(1 for community in hyper_com.values() if len(community)>0))
        if ((after_modularity -before_modularity)<= 1e-07 ):# or hyper_modularity<1e-07:# 
            return final
        else:
            from_before = self.recursive_passage(hypergraph,hyper_com,hyper_com_inv)
            final = self.combine_com(com,from_before)
            return final

    

    def run(self):
        nx.set_node_attributes(self.G, dict(self.G.degree()), 'total_degree')
        self.com,self.com_inv = self.init_dict(self.G)
        self.passage()
        final = self.recursive_passage(self.G,self.com,self.com_inv)

        return final
        



    def run2(self):
        print("passage 1")
        start_time = time.time()
        self.com,self.com_inv = self.init_dict(self.G)
        print(self.com)
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
        mod=0.1
        while self.change==True:
            self.change=False
            print("start iteration")
            self.second_passage(hypergraph,hyper_com,hyper_com_inv)
            final_communities = self.combine_com(self.com,hyper_com)
            #actual_modularity = nx.community.modularity(self.G,list(final_communities.values()))
            #print("actual_modularity = ",actual_modularity)
            modularity = nx.community.modularity(hypergraph,list(hyper_com.values()))
            #print("modularity = ",modularity)
            if modularity<mod:
                print("stopped")
                break
                #hyper_com, hyper_com_inv = self.neighbor_based_init(hypergraph)
                
            mod = modularity
        print("The number of communities was reduced to ",len(hyper_com))
        #print("hyper_com",hyper_com)        
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
        mod = 0.1
        while self.change==True:
            self.change = False
            print("start iteration")
            self.second_passage(hypergraph,hyper_hyper_com,hyper_hyper_com_inv)
            modularity = nx.community.modularity(hypergraph,list(hyper_hyper_com.values()))
            print("modularity = ",modularity)
            final_hyper_communities = self.combine_com(hyper_com,hyper_hyper_com)
            final_final_communities = self.combine_com(self.com,final_hyper_communities)
            actual_modularity = nx.community.modularity(self.G,list(final_final_communities.values()))
            print("actual_modularity = ",actual_modularity)
            #if modularity<mod:
             #   print("stopped")
              #  break
                #hyper_hyper_com,hyper_hyper_com_inv = self.neighbor_based_init(hypergraph)
            mod = modularity
        print("The number of communities was reduced to ",len(hyper_hyper_com))
        old_modularity = new_modularity
        final_hyper_communities = self.combine_com(hyper_com,hyper_hyper_com)
        final_final_communities = self.combine_com(self.com,final_hyper_communities)
        new_modularity = nx.community.modularity(self.G,list(final_final_communities.values()))
        print("new_modularity:",new_modularity)
        if new_modularity-old_modularity<0.01:
            if new_modularity<old_modularity:
                print("the old one was better")
                return final_communities
            else:
                return final_final_communities
        


        print("passage 4")
        print("creating hypergraph")
        hypergraph = self.generate_hyper(hyper_hyper_com,hypergraph,hypergraph.degree,hyper_hyper_com_inv)
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
        

