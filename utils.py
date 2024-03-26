#importing important liberaries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from py2neo import Graph, Node, Relationship,DatabaseError
import time




################################Utilities Function start here############################

def Load_data (nodesPath , edgesPath):
    '''Function Description'''


    nodes = pd.read_csv(nodesPath)
    edges = pd.read_csv(edgesPath)
    
    return nodes,edges



def Create_Graph(nodes , edges):
    '''Function Description'''
    G = nx.Graph()
    # Adding nodes to the graph
    for _, row in nodes.iterrows():
        node_id = row['id'] 
        features = {key: value for key, value in row.items() if key != 'id'}  # Exclude the ID column
        G.add_node(node_id, **features)

    # Adding edges to the graph
    for _, row in edges.iterrows():
        source = row['source']  # Assuming 'source' column contains the source node ID
        target = row['target']  # Assuming 'target' column contains the target node ID
        #We can add more features if the edges have features
        G.add_edge(source, target)
    
    #Return the constructed Networkx Graph
    return G
    
def get_node_features(graph, node_number):
    '''Function Description'''

    if node_number in graph.nodes():
        return graph.nodes[node_number]
    else:
        return None
        
def Load_to_neo4j(URI, userName, passWord, G):

    # Connect to the Neo4j database
    graph = Graph(URI, auth=(userName, passWord))


    try:
        # Run a simple Cypher query to retrieve data from the database
        result = graph.run("MATCH (n) RETURN count(n) AS node_count")

        # Extract and print the result
        for record in result:
            node_count = record["node_count"]
            print(f"Connected to Neo4j. Found {node_count} nodes in the database.")

    except DatabaseError as e:
        print("Failed to connect to Neo4j:", e)

    # Convert NetworkX graph to a dictionary
    data = nx.readwrite.json_graph.node_link_data(G)

    # Iterate over nodes in the NetworkX graph
    for node_id, node_attrs in G.nodes(data=True):
        '''Function Description'''

        # Features extractio
        facebook_id = node_attrs.get('facebook_id', None)
        #page name causes a proplem with specific page name so I commented it till I fix it
        #page_name = node_attrs.get('page_name', None)
        page_type = node_attrs.get('page_type', None)
        #degree_centrality = node_attrs.get('degree_centrality', None)

        '''Create if the nodes aren't created already in the Graph DB, or update 
        ,if the nodes are already in the graph, nodes in Neo4j with the extracted features.'''
            
        query = f"""
        MERGE (n:Node {{id: '{node_id}'}})
        SET n.facebook_id = '{facebook_id}',
            n.page_type = '{page_type}'
        """
        graph.run(query)
        
        #Add the edges of its neighbor
        neighbors = list(G[node_id])
        #print(neighbors)
        for neighbor in neighbors:
            edges_query = f"""
            MATCH (n:Node {{id: '{node_id}'}}), (m:Node {{id: '{neighbor}'}})
            MERGE (n)-[:LINKED]-> (m)
            MERGE (n)<-[:LINKED]-(m)
            """
            graph.run(edges_query)

def Similarity_between_nodes(G):
    '''Function description'''

    