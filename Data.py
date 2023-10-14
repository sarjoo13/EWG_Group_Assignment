import pandas as pd
import numpy as np

df = pd.read_csv("sh_undirected_graph_tod.csv")
df_graph = df.groupby(['s1', 's2', 'tod']).mean().reset_index()

num_i = len(df_graph['s1'].unique())
num_j = len(df_graph['s2'].unique())
num_t = len(df_graph['tod'].unique())

# TODO: This takes too long
matrix = np.zeros((num_i, num_j, num_t))
for i in range(num_i):
    for j in range(num_j):
        for t in range(num_t):
            s1 = df_graph['s1'].unique()[i]
            s2 = df_graph['s2'].unique()[j]
            tod = df_graph['tod'].unique()[t]
            if df_graph.loc[df_graph['s1']==s1].loc[df_graph['s2']==s2].loc[df_graph['tod']==t].empty:
                continue
            else:
                matrix[i,j,t] = df_graph.loc[df_graph['s1']==s1].loc[df_graph['s2']==s2].loc[df_graph['tod']==t].iloc[0]['avg_time']

print(matrix[1,1,0])
print(matrix)


