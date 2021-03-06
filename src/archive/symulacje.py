# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 20:11:49 2017

@author: kamila
"""
# %%

import os
os.chdir("D:/Big Data/projekt zaliczeniowy Python/")
# %%
import datetime
import ec2_spot_pricing_simulator as ecs

import importlib
importlib.reload(ecs)

start = datetime.datetime.strptime(\
"2017-11-21 10:00:00","%Y-%m-%d %H:%M:%S")
end = datetime.datetime.strptime(\
"2017-11-21 20:00:00","%Y-%m-%d %H:%M:%S")

sim = ecs.Ec2Simulator('ceny_spot.txt')
result = sim.estimate_cost_d(0.29,\
start,end,single_sim_time_s=3600)

print("--------- \nCost = ", result[0])
print("---------")
print(result[1])
print("---------")
print(result[2])


