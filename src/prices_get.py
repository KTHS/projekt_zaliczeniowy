# -*- coding: utf-8 -*-
"""
@author: Kamila Kitowska, Katarzyna Pękala
"""

# %%
import boto.ec2
conn = boto.ec2.connect_to_region("us-east-1",\
   aws_access_key_id='AKIAJGBLCUFPEHFLTPGQ',
  	aws_secret_access_key=\
	'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')
# %%
import_start_date = '2017-11-27T00:30:00.000Z' 
import_end_date = '2017-11-28T00:00:00.000Z'

history = conn.get_spot_price_history(
start_time=import_start_date, end_time=import_end_date, instance_type="c4.4xlarge",
product_description="Linux/UNIX",
availability_zone="us-east-1d")

"""
for h in history:
    print (h.timestamp,h.availability_zone,\
         h.instance_type,h.price)
"""
# %%
import csv
ofile =  open('ceny_spot.txt', "w")
ofilewriter = csv.writer(ofile, delimiter='\t')
ofilewriter.writerow(['time','zone','type','price'])
for h in history:
    ofilewriter.writerow([\
        h.timestamp, h.availability_zone,\
        h.instance_type,h.price])
ofile.close()
