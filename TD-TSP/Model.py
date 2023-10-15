import Data as D
from gurobipy import *
from itertools import combinations

df = D.route_df
s = D.matrix
#print(s)

starting_time = D.tod_to_t(D.start_period)
values = []

N = D.aoi_list
T = [t for t in range(1, 12)]
A = [(i, j) for i in N for j in N]
B = [(i,j,t) for i in N for j in N for t in T]
C = [(i,t) for i in N for t in T]

# Model
mdl = Model('TDTSP')

# Create variables
x = mdl.addVars(B, vtype=GRB.BINARY, name="x")
a = mdl.addVars(N, vtype=GRB.CONTINUOUS, name="a")  # time at which a customer is served
d = mdl.addVars(C, vtype=GRB.BINARY, name="d")
c = mdl.addVars(C, vtype=GRB.BINARY, name="c")

# Set the objective function
mdl.modelSense = GRB.MINIMIZE
mdl.setParam('OutputFlag', 1)
mdl.setParam('LogFile', 'output.txt')
mdl.setObjective(quicksum(s[i,j,t] * x[i,j,t] for i, j, t in B))

# Add the constraint
# if - else constraints: if a_i not in [2t-1, 2t+1] -> sum_j x_ijt = 0
# https://support.gurobi.com/hc/en-us/articles/4414392016529-How-do-I-model-conditional-statements-in-Gurobi
# Constants
# M is chosen to be as small as possible given the bounds on x and y
eps = 0.0001
M = 25 + eps

# If a_i > 2t + 1, then d[i,t] = 1
for i in N:
    for t in T:
        mdl.addConstr(a[i] >= 2*t+1 + eps - M * (1 - d[i,t]))
        mdl.addConstr(a[i] <= 2*t+1 + M * d[i,t])
# Add indicator constraints
        mdl.addConstr(
            (d[i, t] == 1) >> (sum(x[i, j, t] for j in N) == 0))
# If a_i < 2t - 1, then c[i,t] = 0
    mdl.addConstr(a[i] >= 2*t-1 + eps - M * (1 - c[i,t]))
    mdl.addConstr(a[i] <= 2*t-1 + M * c[i, t])

# Add indicator constraints
    mdl.addConstr((c[i, t] == 0) >> (sum(x[i, j, t] for j in N) == 0))

# Starting time
    mdl.addConstr(a[i] >= starting_time)

# further constraints
mdl.addConstrs(quicksum(x[i,j,t] for j in N if i != j for t in T) == 1 for i in N)
mdl.addConstrs(quicksum(x[i,j,t] for i in N if i != j for t in T) == 1 for j in N)

# service times
for i in N:
    for j in N:
        for t in T:
            mdl.addConstr((x[i, j, t] == 1) >> (a[j] == a[i] + s[i,j,t]))

# Solve the model
mdl._vars = vars
mdl.Params.LogToConsole = 0
mdl.Params.lazyConstraints = 1

def subtourelim(model, where):
    if where == GRB.Callback.MIPSOL:
        # make a list of edges selected in the solution
        vals = model.cbGetSolution(model._vars)
        selected = tuplelist((i, j) for i, j in model._vars.keys()
                                if vals[i, j] > 0.5)
        # find the shortest cycle in the selected edge list
        tour = subtour(selected)
        if len(tour) < len(N):
            # add subtour elimination constr. for every pair of cities in subtour
            model.cbLazy(quicksum(model._vars[i, j] for i, j in combinations(tour, 2))
                         <= len(tour) - 1)

# Given a tuplelist of edges, find the shortest subtour
def subtour(edges):
    unvisited = N[:]
    cycle = N[:]  # Dummy - guaranteed to be replaced
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
            cycle = thiscycle  # New shortest subtour
    return cycle

mdl.optimize(subtourelim)

if mdl.status == GRB.OPTIMAL:
    print("Optimal solution found!")
    #for var in mdl.getVars():
        #print(f"{var.varName}: {var.x}")
else:
    print("No optimal solution found.")

def get_tours():
    tours = []
    for var in mdl.getVars():
        if var.x > 0.9:
            if var.varName[0] == 'x':
                comps = var.varName.split(',')
                i = int(comps[0][2:])
                j = int(comps[1])
                tours.append((i,j))
    return tours

print(get_tours())


