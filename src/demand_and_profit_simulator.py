# -*- coding: utf-8 -*-
"""
Created on Thu Dec 14 14:16:31 2017

@author: Katarzyna
"""

#%%
#libraries and initial values

import os
os.chdir("C:/pth/")

import importlib
import datetime
import numpy as np
import ec2_spot_pricing_simulator as ecs
import matplotlib.pyplot as plt
from textwrap import wrap
importlib.reload(ecs)

# simulation start and end dates
start = datetime.datetime.strptime(\
"2017-11-21 10:00:00","%Y-%m-%d %H:%M:%S")
end = datetime.datetime.strptime(\
"2017-11-21 20:00:00","%Y-%m-%d %H:%M:%S")

ec2_od = 300 #amount of on-demand servers, already bought
ec2_price_od_old = 0.42 #price of existing on-demand servers, per server per hour
users_per_server = 100 # how many users for one server

revenue = 0.00021   #per server per minute
demand_avg = 40000 #users per minute, avg, preditcion
demand_std_dev = 5000 #users per minute, standard dev, preditcion

ec2_price_od = 0.84 #current price of new on-demand servers, per server per hour

# how many new on demand servers, how many spot servers?
# inital values
ec2_od_new = 0
ec2_spot = 0

n_of_sim = 100 #number of simulations


#%%    
def minimum_from_arrays(a,b):        
    c = []
    for i in range(np.size(a)):
        c.append(min(a[i],b[i])) 
    return c

#%%    
# scenario "only on demand servers"
def first_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,ec2_od_new):
    sim_length_minutes = int((end - start).total_seconds()/60) #how many minutes in simulation
    #simulate user demand
    np.random.seed(1)
    user_demand = np.random.normal(demand_avg,demand_std_dev,sim_length_minutes*n_of_sim) 
    user_demand = np.ceil(user_demand)
    user_demand = np.reshape(user_demand, (n_of_sim, sim_length_minutes))   
    servers_capacity = np.full(sim_length_minutes, ec2_od*users_per_server+ec2_od_new*users_per_server) #server "capacity", in users, per minute
    results = []
    #costs
    server_costs_hour = ec2_price_od_old * ec2_od + ec2_od_new * ec2_price_od #price of old and new servers, per hour
    server_costs_min = server_costs_hour/60 #price of all on demand servers, per minute      
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
        res = [profit_total, users_not_served_total]
        results.append(res)
    return results

# simulation of first scenario
# 
avg_profit = []
avg_denials = []
for j in range(0, 360, 10):
    res = first_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,j)
    avg_res = np.array(res).mean(axis=0)
    avg_profit.append(avg_res[0]) 
    avg_denials.append(avg_res[1]/1000)
    print("additional on-demand servers =",j," | avg total profit =", 
      avg_res[0],"| avg amount of denials-of-access", avg_res[1],)
#plot
fig, ax1 = plt.subplots()
plt.suptitle('First scenario: only on-demand servers')
max_profit = max(avg_profit)
ax2 = ax1.twinx()
ax1.plot(avg_profit,range(0,360,10), 'g-')
ax1.plot(max_profit,avg_profit.index(max_profit)*10,'ro') # max_profit point
ax1.annotate((int(max_profit),avg_profit.index(max_profit)*10), \
             xy=(max_profit,avg_profit.index(max_profit)*10),xytext=(max_profit-600,avg_profit.index(max_profit)*10), \
             arrowprops=dict(facecolor='black', shrink=0.05)) # arrow and max value annotation
ax2.plot(avg_profit,avg_denials, 'b-')
ax2.plot(max_profit,avg_denials[avg_profit.index(max_profit)],'ro') # max_profit point
ax2.annotate((int(max_profit),int(avg_denials[avg_profit.index(max_profit)])), \
             xy=(max_profit,avg_denials[avg_profit.index(max_profit)]),xytext=(max_profit-600, \
              avg_denials[avg_profit.index(max_profit)]),arrowprops=dict(facecolor='black', shrink=0.05)) # arrow and max value annotation

ax1.set_xlabel('Avg total profit')
ax1.set_ylabel('no of od servers', color='g')
ax2.set_ylabel('MM denailas', color='b')

plt.show()

    
#%%
# "old" on demand servers + spot instances only
def second_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,ec2_spot):
    sim_length_minutes = int((end - start).total_seconds()/60) #how many minutes in simulation
    #simulate user demand
    np.random.seed(1)
    user_demand = np.random.normal(demand_avg,demand_std_dev,sim_length_minutes*n_of_sim) 
    user_demand = np.ceil(user_demand)
    user_demand = np.reshape(user_demand, (n_of_sim, sim_length_minutes))
    #simulate spot instances       
    sim = ecs.Ec2Simulator('ceny_spot_sim.txt')
    sim_res = sim.estimate_cost_d(0.26,start,end,single_sim_time_s=3600)    
    #server capacity
    servers_capacity = np.full(sim_length_minutes, ec2_od*users_per_server) #server "capacity", in users, per minute
    servers_capacity = servers_capacity + sim_res[2]*ec2_spot*users_per_server    
    results = []
    #print(sim_res[0]*ec2_spot)
    #costs
    server_costs_hour = ec2_price_od_old * ec2_od + ec2_od_new * ec2_price_od #price of old and new servers, per hour
    server_costs_min = server_costs_hour/60 #price of all on demand servers, per minute      
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
        res = [profit_total, users_not_served_total]
        results.append(res)
    return (results,sim_res[2],sim_length_minutes)

avg_profit = []
avg_denials = []
for j in range(0, 360, 10):
    res = second_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,j)
    avg_res = np.array(res[0]).mean(axis=0)
    avg_profit.append(avg_res[0]) 
    avg_denials.append(avg_res[1]/1000)
    print("additional spot servers =",j," | avg tot. profit =", 
      avg_res[0],"| avg amount of denials", avg_res[1],)

spot_min = np.sum(res[1])
sim_min = res[2]

print("---")
print("Spot servers were working for", spot_min, "minutes (",spot_min/sim_min*100,"% of simulation time)")
print("For", sim_min-spot_min, "minutes only 300 on-demand servers were working (",(sim_min-spot_min)/sim_min*100,"% of simulation time)")

#plot
fig, ax1 = plt.subplots()
plt.suptitle('Second scenario: 300 reserved on-demand servers and spot instances only')

max_profit = max(avg_profit)
ax2 = ax1.twinx()
ax1.plot(avg_profit,range(0,360,10), 'g-')
ax1.plot(max_profit,avg_profit.index(max_profit)*10,'ro')
ax1.annotate((int(max_profit),avg_profit.index(max_profit)*10), \
             xy=(max_profit,avg_profit.index(max_profit)*10),xytext=(max_profit-300, \
             avg_profit.index(max_profit)*10),arrowprops=dict(facecolor='black', shrink=0.05))
ax2.plot(avg_profit,avg_denials, 'b-')
ax2.plot(max_profit,avg_denials[avg_profit.index(max_profit)],'ro')
ax2.annotate((int(max_profit),int(avg_denials[avg_profit.index(max_profit)])), \
             xy=(max_profit,avg_denials[avg_profit.index(max_profit)]), \
             xytext=(max_profit-300,avg_denials[avg_profit.index(max_profit)]),arrowprops=dict(facecolor='black', shrink=0.05))

ax1.set_xlabel('Avg total profit')
ax1.set_ylabel('no of od servers', color='g')
ax2.set_ylabel('MM denailas', color='b')

plt.show()


#%%
import numpy

def add_on_demand_instances(spot_avail):    
    # vector of server availibility
    res_vector = numpy.diff(spot_avail)
    res_vector = numpy.append(res_vector,0)
    res_vector = np.minimum(numpy.zeros_like(spot_avail),res_vector)
    tmp = numpy.absolute(spot_avail-1)
    res_vector = tmp + numpy.roll(res_vector,1) + numpy.roll(res_vector,2)
    res_vector = np.maximum(numpy.zeros_like(spot_avail),res_vector)
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
# "old" on demand servers + spot instances + on-demand servers when spot unavaible    
# on-demand needs 2 min for startup

def third_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,ec2_spot):
    sim_length_minutes = int((end - start).total_seconds()/60) #how many minutes in simulation
    #simulate user demand
    np.random.seed(1)
    user_demand = np.random.normal(demand_avg,demand_std_dev,sim_length_minutes*n_of_sim) 
    user_demand = np.ceil(user_demand)
    user_demand = np.reshape(user_demand, (n_of_sim, sim_length_minutes))       
    #simulate spot instances
    sim = ecs.Ec2Simulator('ceny_spot_sim.txt')
    sim_res = sim.estimate_cost_d(0.235,start,end,single_sim_time_s=3600)    
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
        res = [profit_total, users_not_served_total]
        results.append(res)
    return (results,sim_res[2],new_on_demand_servers,sim_length_minutes)

avg_profit = []
avg_denials = []
for j in range(0, 50, 10):
    res  = third_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,j)
    avg_res = np.array(res[0]).mean(axis=0)
    avg_profit.append(avg_res[0]) 
    avg_denials.append(avg_res[1]/1000)
    print("additional spot/on-demand servers =",j," | avg tot. profit =", 
      avg_res[0],"| avg amount of denials", avg_res[1],)

spot_min = np.sum(res[1])
nod_min = np.sum(res[2])
sim_min = res[3]

print("---")
print("Spot servers were working for", spot_min, "minutes (",spot_min/sim_min*100,"% of simulation time)")
print("Additional on demand servers were working for", nod_min, "minutes (",nod_min/sim_min*100,"% of simulation time)")
print("For", sim_min-nod_min-spot_min, "minutes only 300 on-demand servers were working (",(sim_min-nod_min-spot_min)/sim_min*100,"% of simulation time)")

#plot
fig, ax1 = plt.subplots()

plt.suptitle("\n".join(wrap('Third scenario: 300 reserved on-demand servers, spot instances only and on-demand servers when spot unavaible', 60)))

max_profit = max(avg_profit)
ax2 = ax1.twinx()
ax1.plot(avg_profit,range(0,360,10), 'g-')
ax1.plot(max_profit,avg_profit.index(max_profit)*10,'ro')
ax1.annotate((int(max_profit),avg_profit.index(max_profit)*10),xy=(max_profit,avg_profit.index(max_profit)*10),xytext=(max_profit-300,avg_profit.index(max_profit)*10),arrowprops=dict(facecolor='black', shrink=0.05))
ax2.plot(avg_profit,avg_denials, 'b-')
ax2.plot(max_profit,avg_denials[avg_profit.index(max_profit)],'ro')
ax2.annotate((int(max_profit),int(avg_denials[avg_profit.index(max_profit)])),xy=(max_profit,avg_denials[avg_profit.index(max_profit)]),xytext=(max_profit-300,avg_denials[avg_profit.index(max_profit)]),arrowprops=dict(facecolor='black', shrink=0.05))

ax1.set_xlabel('Avg total profit')
ax1.set_ylabel('no of od servers', color='g')
ax2.set_ylabel('MM denailas', color='b')

plt.show()

#%%

