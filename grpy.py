import numpy as np
import pandas as pd

import gurobipy as gp
from gurobipy import GRB




def handle(periods, gain, installed, time_req, max_do, holding_cost, max_inventory, store_target, total_work):



    # PARAMETERS
    tasks = list(gain.keys())
    ressources = list(installed.keys())

    

    model = gp.Model('Multi-resource Allocation Problem')

    # Variables

    do = model.addVars(periods, tasks, name="Do") # units of a task to be done in a period
    store = model.addVars(periods,tasks, ub=max_inventory,name="Store") # units of a task to defer in a period
    make = model.addVars(periods,tasks, ub=max_do, name="Make") # units of a task done in a period


    # Constraints

    # initial balance
    balance0 = model.addConstrs((do[periods[0],task] == make[periods[0],task] + store[periods[0],task] for task in tasks), name="Initial Balance")

    # balance
    balance = model.addConstrs((store[periods[periods.index(period) - 1], task] +  do[period,task] == make[period,task] + store[period,task] for task in tasks for period in periods if period != periods[0]), name="Balance")

    # task accomplishment
    inventory = model.addConstrs((store[periods[-1],task] == store_target for task in tasks), name = "Inventory_Target")

    # ressource capacity
    capacity = model.addConstrs((gp.quicksum(time_req[ressource][task] * do[period,task] for task in time_req[ressource]) <= total_work * installed[ressource] for ressource in ressources for period in periods), name="Capacity")
    task_assignment = model.addConstrs((gp.quicksum(time_req[resource][task] * installed[resource] for task in tasks) >= 0.00001 for resource in ressources),name="Task_Assignment")



    # Objective Function
    objective = gp.quicksum(gain[task] * make[period,task] - holding_cost * store[period,task] for period in periods for task in tasks)
    model.setObjective(objective,GRB.MAXIMIZE)



    model.setParam(GRB.Param.PoolSearchMode,2)
    model.setParam(GRB.Param.PoolSolutions,1000)
    model.setParam(GRB.Param.PoolGap,0.10)
    model.optimize()


    if model.Status == GRB.INFEASIBLE:
        return []


    num_solutions = model.SolCount

    rows = periods.copy()
    columns = tasks.copy()

    solutions = []

    # Retrieve and print all solutions
    for i in range(num_solutions):
        model.setParam(GRB.Param.SolutionNumber, i)

        # Create dataframes for each plan
        tasks_plan = pd.DataFrame(columns=tasks, index=periods, data=0.0)
        make_plan = pd.DataFrame(columns=tasks, index=periods, data=0.0)
        inventory_plan = pd.DataFrame(columns=tasks, index=periods, data=0.0)

        # Fill the dataframes with the solution data
        for period, task in do.keys():
            if (abs(do[period,task].X) > 1e-6):
                tasks_plan.loc[period,task] = np.round(do[period,task].X,1)
        for period, task in make.keys():
            if (abs(make[period, task].X) > 1e-6):
                make_plan.loc[period, task] = np.round(make[period, task].X, 1)
        for period, task in store.keys():
            if (abs(store[period, task].X) > 1e-6):
                inventory_plan.loc[period, task] = np.round(store[period, task].X, 1)
        
        # Store the solution
        solutions.append({
            'objective_value': model.ObjVal,
            'tasks_plan': tasks_plan,
            'make_plan': make_plan,
            'inventory_plan': inventory_plan
        })


    for i,solution in enumerate(solutions):
        print('Solution ', i)
        print('Objective value: ', solution['objective_value'])
        print('tasks plan:')
        print(solution['tasks_plan'])
        print('Sales plan:')
        print(solution['make_plan'])
        print('Inventory plan:')
        print(solution['inventory_plan'])

    return solutions


# periods = ["durée" + str(i) for i in range(1,6)]
# gain = {
#     "P1": 10, "P2": 6, "P3": 8, "P4": 4, "P5": 11
# }
# installed = {
#     "M1": 1, "M2": 1, "M3": 1, "M4": 1
# }
# time_req = {
#         "M1": {"P1": 0.5, "P2": 0.7, "P5": 0.3},
#         "M2": {"P1": 0.1, "P2": 0.2, "P4": 0.3},
#         "M3": {"P1": 0.2, "P3": 0.8},
#         "M4": {"P1": 0.05, "P2": 0.03, "P4": 0.07, "P5": 0.1}
# }
#
# max_do = {
#         ("durée 1", "P1"): 500,
#         ("durée 1", "P2"): 1000,
#         ("durée 1", "P3"): 300,
#         ("durée 1", "P4"): 300,
#         ("durée 1", "P5"): 800,
#
#         ("durée 2", "P1"): 200,
#         ("durée 2", "P2"): 100,
#         ("durée 2", "P3"): 600,
#         ("durée 2", "P4"): 500,
#         ("durée 2", "P5"): 200,
#
#         ("durée 3", "P1"): 0,
#         ("durée 3", "P2"): 400,
#         ("durée 3", "P3"): 300,
#         ("durée 3", "P4"): 150,
#         ("durée 3", "P5"): 300,
#
#         ("durée 4", "P1"): 500,
#         ("durée 4", "P2"): 1000,
#         ("durée 4", "P3"): 300,
#         ("durée 4", "P4"): 300,
#         ("durée 4", "P5"): 800,
#
#         ("durée 5", "P1"): 600,
#         ("durée 5", "P2"): 0,
#         ("durée 5", "P3"): 0,
#         ("durée 5", "P4"): 500,
#         ("durée 5", "P5"): 400,
#
#         ("durée 6", "P1"): 100,
#         ("durée 6", "P2"): 200,
#         ("durée 6", "P3"): 300,
#         ("durée 6", "P4"): 400,
#         ("durée 6", "P5"): 500,
# }
#
    
# holding_cost = 0.5 # store cost
# max_inventory = 100 # store capcity
# # must have stock at the last period for each task
# store_target = 0 # store target
#
# total_work = 8 * 24 # period work duration
#
# handle(periods, gain, installed, time_req, max_do, holding_cost, max_inventory, store_target, total_work)



# Results

# for i,solution in enumerate(solutions):
#     print('Solution ', i)
#     print('Objective value: ', solution['objective_value'])
#     print('taskion plan:')
#     print(solution['tasks_plan'])
#     print('Sales plan:')
#     print(solution['make_plan'])
#     print('Inventory plan:')
#     print(solution['inventory_plan'])

