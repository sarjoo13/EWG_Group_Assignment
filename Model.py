import pandas as pd
from gurobipy import *
from itertools import combinations

# Toy Example to check model
# TODO: With this example, model is infeasible

df = pd.DataFrame({'s1': [0,0,0,0,0,0,1,1,1,1,1,1,2,2,2,2,2,2],
                   's2': [0,0,1,1,2,2,0,0,1,1,2,2,0,0,1,1,2,2],
                   'tod': [0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1],
                   'avg_time': [1,2,2,3,4,3,5,2,3,4,3,2,1,2,2,3,3,4]})

num_i = len(df['s1'].unique())
num_j = len(df['s2'].unique())
num_t = len(df['tod'].unique())

# TODO: time matrix from Daniela
s = {}
for i in range(num_i):
    for j in range(num_j):
        for t in range(num_t):
            s1 = df['s1'].unique()[i]
            s2 = df['s2'].unique()[j]
            tod = df['tod'].unique()[t]
            if df.loc[df['s1']==s1].loc[df['s2']==s2].loc[df['tod']==t].empty:
                continue
            else:
                s[i,j,t] = df.loc[df['s1']==s1].loc[df['s2']==s2].loc[df['tod']==t].iloc[0]['avg_time']
print(s)

n = len(df['s1'].unique())
tod = len(df['tod'].unique())
values = []

N = [i for i in range(n)]
T = [t for t in range(tod)]
# TODO when incorporating Danielas matrix: Breaking down tod in 2h-slots and giving most of the the same avg_time
A = [(i, j) for i in N for j in N]     # Set of arcs
B = [(i,j,t) for i in N for j in N for t in T]
C = [(i,t) for i in N for t in T]

# Model
mdl = Model('TDTSP')

# Create variables
x = mdl.addVars(B, vtype=GRB.BINARY, name="x")  # if a vehicle travels in an arc
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
        mdl.addConstr(a[i] >= 30*t+15 + eps - M * (1 - d[i,t]))
        mdl.addConstr(a[i] <= 30*t+15 + M * d[i,t])
# Add indicator constraints
        mdl.addConstr(
            (d[i, t] == 1) >> (sum(x[i, j, t] for j in N) == 0))
# If a_i < 2t - 1, then c[i,t] = 0
    mdl.addConstr(a[i] >= 30 * t - 15 + eps - M * (1 - c[i,t]))
    mdl.addConstr(a[i] <= 30 * t - 15 + M * c[i, t])

# Add indicator constraints
    mdl.addConstr((c[i, t] == 0) >> (sum(x[i, j, t] for j in N) == 0))

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

values.append([mdl.ObjVal])


