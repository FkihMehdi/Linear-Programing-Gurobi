from gurobipy import *
import graphDisplayer 

"""
A method to find the shortest path between two nodes in a graph.

...
Parameters
----------
start : str
    The starting node.
end : str
    The ending node.
dist : dict
    A dictionary containing the distances between the nodes.

Returns
-------
float
    The cost of the shortest path.
list
    The shortest path.


"""
def shortest_path(start:str,end:str,dist:dict[(str,str),float]):
    # Create a new model
    shortest_path_model=Model("Shortest Path Model") 
    # shortest_path_model.params.LogToConsole = 0
    shortest_path_model.params.DualReductions  = 0
    shortest_path_model.params.PoolSolutions = 5
    shortest_path_model.params.PoolSearchMode = 2
    shortest_path_model.params.PoolGap = 0.001
    
    
    
    vertices = { i for i,_ in dist.keys()}.union({ j for _,j in dist.keys()})
    
    # Create variables
    vars = shortest_path_model.addVars(dist.keys(), obj=dist, vtype=GRB.INTEGER, name='x',lb=0)
    
    # Set objective
    shortest_path_model.setObjective(quicksum(vars[i,j]*dist[i,j] for i,j in dist.keys()), GRB.MINIMIZE)

    # Add constraints
    shortest_path_model.addConstr(vars.sum(start, '*')== 1,'Edges out of start')
    shortest_path_model.addConstr(vars.sum('*', end)  == 1, 'Edges into end')
    shortest_path_model.addConstrs(vars.sum('*', c) == vars.sum(c, '*') for c in vertices if c != start and c != end)

    # Optimize model
    shortest_path_model.optimize()
    print("le nombre de solution est : ",shortest_path_model.SolCount)
    print("le status de solution est : ",shortest_path_model.status)
    
    # Checking the status of the model
    if(shortest_path_model.status == GRB.OPTIMAL):
        print("Une solution optimale est trouvée")
    elif(shortest_path_model.status == GRB.INFEASIBLE):
        raise Exception("Il n'existe pas de chemin entre les deux noeud")
    elif shortest_path_model.status in [GRB.INF_OR_UNBD, GRB.INFINITY, GRB.UNBOUNDED]:
        raise Exception("Un Cycle negatif est detecté")
    else:
        raise Exception("Le problème n'est pas résolu",shortest_path_model.status)
    # Building the graph 
    edges = []
    for var in shortest_path_model.getVars():
        nameWithoutX = var.varName[2:len(var.varName)-1]
        edge = graphDisplayer.Edge()
        edge.src, edge.dest = list(nameWithoutX.split(','))
        edge.weight=dist[edge.src,edge.dest]
        edge.color = 'red' if var.x == 1 else 'blue'
        edges.append(edge)
        
    nodes = []
    for c in vertices:
        node = graphDisplayer.Node()
        node.name = c
        if(c == start):
            node.color = 'green'
        elif(c == end):
            node.color = 'orange'
        else:
            node.color = 'blue'
        nodes.append(node)
    
    # Display the graph
    graphDisplayer.display_graph(nodes, edges)
    
    # Building the path
    paths = []
    mapperPairToIndex = {pair:i for i,pair in enumerate(dist.keys())}
    numberOfSolutions = shortest_path_model.SolCount
    for i in range(numberOfSolutions):
        shortest_path_model.setParam(GRB.Param.SolutionNumber, i)
        values = shortest_path_model.Xn
        path = []
        current = start
        path.append(current)
        while current != end:
            for i,j in dist.keys():
                if values[mapperPairToIndex[i,j]] == 1 and i == current:
                    path.append(j)
                    current = j
                    break
        paths.append(path)
 
    return shortest_path_model.objVal, paths
    
    
if __name__ == "__main__":
    dist = {
    ("1","2"): 2,
    ("2","1"): -2,
    # ("3","2"): 1,
    # ("1","4"): 1,
    # ("4","2"): 1,
    # ("1","5"): 1,
    # ("5","2"): 1,
    # ("1","6"): 1,
    # ("6","2"): 1,
    # ("6","1"): -3,
    }
    start = "1"
    end = "1"      
    try:
        obj,path = shortest_path(start,end,dist)
        print ("le cout du chemin le plus court est : ",obj)
        print ("le chemin le plus court est : ",path)
    except Exception as e:
        print(e)

