import numpy as np
import pandas as pd

import gurobipy as gp
from gurobipy import GRB

# PARAMETERS

months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]


products = ["P1", "P2", "P3", "P4", "P5"]
profit = {"P1": 10, "P2": 6, "P3": 8, "P4": 4, "P5": 11}


machines = ["M1", "M2", "M3", "M4"]
# number of each machine installed
installed = {"M1": 4, "M2": 2, "M3": 3, "M4": 1}
time_req = {
    "M1": {"P1": 0.5, "P2": 0.7, "P5": 0.3},
    "M2": {"P1": 0.1, "P2": 0.2, "P4": 0.3},
    "M3": {"P1": 0.2, "P3": 0.8},
    "M4": {"P1": 0.05, "P2": 0.03, "P4": 0.07, "P5": 0.1}
}

# market limitations on products
max_sales = {
    ("Jan", "P1"): 500,
    ("Jan", "P2"): 1000,
    ("Jan", "P3"): 300,
    ("Jan", "P4"): 300,
    ("Jan", "P5"): 800,

    ("Feb", "P1"): 200,
    ("Feb", "P2"): 100,
    ("Feb", "P3"): 600,
    ("Feb", "P4"): 500,
    ("Feb", "P5"): 200,

    ("Mar", "P1"): 0,
    ("Mar", "P2"): 400,
    ("Mar", "P3"): 300,
    ("Mar", "P4"): 150,
    ("Mar", "P5"): 300,

    ("Apr", "P1"): 500,
    ("Apr", "P2"): 1000,
    ("Apr", "P3"): 300,
    ("Apr", "P4"): 300,
    ("Apr", "P5"): 800,

    ("May", "P1"): 600,
    ("May", "P2"): 0,
    ("May", "P3"): 0,
    ("May", "P4"): 500,
    ("May", "P5"): 400,

    ("June", "P1"): 100,
    ("June", "P2"): 200,
    ("June", "P3"): 300,
    ("June", "P4"): 400,
    ("June", "P5"): 500,
}

holding_cost = 0.5
max_inventory = 100
# must have stock at the last month for each product
store_target = 50
hours_per_month = 8 * 24



model = gp.Model('Problem 2')

# Variables

produce = model.addVars(months, products, name="Produce") # manufactured quantity
store = model.addVars(months,products, ub=max_inventory,name="Store") # stored quantity
sell = model.addVars(months,products, ub=max_sales, name="Sell") # sold quantity


# Constraints

# initial balance
balance0 = model.addConstrs((produce[months[0],product] == sell[months[0],product] + store[months[0],product] for product in products), name="Initial Balance")

# balance
balance = model.addConstrs((store[months[months.index(month) - 1], product] +  produce[month,product] == sell[month,product] + store[month,product] for product in products for month in months if month != months[0]), name="Balance")

# inventory target at the end of the last month
inventory = model.addConstrs((store[months[-1],product] == store_target for product in products), name = "Inventory_Target")

# machine capacity
capacity = model.addConstrs((gp.quicksum(time_req[machine][product] * produce[month,product] for product in time_req[machine]) <= hours_per_month * installed[machine] for machine in machines for month in months), name="Capacity")




# Objective Function
objective = gp.quicksum(profit[product] * sell[month,product] - holding_cost * store[month,product] for month in months for product in products)
model.setObjective(objective,GRB.MAXIMIZE)


model.optimize()



# Results


rows = months.copy()
columns = products.copy()

production_plan = pd.DataFrame(columns=columns, index=rows, data=0.0)

for month, product in produce.keys():
    if (abs(produce[month,product].x) > 1e-6):
        production_plan.loc[month,product] = np.round(produce[month,product].x,1)

print(production_plan)



sales_plan = pd.DataFrame(columns=columns, index=rows, data=0.0)

for month, product in sell.keys():
    if (abs(sell[month, product].x) > 1e-6):
        sales_plan.loc[month, product] = np.round(sell[month, product].x, 1)
print(sales_plan)



inventory_plan = pd.DataFrame(columns=columns, index=rows, data=0.0)

for month, product in store.keys():
    if (abs(store[month, product].x) > 1e-6):
        inventory_plan.loc[month, product] = np.round(store[month, product].x, 1)
print(inventory_plan)