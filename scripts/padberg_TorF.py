'''
This script takes in the order ID and Box ID as input.
It then checks if the orders can be filled inside the boxes.
Returns the True or False by performing the Padberg Check.
The results are written in padberg_results.csv
'''


# importing the packages
import pulp
import pandas as pd
import random
import time

# setting the seed
random.seed(10000)

# importing the functions
from boxsize_opt.product import Product
from boxsize_opt.box import Box
from boxsize_opt.padberg import *

# importing the order data and probable box data
box = pd.read_csv("data/Box Volumes.csv")
df = pd.concat([pd.read_csv("data/Orderdata1.csv",sep='|'),
                pd.read_csv("data/Orderdata2.csv",sep='|')])
boxtype = box['SKU_ID'].tolist()
df = df[df['v_box_type'].isin(boxtype)]

# making a unique order ID list
x = df['Order_id'].tolist()
x = list(set(x))

# storing sample order IDs and box IDs as list and dictionary respectively
orderid = random.sample(x,100000)
suggested_box = []
for _ in orderid:
    suggested_box.append(df[df['Order_id']==_]['v_box_type'].iloc[0])
boxdim = box.set_index('SKU_ID').T.to_dict('list')

result = []
order_size = []
run_time = []
#solver = pulp.getSolver('HiGHS_CMD')
solver = pulp.getSolver('GUROBI_CMD', msg=False, timeLimit=30)
# doing the Padberg check to all the orders in the sample
for i in range(0,len(orderid)):
    depth = df[df['Order_id'] == orderid[i]]['each_depth'].tolist()
    width = df[df['Order_id'] == orderid[i]]['each_width'].tolist()
    height = df[df['Order_id'] == orderid[i]]['each_height'].tolist()
    pb = boxdim[suggested_box[i]]
    order = []
    # adding all the products of the order to the list
    for j in range(0,len(depth)):
        order.append(Product(j+1,depth[j],width[j],height[j]))
    # carrying out Padberg Check on the eligible boxes 
    start = time.time()
    check = padberg_check(order,Box('pb',pb[0],pb[1],pb[2]),solver=solver)
    result.append(check)
    order_size.append(len(order))
    run_time.append(time.time()-start)
    print(i+1)

print(sum([1 if i==True else 0 for i in result])*100/len(result))

# exporting the result to a csv file
resultdf = pd.DataFrame()
resultdf['orderId'] = orderid
resultdf['suggested_box'] = suggested_box
resultdf['Order_Size'] = order_size
resultdf['Run_Time'] = run_time
resultdf['Padberg_Result'] = result
resultdf.to_csv('data/output/lakeland_data_padberg_check.csv')