import numpy as np
import pandas as pd

import gurobipy as gp
from gurobipy import GRB




def handle():
    # PARAMETERS
    duration = 2
    months = ["durée " + (str(i)) for i in range(1,duration+1)]


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
        ("durée 1", "P1"): 500,
        ("durée 1", "P2"): 1000,
        ("durée 1", "P3"): 300,
        ("durée 1", "P4"): 300,
        ("durée 1", "P5"): 800,

        ("durée 2", "P1"): 200,
        ("durée 2", "P2"): 100,
        ("durée 2", "P3"): 600,
        ("durée 2", "P4"): 500,
        ("durée 2", "P5"): 200,

        ("durée 3", "P1"): 0,
        ("durée 3", "P2"): 400,
        ("durée 3", "P3"): 300,
        ("durée 3", "P4"): 150,
        ("durée 3", "P5"): 300,

        ("durée 4", "P1"): 500,
        ("durée 4", "P2"): 1000,
        ("durée 4", "P3"): 300,
        ("durée 4", "P4"): 300,
        ("durée 4", "P5"): 800,

        ("durée 5", "P1"): 600,
        ("durée 5", "P2"): 0,
        ("durée 5", "P3"): 0,
        ("durée 5", "P4"): 500,
        ("durée 5", "P5"): 400,

        ("durée 6", "P1"): 100,
        ("durée 6", "P2"): 200,
        ("durée 6", "P3"): 300,
        ("durée 6", "P4"): 400,
        ("durée 6", "P5"): 500,
    }


    holding_cost = 0.5 # store cost
    max_inventory = 100 # store capcity
    # must have stock at the last month for each product
    store_target = 50 # store target

    hours_per_month = 8 * 24 # period work duration



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



    model.setParam(GRB.Param.PoolSearchMode,2)
    model.setParam(GRB.Param.PoolSolutions,1000)
    model.setParam(GRB.Param.PoolGap,0.10)
    model.optimize()


    num_solutions = model.SolCount

    rows = months.copy()
    columns = products.copy()

    solutions = []
    # Retrieve and print all solutions
    for i in range(num_solutions):
        model.setParam(GRB.Param.SolutionNumber, i)

        # Create dataframes for each plan
        production_plan = pd.DataFrame(columns=products, index=months, data=0.0)
        sales_plan = pd.DataFrame(columns=products, index=months, data=0.0)
        inventory_plan = pd.DataFrame(columns=products, index=months, data=0.0)

        # Fill the dataframes with the solution data
        for month, product in produce.keys():
            if (abs(produce[month,product].X) > 1e-6):
                production_plan.loc[month,product] = np.round(produce[month,product].X,1)
        for month, product in sell.keys():
            if (abs(sell[month, product].X) > 1e-6):
                sales_plan.loc[month, product] = np.round(sell[month, product].X, 1)
        for month, product in store.keys():
            if (abs(store[month, product].X) > 1e-6):
                inventory_plan.loc[month, product] = np.round(store[month, product].X, 1)
        
        # Store the solution
        solutions.append({
            'objective_value': model.ObjVal,
            'production_plan': production_plan,
            'sales_plan': sales_plan,
            'inventory_plan': inventory_plan
        })

    return solutions


# handle()

# Results

# for i,solution in enumerate(solutions):
#     print('Solution ', i)
#     print('Objective value: ', solution['objective_value'])
#     print('Production plan:')
#     print(solution['production_plan'])
#     print('Sales plan:')
#     print(solution['sales_plan'])
#     print('Inventory plan:')
#     print(solution['inventory_plan'])

