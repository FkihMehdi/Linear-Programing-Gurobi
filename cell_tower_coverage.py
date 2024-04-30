import gurobipy as gp
from gurobipy import GRB

# tested with Gurobi v9.0.0 and Python 3.7.0

# Parameters
budget = 20
regions, population = gp.multidict({
    0: 523, 1: 690, 2: 420,
    3: 1010, 4: 1200, 5: 850,
    6: 400, 7: 1008, 8: 950
})

sites, coverage, cost = gp.multidict({
    0: [{0, 1, 5}, 4.2],
    1: [{0, 7, 8}, 6.1],
    2: [{2, 3, 4, 6}, 5.2],
    3: [{2, 5, 6}, 5.5],
    4: [{0, 2, 6, 7, 8}, 4.8],
    5: [{3, 4, 8}, 9.2]
})

# MIP  model formulation
m = gp.Model("cell_tower")

build = m.addVars(len(sites), vtype=GRB.BINARY, name="Build")
is_covered = m.addVars(len(regions), vtype=GRB.BINARY, name="Is_covered")

m.addConstrs((gp.quicksum(build[t] for t in sites if r in coverage[t]) >= is_covered[r]
              for r in regions), name="Build2cover")
m.addConstr(build.prod(cost) <= budget, name="budget")

m.setObjective(is_covered.prod(population), GRB.MAXIMIZE)

m.optimize()

# display optimal values of decision variables

for tower in build.keys():
    if (abs(build[tower].x) > 1e-6):
        print(f"\n Build a cell tower at location Tower {tower}.")

# Percentage of the population covered by the cell towers built is computed as follows.

total_population = 0

for region in range(len(regions)):
    total_population += population[region]

coverage = round(100 * m.objVal / total_population, 2)

print(f"\n The population coverage associated to the cell towers build plan is: {coverage} %")

# Percentage of budget consumed to build cell towers

total_cost = 0

for tower in range(len(sites)):
    if (abs(build[tower].x) > 0.5):
        total_cost += cost[tower] * int(build[tower].x)

budget_consumption = round(100 * total_cost / budget, 2)

print(f"\n The percentage of budget consumed associated to the cell towers build plan is: {budget_consumption} %")
