'''
This script takes in the eligible boxes identified by volume fill as input.
It then checks if the orders can be filled inside the eligible boxes.
Returns the set of boxes that can be used for each order by performing the Padberg Check.
The results are written in padberg_results.csv
'''

# importing the packages
import pulp
import pandas as pd
import time
import numpy as np
import datetime
import sys
from typing import Tuple, List

# importing the functions
from boxsize_opt.product import Product
from boxsize_opt.box import Box

from boxsize_opt.filter import get_eligible_boxes, probable_box

print(f'Command line args: {sys.argv}')

# importing the order data and probable box data
print('Reading data...')
df = pd.read_csv("data/output/merged_order_data.csv")
eligibleboxes = pd.read_csv("data/output/probable_box_data_analysis.csv")
#eligibleboxes = eligibleboxes.head(100)
#eligibleboxes['eligibleBoxesId'] = eligibleboxes['eligibleBoxesId'].apply(eval)

if len(sys.argv) == 1:
    filter_orders = False
    start, n_orders = 0, len(eligibleboxes)
else:
    assert len(sys.argv) == 3, "Must provide row start index and number of orders"
    filter_orders = True
    start = int(sys.argv[1])
    n_orders = int(sys.argv[2])



# sorts the boxes in ascending order of volume and returns corresponding packing efficiencies
def volume_sort(boxes: List[str], ordervol: float) -> Tuple[List[str], List[float]]:
    volume = []
    for b in boxes:
        dummy = probable_box(b)
        volume.append(dummy[1]*dummy[2]*dummy[3])
    sort_order = np.argsort(volume).tolist()
    volume = sorted(volume)
    return [boxes[a] for a in sort_order], [ordervol/volume[p] for p in range(0,len(volume))]


# printing start time
start_time = time.time()
#print(start_time)

# creating a text file to store the results
if filter_orders:
    txt_fn = f"data/output/padberg_results_{start}_{n_orders}.txt"
    csv_fn = f'data/output/padberg_results_{start}_{n_orders}.csv'
else:
    txt_fn = "data/output/padberg_results.txt"
    csv_fn = 'data/output/padberg_results.csv'

print(f'Results will be written to {txt_fn} and {csv_fn}', flush=True)

with open(txt_fn, "a") as file:
    file.write(f"{'index'}\t{'orderId'}\t{'orderVolume'}\t{'eligibleBoxesId'}\t{'Padberg_Result'}\t{'Packing_Efficiency'}\n")

# defining the solver
#solver = pulp.getSolver('HiGHS_CMD')
solver = pulp.getSolver('GUROBI_CMD', msg=False, timeLimit=15)

# defining resultdf to store the output
column_names = ["orderId", "orderVolume", "eligibleBoxesId", "eligibleBoxesPackingEfficiency", 
                "mostEligibleBox", "mostEligibleBoxVolume", "mostEligibleBoxPackingEfficiency",
                "Padberg_Result", "Padberg_Packing_Efficiency"] 
resultdf = pd.DataFrame(columns = column_names)

print('Started the Padberg Check at',datetime.datetime.now(),'\nThis might take several hours...', flush=True)
# doing the Padberg check to all the orders in the sample
for i, row in eligibleboxes.iterrows():

    if filter_orders:
        if i < start or i >= start + n_orders:
            continue


    # writing the imported data to the result df
    for c in range(0,len(column_names)-2):
        resultdf.loc[i, column_names[c]] = row[column_names[c]]
    
    # storing the dims in lists 
    prod_df = df[df['Order_id'] == row['orderId']]
    depth = prod_df['each_depth'].tolist()
    width = prod_df['each_width'].tolist()
    height = prod_df['each_height'].tolist()
    order = []
    
    # adding all the products of the order to the list
    for j in range(0,len(depth)):
        order.append(Product(j+1,depth[j],width[j],height[j]))
    
    box_names = eval(row['eligibleBoxesId'])

    boxes = get_eligible_boxes(order, box_names, use_dim_check=True, solver=solver)

    boxes, boxPE = volume_sort(boxes, row['orderVolume'])
    resultdf.loc[i, 'Padberg_Result'] = boxes
    resultdf.loc[i, 'Padberg_Packing_Efficiency'] = boxPE

    # writing the output in a text file
    # with open(txt_fn, "a") as file:
    #     file.write(f"{i}\t{row['orderId']}\t{row['orderVolume']}\t{box_names}\t{boxes}\t{boxPE}\n")
    
    # printing the progress
    if (i+1) % 200 == 1:
        print(f'Order {i+1} out of {n_orders} ({100*(i+1)/n_orders:.1f}% done)', flush=True)


# exporting the result to a csv file
resultdf.to_csv(csv_fn, index = False)

# Time Taken
print("Process finished --- %s seconds ---" % (time.time() - start_time))