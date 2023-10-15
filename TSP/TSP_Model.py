import gurobipy as gp
from gurobipy import GRB
from itertools import combinations

import TSP_Data as Data

"""
This file takes the avg_time matrix defined in TSP_Data.py and solves the corresponding TSP model. 
The printed list consists of tupels (route_id, total_driving_time) where the total driving time is the sum
of the optimal objective value (for all distances between aois) and the additional time corresponding to the 
drivings within one aoi.
"""

n = 500     # number of considered routes

objvals = []
pairs = []

routes = Data.get_route_dict(n)

for key in routes.keys():
    print("Route ", routes[key]['id'])
    capitals = routes[key]['aoi_list']
    dist = routes[key]['matrix']

    m = gp.Model()
    m.setParam('OutputFlag', 0)

    # Variables: is city 'i' adjacent to city 'j' on the tour?
    vars = m.addVars(dist.keys(), obj=dist, vtype=GRB.BINARY, name='x')

    # Symmetric direction: Copy the object
    for i, j in vars.keys():
        vars[j, i] = vars[i, j]  # edge in opposite direction

    # Constraints: two edges incident to each city
    cons = m.addConstrs(vars.sum(c, '*') == 2 for c in capitals)

    # Callback - use lazy constraints to eliminate sub-tours

    def subtourelim(model, where):
        if where == GRB.Callback.MIPSOL:
            # make a list of edges selected in the solution
            vals = model.cbGetSolution(model._vars)
            selected = gp.tuplelist((i, j) for i, j in model._vars.keys()
                                 if vals[i, j] > 0.5)
            # find the shortest cycle in the selected edge list
            tour = subtour(selected)
            if len(tour) < len(capitals):
                # add subtour elimination constr. for every pair of cities in subtour
                model.cbLazy(gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2))
                             <= len(tour)-1)

    # Given a tuplelist of edges, find the shortest subtour

    def subtour(edges):
        unvisited = capitals[:]
        cycle = capitals[:] # Dummy - guaranteed to be replaced
        while unvisited:  # true if list is non-empty
            thiscycle = []
            neighbors = unvisited
            while neighbors:
                current = neighbors[0]
                thiscycle.append(current)
                unvisited.remove(current)
                neighbors = [j for i, j in edges.select(current, '*')
                             if j in unvisited]
            if len(thiscycle) <= len(cycle):
                cycle = thiscycle # New shortest subtour
        return cycle

    m._vars = vars
    m.Params.lazyConstraints = 1
    m.optimize(subtourelim)

    if m.status == GRB.OPTIMAL:
        obj = m.objVal + routes[key]['add_time']
        print("Time: ", obj)
        objvals.append(obj)
        pairs.append((routes[key]['id'], obj))
    else:
        print('Unfeasible')
        objvals.append(0)
        pairs.append((routes[key]['id'], routes[key]['add_time']))

print('*****************************************************')
print(objvals)
print(pairs)