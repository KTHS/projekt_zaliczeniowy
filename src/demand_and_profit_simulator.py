# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 14:16:31 2017

@author: Katarzyna
"""

#%%

#initial values

ec2_od = 300 #amount of on-demand servers
ec2_price_od_old = 0.42 #price of existing on-demand servers, per server per hour
users_per_server = 100 # how many users for one server

revenue = 0.00021 #per server per minute

demand_avg = 40000 #users per minute
demand_std_dev = 5000

ec2_price_od = 0.84 #current price of new on-demand servers, per server per hour

# how many new on demand servers, how many spot servers?
ec2_od_new = 0
ec2_spot = 0

sim_length_days = 3 # how many days in simulation


#%%
#user demand simulation

import numpy as np

np.random.seed(1)

sim_length_minutes = sim_length_days * 24 * 60 #how many minutes in simulation
n_of_sim = 1000 #number of demand simulation

#one row of array per one simulation, eg. one row = 3 days*24h*60 minutes of datapoints 
user_demand = np.random.normal(demand_avg,demand_std_dev,sim_length_minutes*n_of_sim) 
user_demand = np.ceil(user_demand)
user_demand = np.reshape(user_demand, (n_of_sim, sim_length_minutes))


#%%
# scenario "only on demand servers", could be a baseline

for i in range(0, n_of_sim):
    servers_capacity = np.full(sim_length_minutes, ec2_od*users_per_server) #server "capacity", in users, per minute
    ec2_od_new = np.ceil(max(user_demand[i]-servers_capacity)/100) #how many new on demand servers (based on user demand simulation)
    server_costs_hour = ec2_price_od_old * ec2_od + ec2_od_new * ec2_price_od #price of old and new servers, per hour
    server_costs_min = server_costs_hour/60 #price of all on demand servers, per minute
    revenue_min = user_demand[i] * revenue # revenue per minute
    profit_min = revenue_min - server_costs_min # profit per minute
    profit_total = np.sum(profit_min) #total profit in one simulation
    print(i, "profit = ",profit_total)