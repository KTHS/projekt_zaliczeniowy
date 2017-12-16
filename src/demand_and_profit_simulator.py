# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 14:16:31 2017

@author: Katarzyna
"""

#%%

#initial values
start = datetime.datetime.strptime(\
"2017-11-28 2:00:00","%Y-%m-%d %H:%M:%S")
end = datetime.datetime.strptime(\
"2017-11-28 6:00:00","%Y-%m-%d %H:%M:%S")

ec2_od = 300 #amount of on-demand servers
ec2_price_od_old = 0.42 #price of existing on-demand servers, per server per hour
users_per_server = 100 # how many users for one server

revenue = 0.00021   #per server per minute

demand_avg = 40000 #users per minute
demand_std_dev = 5000

ec2_price_od = 0.84 #current price of new on-demand servers, per server per hour

# how many new on demand servers, how many spot servers?
ec2_od_new = 0
ec2_spot = 0



#%%
#user demand simulation

import numpy as np

np.random.seed(1)

sim_length_minutes = int((end - start).total_seconds()/60) #how many minutes in simulation
n_of_sim = 100 #number of demand simulation

#one row of array per one simulation, eg. one row = 3 days*24h*60 minutes of datapoints 
user_demand = np.random.normal(demand_avg,demand_std_dev,sim_length_minutes*n_of_sim) 
user_demand = np.ceil(user_demand)
user_demand = np.reshape(user_demand, (n_of_sim, sim_length_minutes))

#%%
# scenario "only on demand servers", could be a baseline
# input - simulated user demand and the amount of new on demand servers
# number of simulations = amount of 'user demand' time series 
# result is a list of lists: list of total profits and list of how many users were denied access (demand > servers capacity)

#%%    
def minimum_from_arrays(a,b):        
    c = []
    for i in range(np.size(a)):
        c.append(min(a[i],b[i])) 
    return c

#%%    
def first_scenario(user_demand,ec2_od_new):
    results = []
    for i in range(0, n_of_sim):
        servers_capacity = np.full(sim_length_minutes, ec2_od*users_per_server+ec2_od_new*users_per_server) #server "capacity", in users, per minute
        #ec2_od_new = np.ceil(max(user_demand[i]-servers_capacity)/100) #how many new on demand servers (based on user demand simulation)      
        diff_capacity_demand = servers_capacity - user_demand[i]
        users_not_served_total = np.sum(diff_capacity_demand[diff_capacity_demand<0])*(-1)    
        #costs
        server_costs_hour = ec2_price_od_old * ec2_od + ec2_od_new * ec2_price_od #price of old and new servers, per hour
        server_costs_min = server_costs_hour/60 #price of all on demand servers, per minute      
        #revenue
        users_served = np.array(minimum_from_arrays(servers_capacity,user_demand[i]))
        revenue_min = users_served * revenue # revenue per minute
        #profit
        profit_min = revenue_min - server_costs_min # profit per minute
        profit_total = np.sum(profit_min) #total profit in one simulation
        #print(i, "loop | profit = ",profit_total, "| users denied access = ",users_not_served_total)
        res = [profit_total, users_not_served_total]
        results.append(res)
    return results

# simulation of first scenario
for j in range(0, 360, 10):
    res = first_scenario(user_demand,j)
    avg_res = np.array(res).mean(axis=0)
    print("new on demand server amount =",j," | average total profit =", 
      avg_res[0],"| average amount of access denials", avg_res[1],)
    
