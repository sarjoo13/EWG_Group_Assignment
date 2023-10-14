import pandas as pd
import numpy as np

# whole travel-time dataframe

df = pd.read_csv("sh_undirected_graph_tod.csv")
df_graph = df.groupby(['s1', 's2']).mean().reset_index()

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


# obtaining the dictionary dependent on time of day

num_i = len(route_df['s1'].unique())
num_j = len(route_df['s2'].unique())

matrix = {}
count = 0
for i in range(num_i):
    for j in range(num_j):
            s1 = route_df['s1'].unique()[i]
            s2 = route_df['s2'].unique()[j]
            if route_df.loc[route_df['s1']==s1].loc[route_df['s2']==s2].empty:
                matrix[s1,s2] = 100
            else:
                matrix[s1,s2] =route_df.loc[route_df['s1']==s1].loc[route_df['s2']==s2].iloc[0]['avg_time']
                count += 1
print(count) # Number of non-zero entries
print(matrix)






