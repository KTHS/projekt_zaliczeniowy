# -*- coding: utf-8 -*-
"""
@author: Kamila Kitowska, Katarzyna Pękala
"""

#%%
my_path = ""

#%%
#libraries 
import os
os.chdir(my_path)
import importlib
import datetime
import numpy as np
import scenarios as scn
import matplotlib.pyplot as plt
from textwrap import wrap
#importlib.reload(scn)

#simulate spot prices:
#import price_sim
#it generates ceny_spot_sim.txt file

#get spot prices:
#import prices_get
#it generates ceny_spot.txt file

#%%
# initial values
start = datetime.datetime.strptime("2017-11-21 10:00:00","%Y-%m-%d %H:%M:%S")
end = datetime.datetime.strptime("2017-11-21 20:00:00","%Y-%m-%d %H:%M:%S")
ec2_od = 300 # amount of on-demand servers, already bought
ec2_price_od_old = 0.42 # price of bought on-demand servers, per server per hour
users_per_server = 100 # number of concurrent users per server
revenue = 0.00021   #per user per minute
demand_avg = 40000 #predicted avg. users per minute
demand_std_dev = 5000 #predicted avg. users per minute 
ec2_price_od = 0.84 # price of new on-demand servers, per server per hour
ec2_od_new = 0 # variable for new on-demand servers
ec2_spot = 0 # variable for new spot server

# project parameters
n_of_sim = 500 # number of simulations
availability_level = 0.99 # how many users/min must have access
availability_no_sim = 0.9 # how many simulations must meet availability level 
bid = 0.25 # bid
spot_prices_s = 1 #spot prices source: 1 - simulation, 0 - historical

if spot_prices_s == 1:
    spot_file = "ceny_spot_sim.txt"
else:
    spot_file = "ceny_spot.txt"    
#%%    
# scenario "only on demand servers"

avg_profit = []
avg_denials = []
final_result = ()

# simulations for j additional on-demand servers
for j in range(200, 300, 10):
    res = scn.first_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,j,
                         ec2_od, users_per_server, ec2_price_od_old, 
                         ec2_price_od, revenue, availability_level)
    avg_res = np.array(res[0]).mean(axis=0) 
    avg_profit.append(avg_res[0]) 
    avg_denials.append(avg_res[1]/1000)
    print("additional on-demand servers =",j," | avg total profit =", 
      avg_res[0],"| avg amount of denials-of-access", avg_res[1],
      "| availability ", avg_res[2]*100,"% | availability cond. counter",res[1])
    if res[1]/n_of_sim>availability_no_sim and scn.is_empty(final_result):
        final_result = (avg_res,res[1],j)

# final result of simulations
if scn.is_empty(final_result):
    print("\n\nAvailability condition of",availability_level*100,"% in",
          availability_no_sim*n_of_sim,"out of",n_of_sim,
          "simulations wasn't satisfied.")
else:          
    print("\nFINAL RESULT: \nAdditional on-demand servers =",final_result[2],
          " | avg total profit =", final_result[0][0],
          "| avg amount of denials-of-access", final_result[0][1],
          "| availability ", final_result[0][2]*100,"% \nIn ",final_result[1],
          "simulations out of",n_of_sim,"availability condition of",
          availability_level,"was met.")

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
# simulation of second scenario
    
avg_profit = []
avg_denials = []
final_result = ()
for j in range(100, 360, 10):
    res = scn.second_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,j,
                          spot_file, bid, users_per_server, ec2_od, ec2_od_new,
                          ec2_price_od,revenue, availability_level, 
                          ec2_price_od_old,my_path)
    avg_res = np.array(res[0]).mean(axis=0)
    avg_profit.append(avg_res[0]) 
    avg_denials.append(avg_res[1]/1000)
    print("additional spot servers =",j," | avg tot. profit =", 
      avg_res[0],"| avg amount of denials", avg_res[1],"| availability ", 
      avg_res[2]*100,"% | availability cond. counter",res[3])
    if res[3]/n_of_sim>availability_no_sim and scn.is_empty(final_result):
        final_result = (avg_res,res[3],j)

if scn.is_empty(final_result):
    print("\n\nAvailability condition of",availability_level*100,"% in",availability_no_sim*n_of_sim,"out of",n_of_sim,"simulations wasn't satisfied.")
else:          
    print("\nFINAL RESULTS: \nadditional spot servers =",final_result[2]," | avg total profit =", 
      final_result[0][0],"| avg amount of denials-of-access", final_result[0][1],
      "| availability ", final_result[0][2]*100,"% \nIn ",final_result[1],
      "simulations out of",n_of_sim,"availability condition of",availability_level,"was met.")

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
#third scenario
# "old" on demand servers + spot instances + on-demand servers when spot unavaible    
# on-demand needs 2 min for startup

avg_profit = []
avg_denials = []
final_result = ()
for j in range(0, 200, 10):
    res  = scn.third_scenario(start,end,demand_avg,demand_std_dev,n_of_sim,j, 
                              spot_file, bid, users_per_server, ec2_od, 
                              ec2_price_od, ec2_price_od_old, revenue, 
                              availability_level, my_path)
    avg_res = np.array(res[0]).mean(axis=0)
    avg_profit.append(avg_res[0]) 
    avg_denials.append(avg_res[1]/1000)
    print("additional spot/on-demand servers =",j," | avg tot. profit =", 
      avg_res[0],"| avg amount of denials", avg_res[1],"| availability ", 
      avg_res[2]*100,"% | availability cond. counter",res[4])
    if res[4]/n_of_sim>availability_no_sim and scn.is_empty(final_result):
        final_result = (avg_res,res[4],j)

if scn.is_empty(final_result):
    print("\n\nAvailability condition of",availability_level*100,"% in",availability_no_sim*n_of_sim,"out of",n_of_sim,"simulations wasn't satisfied.")
else:          
    print("\nFINAL RESULTS: \nAdditional spot servers =",final_result[2]," | avg total profit =", 
      final_result[0][0],"| avg amount of denials-of-access", final_result[0][1],
      "| availability ", final_result[0][2]*100,"% \nIn ",final_result[1],
      "simulations out of",n_of_sim,"availability condition of",availability_level,"was met.")

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

