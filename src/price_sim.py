# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 22:24:55 2018

@author: kamila
"""
#%%
import random
import matplotlib.pyplot as plt
import numpy as np
import datetime
import csv
from collections import namedtuple

#%%
history = []
HistoryRow = namedtuple('HistoryRow', ['timestamp', 'price'])
history_file = 'C:/pth/ceny_spot_all.txt'
with open(history_file, "r") as f:
    file = csv.DictReader(f, delimiter='\t')
    for row in file:
        hist = HistoryRow(datetime.datetime.strptime(row['time'], "%Y-%m-%dT%H:%M:%S.%fZ"), price=float(row['price']))
        history.append(hist)
        
history = [h for h in history if h.timestamp.date() < datetime.date(2017, 11, 28)]

#%%

history_sorted = sorted(history)
prices = [h.price for h in history_sorted]
history_diff = np.diff(prices)
history_diff_non_zero = [h for h in history_diff if h!=0]
#%%
start_date = datetime.datetime.strptime(\
"2017-11-21 4:00:00","%Y-%m-%d %H:%M:%S")
end_date = datetime.datetime.strptime(\
"2017-11-21 20:00:00","%Y-%m-%d %H:%M:%S")

t1 = end_date-start_date
n_minutes = int(t1.total_seconds()/60)

#%%
#n_minutes = 16*60
spot = []
random.seed(10)
spot.append(random.choice(prices))
for i in range(0,n_minutes):
    spot.append(spot[-1]+random.choice(history_diff_non_zero))
plt.plot(spot)
plt.show()
    
#%%
import matplotlib.pyplot as plt
prices_day = [h.price for h in history_sorted if h.timestamp.date() == datetime.date(2017, 11, 6) ]
plt.plot(prices_day)
plt.show()

#%%
hist_day_diff = np.diff(prices_day)
plt.plot(hist_day_diff) 
plt.show()

#%%
import csv
ofile =  open('C:/pth/ceny_spot_sim.txt', "w")
ofilewriter = csv.writer(ofile, delimiter='\t')
ofilewriter.writerow(['time','zone','type','price'])
format = "%Y-%m-%dT%H:%M:%S.%fZ"

for i in reversed(range(len(spot))):
    t1 = start_date+datetime.timedelta(seconds=60*i)
    t2 = t1.strftime(format)
    ofilewriter.writerow([\
        t2, "sim",\
        "sim",spot[i]])
ofile.close()

#%%
