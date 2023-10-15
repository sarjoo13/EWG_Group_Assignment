import pandas as pd
import numpy as np

def get_route_dict(n):
    """
    :param n: Determines how many routes of the total 6383 will be considered
              The first n rows are then selected
    :return: dictionary containing for each remaining route, its id, list of aois, avg_time matrix for those aois
    and a additional time that needs to be added to the model solutions
    """
    routes = {}

    # whole travel-time dataframe

    df = pd.read_csv("sh_undirected_graph_tod.csv")
    df_graph = df.groupby(['s1', 's2']).mean().reset_index()

    # routes of interest
    df_routes = pd.read_csv("sh_routes_top_20_most_traveled_drivers.csv")
    #print(df_routes.shape)
    #print(df_routes.loc[1,:])

    dict_idx = 0
    for row_idx in range(500): # eig 6838 rows
        route = df_routes.loc[row_idx,:]
        id = df_routes.loc[row_idx, 'route_id']

        # aoi list: convert str to int
        str = route.loc['aoi_list']
        comps = str[1:-1].split(',')
        aoi_list = [int(x) for x in comps]
        #print(aoi_list)

        # Add time for the drivings within one aoi

        add_time = 0
        for elm in aoi_list:
            if aoi_list.count(elm) > 1:
                number = aoi_list.count(elm)
                if df_graph.loc[df_graph['s1']==elm].loc[df_graph['s2']==elm].empty:
                    continue
                time = df_graph.loc[df_graph['s1']==elm].loc[df_graph['s2']==elm].iloc[0]['avg_time']
                add_time += (number -1) * time

        route_df = df_graph.loc[df_graph['s1'].isin(aoi_list)].loc[df_graph['s2'].isin(aoi_list)]
        #print(route_df)


        # obtaining the dictionary dependent on time of day

        num_i = len(route_df['s1'].unique())
        num_j = len(route_df['s2'].unique())

        #if num_i != num_j:
        #    raise ImportError("S1 and S2 do not have the same aois")
        if num_i == 1:
            continue

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
        #print(count) # Number of non-zero entries

        routes[dict_idx] = {'id': id, 'aoi_list': aoi_list, 'matrix': matrix, 'add_time': add_time}
        dict_idx += 1

    #print(routes)
    return routes