import rdflib
import networkx as nx
import matplotlib.pyplot as plt

# Create a Graph
g = rdflib.Graph()

# Load the Turtle file
file = 'bldg1.ttl'

# Parse the Turtle file into the RDF graph
g.parse(file, format="turtle")
#binding namespace 
g.bind("bldg1", "http://buildsys.org/ontologies/bldg1#")

# Create a networkx graph
G = nx.DiGraph()  # Directed graph to represent the relationships

# Query to extract AHU details and their relationships
query = """
    SELECT ?ahu ?feeds ?points ?fedby
    WHERE {
        ?ahu a brick:Air_Handler_Unit .
        OPTIONAL { ?ahu brick:feeds ?feeds . }
        OPTIONAL { ?ahu brick:hasPoint ?points . }
        OPTIONAL { ?ahu brick:isFedBy ?fedby . }
    }
"""

results = g.query(query)

# Add nodes and edges to the networkx graph based on the results
for row in results:
    unit = str(row.ahu)  
    feeds = str(row.feeds) if row.feeds else None  # Feeds can be None
    # 
    feeds = g.qname(row.feeds) if row.feeds else None  
    points = str(row.points) if row.points else None  # Points can be None
    fedby = str(row.fedby) if row.fedby else None  # FedBy can be None

    # Add  node in the graph
    G.add_node(unit, type="Air Handler Unit")
    #edges
    if feeds:
        G.add_edge(unit, feeds, relationship="feeds")
    if points:
        G.add_edge(unit, points, relationship="hasPoint")
    if fedby:
        G.add_edge(fedby, unit, relationship="isFedBy")

# Visualization
plt.figure(figsize=(12, 12))  
pos = nx.spring_layout(G, seed=42, k=0.5) 
nx.draw(G, pos, with_labels=True, node_size=3000, node_color="lightblue", font_size=10, font_weight='bold', edge_color="gray")

edge_labels = nx.get_edge_attributes(G, 'relationship')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)

plt.gca().set_aspect('equal', adjustable='box')

plt.show()
