# -*- coding: utf-8 -*-
"""
@author: Kamila Kitowska, Katarzyna Pękala
"""

#%%
#libraries 

import os
import importlib
import numpy as np
import ec2_spot_pricing_simulator as ecs
import matplotlib.pyplot as plt
from textwrap import wrap
#importlib.reload(ecs)

#%%
#auxiliary functions
    
def minimum_from_arrays(a,b):        
    c = []
    for i in range(np.size(a)):
        c.append(min(a[i],b[i])) 
    return c

def is_empty(any_structure):
    if any_structure:
        return False
    else:
        return True

def add_on_demand_instances(spot_avail):    
    # vector of server availibility
    res_vector = np.diff(spot_avail)
    res_vector = np.append(res_vector,0)
    res_vector = np.minimum(np.zeros_like(spot_avail),res_vector)
    tmp = np.absolute(spot_avail-1)
    res_vector = tmp + np.roll(res_vector,1) + np.roll(res_vector,2)
    res_vector = np.maximum(np.zeros_like(spot_avail),res_vector)
    res_vector[0] = 0
    res_vector[1] = 0
    # cost
    cost = 0
    j = 0
    for i in range(len(tmp)):
        if tmp[i] == 1 and j%60==0:
            cost = cost + 1
            j = j + 1
        elif tmp[i] == 1:
            j = j + 1
        else:
            j = 0
    result = (res_vector,cost)
    return result

#%%
def first_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,ec2_od_new, 
                   ec2_od, users_per_server, ec2_price_od_old, ec2_price_od, 
                   revenue, availability_level):
    sim_length_minutes = int((end - start).total_seconds()/60) #how many minutes in simulation
    #simulate user demand
    np.random.seed(1)
    user_demand = np.random.normal(demand_avg,demand_std_dev,sim_length_minutes*n_of_sim) 
    user_demand = np.ceil(user_demand)
    user_demand = np.reshape(user_demand, (n_of_sim, sim_length_minutes))   
    servers_capacity = np.full(sim_length_minutes, ec2_od*users_per_server+ec2_od_new*users_per_server) #server "capacity", in users, per minute
    servers_capacity[0] = ec2_od*users_per_server # two minutes for startup
    servers_capacity[1] = ec2_od*users_per_server # two minutes for startup
    results = []
    #costs
    server_costs_hour = ec2_price_od_old * ec2_od + ec2_od_new * ec2_price_od #price of old and new servers, per hour
    server_costs_min = server_costs_hour/60 #price of all on demand servers, per minute      
    avail_counter = 0
    for i in range(0, n_of_sim):
        #ec2_od_new = np.ceil(max(user_demand[i]-servers_capacity)/100) #how many new on demand servers (based on user demand simulation)      
        diff_capacity_demand = servers_capacity - user_demand[i]
        users_not_served_total = np.sum(diff_capacity_demand[diff_capacity_demand<0])*(-1)    
        #revenue
        users_served = np.array(minimum_from_arrays(servers_capacity,user_demand[i]))
        revenue_min = users_served * revenue # revenue per minute
        #profit
        profit_min = revenue_min - server_costs_min # profit per minute
        profit_total = np.sum(profit_min) #total profit in one simulation
        #print(i, "loop | profit = ",profit_total, "| users denied access = ",users_not_served_total)        
        avail = (np.sum(user_demand[i])-users_not_served_total)/np.sum(user_demand[i])
        if avail>=availability_level:
            avail_counter = avail_counter + 1
        res = [profit_total, users_not_served_total,avail]       
        results.append(res)    
    return (results,avail_counter)

#%%
def second_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,ec2_spot,
                    spot_file, bid, users_per_server, ec2_od, ec2_od_new,
                    ec2_price_od,revenue, availability_level, ec2_price_od_old,
                    my_path):
    os.chdir(my_path)
    sim_length_minutes = int((end - start).total_seconds()/60) #how many minutes in simulation
    #simulate user demand
    np.random.seed(1)
    user_demand = np.random.normal(demand_avg,demand_std_dev,sim_length_minutes*n_of_sim) 
    user_demand = np.ceil(user_demand)
    user_demand = np.reshape(user_demand, (n_of_sim, sim_length_minutes))
    #simulate spot instances       
    sim = ecs.Ec2Simulator(spot_file)
    sim_res = sim.estimate_cost_d(bid,start,end,single_sim_time_s=3600)    
    #server capacity
    servers_capacity = np.full(sim_length_minutes, ec2_od*users_per_server) #server "capacity", in users, per minute
    servers_capacity = servers_capacity + sim_res[2]*ec2_spot*users_per_server    
    results = []
    #print(sim_res[0]*ec2_spot)
    #costs
    server_costs_hour = ec2_price_od_old * ec2_od + ec2_od_new * ec2_price_od #price of old and new servers, per hour
    server_costs_min = server_costs_hour/60 #price of all on demand servers, per minute      
    avail_counter = 0
    for i in range(0, n_of_sim):
        #ec2_od_new = np.ceil(max(user_demand[i]-servers_capacity)/100) #how many new on demand servers (based on user demand simulation)      
        diff_capacity_demand = servers_capacity - user_demand[i]
        users_not_served_total = np.sum(diff_capacity_demand[diff_capacity_demand<0])*(-1)    
        #revenue
        users_served = np.array(minimum_from_arrays(servers_capacity,user_demand[i]))
        revenue_min = users_served * revenue # revenue per minute
        #profit
        profit_min = revenue_min - server_costs_min # profit per minute
        profit_total = np.sum(profit_min)-sim_res[0]*ec2_spot #total profit in one simulation
        #print(i, "| profit = ",profit_total, "| denied access = ",users_not_served_total)
        avail = (np.sum(user_demand[i])-users_not_served_total)/np.sum(user_demand[i])
        if avail>=availability_level:
            avail_counter = avail_counter + 1
        res = [profit_total, users_not_served_total, avail]
        results.append(res)
    return (results,sim_res[2],sim_length_minutes,avail_counter)

#%%
    
def third_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,ec2_spot,spot_file, 
                   bid, users_per_server, ec2_od, ec2_price_od, ec2_price_od_old,
                   revenue, availability_level, my_path):
    os.chdir(my_path)
    sim_length_minutes = int((end - start).total_seconds()/60) #how many minutes in simulation
    #simulate user demand
    np.random.seed(1)
    user_demand = np.random.normal(demand_avg,demand_std_dev,sim_length_minutes*n_of_sim) 
    user_demand = np.ceil(user_demand)
    user_demand = np.reshape(user_demand, (n_of_sim, sim_length_minutes))       
    #simulate spot instances
    sim = ecs.Ec2Simulator(spot_file)
    sim_res = sim.estimate_cost_d(bid,start,end,single_sim_time_s=3600)    
    #simulate server capacity
    servers_capacity = np.full(sim_length_minutes, ec2_od*users_per_server) #server "capacity", in users, per minute
    servers_capacity = servers_capacity + sim_res[2]*ec2_spot*users_per_server #on-demand plus spot servers   
    new_on_demand_instances = add_on_demand_instances(sim_res[2])
    #print(sim_res[2])
    new_on_demand_servers = new_on_demand_instances[0]
    #print(new_on_demand_servers)
    servers_capacity = servers_capacity  + new_on_demand_servers*ec2_spot*users_per_server #on-demand plus spot plus new on-demand
    #costs
    od_server_costs = ec2_price_od_old * ec2_od * sim_length_minutes / 60
    od_new_servers_costs = new_on_demand_instances[1] * ec2_spot * ec2_price_od
    spot_costs = sim_res[0] * ec2_spot
    total_cost = od_server_costs + od_new_servers_costs + spot_costs
    results = []    
    avail_counter = 0
    for i in range(0, n_of_sim):
        #ec2_od_new = np.ceil(max(user_demand[i]-servers_capacity)/100) #how many new on demand servers (based on user demand simulation)      
        diff_capacity_demand = servers_capacity - user_demand[i]
        users_not_served_total = np.sum(diff_capacity_demand[diff_capacity_demand<0])*(-1)    
        #revenue
        users_served = np.array(minimum_from_arrays(servers_capacity,user_demand[i]))
        revenue_min = users_served * revenue # revenue per minute
        #profit
        profit_total = np.sum(revenue_min)-total_cost #total profit in one simulation
        #print(i, "| profit = ",profit_total, "| denied access = ",users_not_served_total)
        avail = (np.sum(user_demand[i])-users_not_served_total)/np.sum(user_demand[i])
        if avail>=availability_level:
            avail_counter = avail_counter + 1
        res = [profit_total, users_not_served_total, avail]
        results.append(res)
    return (results,sim_res[2],new_on_demand_servers,sim_length_minutes,avail_counter)

