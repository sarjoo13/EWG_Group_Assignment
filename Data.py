import pandas as pd
import numpy as np

# whole travel-time dataframe

df = pd.read_csv("sh_undirected_graph_tod.csv")
df_graph = df.groupby(['s1', 's2', 'tod']).mean().reset_index()
print(df['tod'].unique())

# routes of interest
df_routes = pd.read_csv("sh_routes_top_20_most_traveled_drivers.csv")
print(df_routes.shape)
print(df_routes.loc[1,:])

route = df_routes.loc[1,:]

# aoi list: convert str to int
str = route.loc['aoi_list']
comps = str[1:-1].split(',')
aoi_list = [int(x) for x in comps]
print(aoi_list)

route_df = df_graph.loc[df_graph['s1'].isin(aoi_list)].loc[df_graph['s2'].isin(aoi_list)]
print(route_df)

# tod list: convert str to int
str = route.loc['tod_list']
comps = str[1:-1].split(',')
tod_list = [int(x) for x in comps]
print(tod_list)

start_period = min(tod_list)

# Converting tod and time period

# tod to mathematical t
def tod_to_t(tod):
    if tod == 0:
        raise ImportError("Oh no, there is a tod 0!!!")
    elif tod == 1:
        t = 3
        # this shifts all routes starting between 0 and 7 to start at 5 o'clock
    elif tod == 2:
        t = 4
    elif tod == 3:
        t = 7
        # this shifts all routes starting between 9 and 17 to start at 13 o'clock
    elif tod == 4:
        t = 9
    elif tod == 5:
        t = 5
        # this shifts all routes starting between 19 and 24 to start at 19 o'clock
    else:
        raise ImportError("There are more than 5 times of the day")

    return t

# obtaining the dictionary dependent on time of day

num_i = len(route_df['s1'].unique())
num_j = len(route_df['s2'].unique())
num_t = len(route_df['tod'].unique())

#matrix = 100*np.ones((num_i, num_j, 12))
#matrix = np.zeros((num_i, num_j, 12))
matrix = {}
count = 0
periods = []
for i in range(num_i):
    for j in range(num_j):
        for t in range(num_t):
            s1 = route_df['s1'].unique()[i]
            s2 = route_df['s2'].unique()[j]
            tod = route_df['tod'].unique()[t]
            t2 = tod_to_t(tod)
            periods.append(t2)
            if route_df.loc[route_df['s1']==s1].loc[route_df['s2']==s2].loc[route_df['tod']==t].empty:
                #matrix[i,j,t2] = 100
                matrix[s1,s2,t2] = 100
            else:
                matrix[s1,s2,t2] =route_df.loc[route_df['s1']==s1].loc[route_df['s2']==s2].loc[route_df['tod']==t].iloc[0]['avg_time']
                count += 1
print(count) # Number of non-zero entries
print(matrix)

for t in range(1,12):
    if t in periods:
        pass
    else:
        for i in range(num_i):
            for j in range(num_j):
                s1 = route_df['s1'].unique()[i]
                s2 = route_df['s2'].unique()[j]
                matrix[s1, s2,t] = 100

print(matrix)


def t_to_tod(t):
    if t in [0,1,2,3]:
        tod = 1
    elif t == 4:
        tod = 2
    elif t in [3,4,5,6,7,8]:
        tod = 3
    elif t == 9:
        tod = 4
    else:
        tod = 5


