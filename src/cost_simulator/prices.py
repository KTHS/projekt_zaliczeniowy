# -*- coding: utf-8 -*-
# rynek serwerow c3.4xlarge jest niepłynny -> zamieniłam na c4.4xlarge

# %%
import boto.ec2
conn = boto.ec2.connect_to_region("us-east-1",\
   aws_access_key_id='AKIAJGBLCUFPEHFLTPGQ',
  	aws_secret_access_key=\
	'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')
# %%
start = '2017-11-20T00:00:00.000Z' 
end = '2017-11-22T00:10:00.000Z'

history = conn.get_spot_price_history(
start_time=start, end_time=end, instance_type="c4.4xlarge",
product_description="Linux/UNIX",
availability_zone="us-east-1d")

"""
for h in history:
    print (h.timestamp,h.availability_zone,\
         h.instance_type,h.price)
"""
# %%
import csv
ofile =  open('d:/Big Data/projekt zaliczeniowy Python/ceny_spot.txt', "w")
ofilewriter = csv.writer(ofile, delimiter='\t')
ofilewriter.writerow(['time','zone','type','price'])
for h in history:
    ofilewriter.writerow([\
        h.timestamp, h.availability_zone,\
        h.instance_type,h.price])
ofile.close()
