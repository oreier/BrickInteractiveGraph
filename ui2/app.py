import rdflib
from pyvis.network import Network
import json
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

# Initialize RDF graph
g = rdflib.Graph()

# Load the RDF data (replace with your actual TTL file)
file = 'bldg1.ttl'
g.parse(file, format="turtle")

g.bind("bldg1", "http://buildsys.org/ontologies/bldg1#")
g.bind("brick", "https://brickschema.org/schema/Brick#")
g.bind("ns4", "http://buildsys.org/ontologies/bldg1#bldg1.CHW.Pump1_Start/")
g.bind("owl", "http://www.w3.org/2002/07/owl#")
g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
g.bind("ref", "https://brickschema.org/schema/Brick/ref#")
g.bind("unit", "http://qudt.org/vocab/unit/")

# Initialize Pyvis network
net = Network(directed=True)

query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX brick: <https://brickschema.org/schema/Brick#>
    SELECT DISTINCT ?subject ?predicate ?object
    WHERE {
        ?subject ?predicate ?object .
        FILTER (?subject != ?object)  # Exclude self-referencing 
    }
"""

# Execute the query to get nodes
results = g.query(query)

# Add nodes to the network 
visited_nodes = set()

for row in results:
    # subject_name = str(row['subject'])
    # object_name = str(row['object'])

    # compact_subject = g.qname(subject_name)
    # compact_object = g.qname(object_name)
    compact_subject = str(row['subject'])
    compact_object = str(row['object'])
    
    # Add node if it hasn't been added before
    if compact_subject not in visited_nodes:
        net.add_node(compact_subject, title=compact_subject, label=compact_subject)  
        visited_nodes.add(compact_subject)
    if compact_object not in visited_nodes:
        net.add_node(compact_object, title=compact_object, label=compact_object) 
        visited_nodes.add(compact_object)

for row in results:
    subject_name = str(row['subject'])
    predicate_name = str(row['predicate'])
    object_name = str(row['object'])
    
    # Add edge between the nodes
    net.add_edge(subject_name, object_name, label=predicate_name)

print(f"Total number of nodes: {len(visited_nodes)}")

network_data = net.get_network_data()
nodes = network_data[0]
edges = network_data[1]

# Convert nodes and edges to JSON strings
nodes_json = json.dumps(nodes)
edges_json = json.dumps(edges)

# define the route to serve the HTML page
@app.route("/")
def index():
    nodes = []
    edges = []
    
    for row in results:
        subject = str(row['subject'])
        object = str(row['object'])
        
        if subject not in [node['id'] for node in nodes]:
            nodes.append({'id': subject, 'label': subject})
        if object not in [node['id'] for node in nodes]:
            nodes.append({'id': object, 'label': object})
        
        # Add edges
        edges.append({'from': subject, 'to': object, 'label': str(row['predicate'])})
    
    # Convert to JSON
    nodes_json = json.dumps(nodes)
    edges_json = json.dumps(edges)

    #print(f"nodes_json: {nodes_json}")
    #print(f"edges_json: {edges_json}")
    
    return render_template("interactive_building_graph.html", 
                           nodes_json=nodes_json, 
                           edges_json=edges_json)

# Define the route to handle SPARQL queries
@app.route("/execute_query", methods=["POST"])
def execute_query():
    query = request.json.get('query')
    
    try:
        results = g.query(query)
        result_list = [{'subject': str(row['subject']), 'predicate': str(row['predicate']), 'object': str(row['object'])} for row in results]
        return jsonify({'results': result_list})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == "__main__":
    app.run(debug=True)
