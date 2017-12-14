# -*- coding: utf-8 -*-
"""
Created on Thu Nov 09 16:12:55 2017

@author: kamila

"""
import datetime

class Ec2Simulator(object):
    def __init__(self, history_file=None):
        
        if history_file == None: #jesli nie podano pliku otwieramy polaczenie i sciagamy dane
            import boto.ec2
            conn = boto.ec2.connect_to_region("us-east-1",aws_access_key_id='AKIAJGBLCUFPEHFLTPGQ',aws_secret_access_key='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')
            self.history = conn.get_spot_price_history(\
                               instance_type="c4.4xlarge",\
                               product_description="Linux/UNIX",\
                               availability_zone="us-east-1d")
        else:
            from collections import namedtuple
            import csv
            HistoryRow = namedtuple('HistoryRow', ['timestamp', 'price'])
            self.history = []

            with  open(history_file, "r") as f:
                file = csv.DictReader(f, delimiter='\t')
                for row in file:
                    hist = HistoryRow(row['time'], price=float(row['price']))
                    self.history.append(hist)
                    
        self.timestamps = [datetime.datetime.strptime(h.timestamp, "%Y-%m-%dT%H:%M:%S.%fZ") for h in self.history]
        
        
    def _get_spot(self,t):
        
        if t > self.timestamps[0]:
            print("zbyt malo danych w historii")
            return None
        smaller_ts = max(dt for dt in self.timestamps if dt <= t)
        i = self.timestamps.index(smaller_ts)
        return self.history[i].price
    
    def _terminate(self,t,bid):
        t0 = t
        t1 = t + datetime.timedelta(hours=1)
        
        if t1 > self.timestamps[0]:
            t1 = self.timestamps[0]
            
        youngest = max(dt for dt in self.timestamps if dt <= t0)
        oldest = max(dt for dt in self.timestamps if dt <= t1)
        
        if bid < max([self.history[i].price for i in range(self.timestamps.index(oldest),self.timestamps.index(youngest)+1)]):
            status = True
            sindex = max(i for i in range(self.timestamps.index(oldest),self.timestamps.index(youngest)+1) if self.history[i].price > bid)
            start = self.timestamps[sindex]
            
            if bid > min([self.history[i].price for i in range(0,sindex+1)]):    
                eindex = max(i for i in range(0,sindex+1) if self.history[i].price <= bid)
                end = self.timestamps[eindex]
            else:
                end = self.timestamps[0]
        else:
            status = False
            start = None
            end = None
          
        return {'status':status, 'start':start ,'end':end }
        
    
    
    
    def estimate_cost_d (self, bid_price, zone_machine, start_datetime, end_datetime=None,
    warmup_time_s=0,request_time_s=None,request_sim_runs=None,single_sim_time_s=1,use_full_last_hour=True,stop_on_terminate = False):
        
    # simulation time - poprawić żeby liczyło dokładnie koszyt za czas symulacji
    # co jesli czas symulacji wyjdzie poza historie?
        
    # check date parameters
        if start_datetime < min(i
            for i in self.timestamps) or start_datetime > end_datetime:
          raise ValueError('Wrong date parameter')

        if end_datetime > self.timestamps[0]:
          raise ValueError('Wrong end date parameter') 
    
        # initial values
        cost = 0        
        t0 = start_datetime
        end_of_sim = False
        server_working_time = 0
        warmup_no = 1                       

        # simulation time       
        if end_datetime == None:
            end_datetime = self.timestamps[0] #jesli nie podano czasu zakonczenia przyjmujemy ostatni dostepny w historii
        
        if request_time_s == None and request_sim_runs == None:
            request_time_s = (end_datetime-t0).total_seconds()
        else:
            if request_time_s == None:
                request_time_s = request_sim_runs * single_sim_time_s                 
    
        # cost calculation
        while t0 < end_datetime and not end_of_sim:
            print(cost)
            print(t0)
            if not self._terminate(t0,bid_price)['status']:
                print(self._get_spot(t0))
                cost += self._get_spot(t0)
                t0 = t0 + datetime.timedelta(hours=1)
                server_working_time = server_working_time + 3600 - warmup_no * warmup_time_s
                warmup_no = 0
        
            else:
                if stop_on_terminate:
                    end_datetime = t0
                else:
                    print("termination")
                    server_working_time = server_working_time + (self._terminate(t0,bid_price)['start'] - t0).total_seconds()
                    warmup_no = 1
                    t0 = self._terminate(t0,bid_price)['end']
            if server_working_time >= request_time_s:
                end_of_sim = True
            print(cost,"\n")    

           
      
        return cost
        
