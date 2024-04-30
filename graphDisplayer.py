from pyvis.network import Network

class Edge:
    def __init__(self):
        self.src = 0
        self.dest = 0
        self.weight = 0
        self.color = ""
    def __str__(self):
        return f"src: {self.src}, dest: {self.dest}, weight: {self.weight}, color: {self.color}"
    
class Node:
    def __init__(self):
        self.name = 0
        self.color = ""
    def __str__(self):
        return f"name: {self.name}, color: {self.color}"

def display_graph(nodes: list[Node],edges: list[Edge]):
    nt = Network(notebook=True,directed=True)
    for node in nodes: 
        nt.add_node(node.name,color=node.color)
    for edge in edges:  
        # print(edge)
        nt.add_edge(edge.src,edge.dest,color=edge.color,label=str(edge.weight))
    nt.show("shortest-path.html")


