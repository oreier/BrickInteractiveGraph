# /// script
# dependencies = [
#   "rdflib",
#   "pyvis",
#   "json",
#   "collections",
#   "random"
# ]
# ///

import rdflib
from pyvis.network import Network
import json

from collections import defaultdict
import random

# Load configuration from JSON file
with open("config.json") as config_file:
    config = json.load(config_file)

# Use config values
rdf_file = config.get("rdf_file")
starting_keywords = config.get("starting_node_keywords")

# Initialize RDF graph
g = rdflib.Graph()

type_map = {}  # node_id → type_label
type_colors = {}  # type_label → hex color

# Load the RDF data (replace with your actual TTL file)

g.parse(rdf_file, format="turtle")

g.bind("bldg1", "http://buildsys.org/ontologies/bldg1#")
g.bind("brick", "https://brickschema.org/schema/Brick#")
g.bind("ns4", "http://buildsys.org/ontologies/bldg1#bldg1.CHW.Pump1_Start/")
g.bind("owl", "http://www.w3.org/2002/07/owl#")
g.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
g.bind("ref", "https://brickschema.org/schema/Brick/ref#")
g.bind("unit", "http://qudt.org/vocab/unit/")

# Initialize Pyvis network
net = Network(directed=True)

# SPARQL query to extract main nodes and their relationships
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

def rename_node(node):
    if isinstance(node, rdflib.term.URIRef):
        return g.qname(node)  # Shorten the URI for display
    elif isinstance(node, rdflib.term.Literal):
        return f"{node} ({node.datatype})"
    else:
        return str(node)

def rename_predicate(predicate):
    if isinstance(predicate, rdflib.term.URIRef):
        return g.qname(predicate)
    else:
        return str(predicate)
    
def inital_nodes(node_label):
    # keywords = ['FLOOR']
    result = any(keyword in node_label.upper() for keyword in starting_keywords)
    if result:
        print(f"✔️ Matched: {node_label}")
    return result

def get_color_for_type(type_label):
    if type_label not in type_colors:
        # Generate soft pastel color
        r = lambda: random.randint(100, 200)
        type_colors[type_label] = f'#{r():02x}{r():02x}{r():02x}'
    return type_colors[type_label]

def is_class_type(type_label):
    class_keywords = ['owl']  
    return any(keyword.lower() in type_label.lower() for keyword in class_keywords)
   

# Build type_map: node → type
type_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX brick: <https://brickschema.org/schema/Brick#>
SELECT DISTINCT ?subject ?type
WHERE {
    ?subject rdf:type ?type .
}
"""

for row in g.query(type_query):
    subject = rename_node(row['subject'])
    type_label = rename_node(row['type'])
    type_map[subject] = type_label


# Add all nodes with visibility tags
for row in results:
    for node in [row['subject'], row['object']]:
        if isinstance(node, rdflib.term.URIRef):
            node_label = rename_node(node)
            if node_label not in visited_nodes:
                node_uri = str(node)
                is_main = inital_nodes(node_label)
                node_type = type_map.get(node_label, None)
                net.add_node(
                    node_label,
                    label=node_label,
                    title=node_type,
                    uri=node_uri,
                    shape="dot",
                    color = get_color_for_type(node_type) if node_type else "#C0C0C0",
                    hidden=not is_main
                )
                visited_nodes.add(node_label)

# Add all edges (hide ones between hidden nodes)
for row in results:
    subject_label = rename_node(row['subject'])
    object_label = rename_node(row['object'])
    predicate_name = rename_predicate(row['predicate'])

    # Determine visibility from current node properties
    if isinstance(row['subject'], rdflib.term.URIRef) and isinstance(row['object'], rdflib.term.URIRef):
        subject_node = net.get_node(subject_label)
        object_node = net.get_node(object_label)
        hidden = subject_node.get('hidden', False) or object_node.get('hidden', False)

        net.add_edge(subject_label, object_label, label=predicate_name, hidden=hidden)


print(f"Total number of nodes: {len(visited_nodes)}")

net.force_atlas_2based()

network_data = net.get_network_data()
nodes = network_data[0]
edges = network_data[1]

# Convert nodes and edges to JSON strings
nodes_json = json.dumps(nodes)
edges_json = json.dumps(edges)

# Generate and save the graph to an HTML file
net.show('ui3.html', notebook=False)

# HTML content embedding
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interactive Building Graph</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; margin: 0; background-color: #f7f9fb}}

        header {{
            background: linear-gradient(to right, #0062ff, #00c9a7);
            color: white;
            padding: 20px 40px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        header h1 {{
            margin: 0;
            font-size: 1.8rem;
            font-weight: 600;
        }}

        header .subtitle {{
            font-size: 0.95rem;
            font-weight: 400;
            opacity: 0.9;
        }}

        #graph-container {{ height: 800px; }}
        #query-container {{ margin-top: 20px; }}

        /* Style for the sidebar */
        #sidebar {{
            position: fixed;
            top: 0;
            right: -400px;
            width: 350px;
            height: 100%;
            background-color: white;
            box-shadow: -2px 0 8px rgba(0, 0, 0, 0.2);
            transition: right 0.3s ease;
            padding: 20px;
            z-index: 999;
            overflow-y: auto;
        }}

        #sidebar.open {{
            right: 0;
        }}

        .sidebar-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}

        .sidebar-header h2 {{
            margin: 0;
            font-size: 1.4rem;
        }}

        .sidebar-header .close-btn {{
            font-size: 1.5rem;
            cursor: pointer;
        }}

        .connections-list {{
            margin-top: 10px;
            font-size: 0.95rem;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
            word-break: break-word;
        }}

        .connection-item {{
            padding: 6px 8px;
            border-radius: 6px;
            background-color: #f1f5f9;
            margin-bottom: 6px;
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 6px;
        }}

        .relation {{
            font-weight: 600;
            color: #0062ff;
            white-space: nowrap;
        }}

        .arrow {{
            font-weight: bold;
            color: #555;
        }}

        .target {{
            font-weight: 500;
            color: #222;
        }}

        .hidden-tag {{
            font-style: italic;
            font-size: 0.85rem;
            color: #999;
        }}
        
    </style>
</head>
<body>
    <header>
        <div>
            <h1>Building Ontology Viewer</h1>
            <div class="subtitle">Explore relationships between building components</div>
        </div>
    </header>

    <div style="padding: 20px; background-color: #f7f9fb;">
        <input id="search-input" type="text" placeholder="Search for a node..." 
            style="padding: 10px; width: 300px; font-size: 1rem; border-radius: 4px; border: 1px solid #ccc;" />
        <button onclick="searchNode()" 
                style="padding: 10px 15px; font-size: 1rem; border: none; background-color: #0062ff; color: white; border-radius: 4px; margin-left: 10px;">
            Search
        </button>
    </div>

    <button onclick="openSettings()" 
        style="margin-left: 20px; padding: 10px 15px; font-size: 1rem; background-color: #ccc; border: none; border-radius: 4px;">
        ⚙️ Settings
    </button>


    <!-- MENU SCREEN -->
    <div id="menu-screen" style="position: absolute; width: 100%; height: 100%; background: #f7f9fb; z-index: 9999; display: flex; flex-direction: column; justify-content: center; align-items: center;">
        <h2>Select Graph Settings</h2>


        <label style="margin-top: 20px;">Color Scheme:</label>
        <div>
            <label><input type="radio" name="color-mode" value="type" checked /> Default by Type</label><br />
            <label><input type="radio" name="color-mode" value="class-instance" /> Class vs Instance</label>
        </div>

        <button onclick="initializeGraph()" style="margin-top: 30px; padding: 10px 20px; font-size: 1rem;">Load Graph</button>
    </div>



    <div id="graph-container"></div>

    <div id="sidebar">
        <div class="sidebar-header">
            <h2 id="sidebar-title">Node Info</h2>
            <span class="close-btn" onclick="closeSidebar()">×</span>
        </div>
        <div id="sidebar-content">
            <p>Select a node to see details here.</p>
        </div>
    </div>


    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"></script>
    <script>
        var container = document.getElementById('graph-container');
        let currentColorMode = "type";  

        var allNodes = {nodes_json};
        var allEdges = {edges_json};

        // Initialize graph with only visible nodes/edges
        var visibleNodes = allNodes.filter(n => !n.hidden);
        var visibleEdges = allEdges.filter(e => !e.hidden);

        var data = {{
            nodes: new vis.DataSet(visibleNodes),
            edges: new vis.DataSet(visibleEdges)
        }};

        
        var options = {{
            "clickToUse": true,
            "physics": {{
                "enabled": true,
                "solver": "forceAtlas2Based", // This keeps the force-directed layout
                "timestep": 0.5, // Controls speed of the physics simulation
                "minVelocity": 0.1
            }},
            "interaction": {{
                "dragNodes": true,   // Enable dragging nodes
                "zoomView": true,    // Enable zooming
                "tooltipDelay": 200  // Tooltip delay for hover effect
            }},
            "layout": {{
                "improvedLayout": false
            }}
        }};
        
        var network = new vis.Network(container, data, options);

        function initializeGraph() {{

            // Get selected color mode
            const selectedColorMode = document.querySelector('input[name="color-mode"]:checked').value;


            if (selectedColorMode !== currentColorMode) {{
                currentColorMode = selectedColorMode;

                // Re-apply the selected color mode
                const useClassInstanceMode = (currentColorMode === "class-instance");
                updateNodeColors(useClassInstanceMode);
            }}

            // Remove the menu screen
            document.getElementById("menu-screen").style.display = "none";

        }}
        window.initializeGraph = initializeGraph;

        function openSettings() {{
            // Show the menu screen
            document.getElementById("menu-screen").style.display = "flex";
        }}


        function revealNeighbors(nodeId) {{
            let revealed = [];

            allEdges.forEach(function(edge) {{
                if ((edge.from === nodeId || edge.to === nodeId) && edge.hidden) {{
                    edge.hidden = false;

                    // Reveal the connected node
                    let neighborId = edge.from === nodeId ? edge.to : edge.from;

                    let neighborNode = allNodes.find(n => n.id === neighborId);
                    if (neighborNode && neighborNode.hidden) {{
                        neighborNode.hidden = false;
                        revealed.push(neighborId);
                    }}
                }}
            }});

            // Update dataset
            let nodesToAdd = [];
            let edgesToAdd = [];

            allNodes.forEach(n => {{
                if (!n.hidden) nodesToAdd.push(n);
            }});

            allEdges.forEach(e => {{
                if (!e.hidden) edgesToAdd.push(e);
            }});

            network.body.data.nodes.update(nodesToAdd);
            network.body.data.edges.update(edgesToAdd);

            return revealed;
        }}

        function collapseNeighbors(nodeId) {{
            let toHideNodes = new Set();
            let toHideEdges = [];

            // Find neighbors
            allEdges.forEach(edge => {{
                if (edge.from === nodeId || edge.to === nodeId) {{
                    const neighborId = edge.from === nodeId ? edge.to : edge.from;

                    // Check if that neighbor is only connected to this node (i.e., safe to collapse)
                    const connections = allEdges.filter(e =>
                        (e.from === neighborId || e.to === neighborId) && 
                        !e.hidden && (e.from !== nodeId && e.to !== nodeId)
                    );

                    if (connections.length === 0) {{
                        // Hide edge
                        edge.hidden = true;
                        toHideEdges.push(edge);

                        // Hide neighbor node
                        let neighborNode = allNodes.find(n => n.id === neighborId);
                        if (neighborNode) {{
                            neighborNode.hidden = true;
                            toHideNodes.add(neighborNode);
                        }}
                    }}
                }}
            }});

            // Update dataset
            network.body.data.nodes.update([...toHideNodes]);
            network.body.data.edges.update(toHideEdges);

            console.log(`Collapsed neighbors for node: ${{nodeId}}`);
        }}

        function showSidebar(node) {{
            var content = `<strong>Label:</strong> ${{node.label}}<br>`;
            content += `<strong>URI:</strong> ${node.title}<br><br>`;

           // All connections (even hidden ones)
            var relatedEdges = allEdges.filter(e => e.from === node.id || e.to === node.id);

           if (relatedEdges.length > 0) {{
                content += `<strong>Connections:</strong><div class="connections-list">`;

                relatedEdges.forEach(edge => {{
                    var neighborId = edge.from === node.id ? edge.to : edge.from;
                    var neighborNode = allNodes.find(n => n.id === neighborId);
                    var neighborLabel = neighborNode?.label || "[Unknown]";
                    var relation = edge.label || "—";
                    var hiddenTag = neighborNode?.hidden ? "<span class='hidden-tag'>(hidden)</span>" : "";

                    content += `
                        <div class="connection-item">
                            <span class="relation">${{relation}}</span>
                            <span class="arrow">→</span>
                            <span class="target">${{neighborLabel}}</span>
                            ${{hiddenTag}}
                        </div>
                    `;
                }});

                content += `</div>`;
            }} else {{
                content += `<em>No connections found.</em>`;
            }}


            document.getElementById('sidebar-title').textContent = node.label;
            document.getElementById('sidebar-content').innerHTML = content;

            document.getElementById('sidebar').classList.add('open');
        }}

        function closeSidebar() {{
            document.getElementById('sidebar').classList.remove('open');
        }}

        function searchNode() {{
            var input = document.getElementById("search-input").value.trim().toLowerCase();
            if (!input) return;

            // Try to find node by label or ID (case-insensitive)
            var foundNode = allNodes.find(node => 
                node.label.toLowerCase().includes(input) || 
                (node.id && node.id.toLowerCase().includes(input))
            );

            if (foundNode) {{
                // If node is hidden, reveal it and its connections
                if (foundNode.hidden) {{
                    foundNode.hidden = false;
                    revealNeighbors(foundNode.id);
                    network.body.data.nodes.update(foundNode);
                }}

                // Zoom and focus on the node
                network.focus(foundNode.id, {{
                    scale: 1.5,
                    animation: {{
                        duration: 1000,
                        easingFunction: "easeInOutQuad"
                    }}
                }});

                showSidebar(foundNode);  // Also show sidebar info
            }} else {{
                alert("No node found with that name.");
            }}
        }} 

        // Function to update node colors based on the mode
        function updateNodeColors(useClassInstanceMode) {{
            allNodes.forEach(function(node) {{
                const nodeURI = node.uri|| "";
                const nodeType = node.title || "";

                if (useClassInstanceMode) {{
                    node.color = nodeURI.includes("owl") ? "#4A90E2" : "#7ED957";  // Class vs Instance
                }} else {{
                    // Type mode: assign consistent pastel color per type
                    const hash = [...nodeType].reduce((acc, char) => acc + char.charCodeAt(0), 0);
                    const r = 100 + (hash * 53 % 100);
                    const g = 100 + (hash * 97 % 100);
                    const b = 100 + (hash * 29 % 100);
                    node.color = `rgb(${{r}}, ${{g}}, ${{b}})`;
                }}
            }});

            network.body.data.nodes.update(allNodes);
        }};

        // Add a click event listener 
        let clickTimeout = null;

        network.on("click", function(event) {{
            if (clickTimeout) {{
                clearTimeout(clickTimeout);
                clickTimeout = null;
            }}

            const clickedNode = event.nodes[0];
            if (clickedNode) {{
                // Delay the single click action to distinguish it from double click
                clickTimeout = setTimeout(() => {{
                    const node = network.body.data.nodes.get(clickedNode);
                    showSidebar(node);
                }}, 200); // 200ms delay to wait for possible double click
            }}
        }});

        network.on("doubleClick", function(event) {{
            if (clickTimeout) {{
                clearTimeout(clickTimeout); // Cancel the single-click
                clickTimeout = null;
            }}

            const clickedNode = event.nodes[0];
            if (clickedNode) {{
                const revealed = revealNeighbors(clickedNode);
                if (revealed.length === 0) {{ 
                    collapseNeighbors(clickedNode);
                }} else {{
                    console.log("Expanded neighbors: " + revealed.join(", "));
                }}
            }}
        }});


    </script>
</body>
</html>
"""

# Save the HTML content to a file
with open("ui3.html", "w", encoding="utf-8") as f:
    f.write(html_content)