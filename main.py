from flask import Flask, request, render_template
import networkx as nx
import random

app = Flask(__name__)

# Step 1: Create a graph structure
G = nx.DiGraph()

# Step 2: Define symbolic thought nodes with categories
nodes = {
    "Fire": {"type": "element", "categories": ["heat", "danger"]},
    "Heat": {"type": "effect", "categories": ["comfort", "danger"]},
    "Burn": {"type": "action", "categories": ["danger"]},
    "Destruction": {"type": "consequence", "categories": ["danger"]},
    "Warmth": {"type": "benefit", "categories": ["comfort"]},
    "Lava": {"type": "similar", "categories": ["heat", "danger"]},
    "Water": {"type": "opposite", "categories": ["calm", "comfort"]}
}

# Add nodes to the graph
for node, attributes in nodes.items():
    G.add_node(node, **attributes)

# Step 3: Define weighted dynamic relationships between thoughts
edges = [
    ("Fire", "Heat", 0.8),
    ("Fire", "Burn", 0.7),
    ("Fire", "Destruction", 0.6),
    ("Fire", "Warmth", 0.5),
    ("Fire", "Lava", 0.7),
    ("Fire", "Water", 0.2),  # Weak connection, opposite concept
    ("Heat", "Warmth", 0.9),
    ("Heat", "Burn", 0.8),
    ("Burn", "Destruction", 0.9),
    ("Water", "Fire", 0.1)  # Weak reverse connection
]

# Add weighted edges to the graph
for source, target, weight in edges:
    G.add_edge(source, target, weight=weight)

# Step 4: Define a function to navigate thoughts dynamically
def navigate_thoughts(start_node, context="default"):
    start_node = start_node.capitalize()  # Ensures first letter is uppercase
    if start_node not in G:
        return f"'{start_node}' not found in thought network."

    thought_paths = list(G[start_node].items())
    
    # Adjust weights dynamically based on context
    adjusted_weights = {target: data["weight"] for target, data in thought_paths}
    for target in adjusted_weights:
        categories = G.nodes[target].get("categories", [])
        if context == "danger" and "danger" in categories:
            adjusted_weights[target] *= 1.2  # Increase weight for danger-related thoughts
        elif context == "comfort" and "comfort" in categories:
            adjusted_weights[target] *= 1.2  # Increase weight for comfort-related thoughts

    # Normalize weights to create probabilities
    total_weight = sum(adjusted_weights.values())
    probabilities = {target: weight / total_weight for target, weight in adjusted_weights.items()}

    # Select a thought based on probabilities
    selected_thoughts = random.choices(list(probabilities.keys()), weights=probabilities.values(), k=len(probabilities))

    result = [f"{target} (weight: {adjusted_weights[target]:.2f})" for target in selected_thoughts]
    
    return f"Thought paths from '{start_node}' in context '{context}':\n" + "\n".join(result)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_node = request.form['start_node']
        context = request.form['context']
        result = navigate_thoughts(start_node, context)
        return render_template('index.html', result=result)
    return render_template('index.html', result='')

if __name__ == '__main__':
    app.run(debug=True)