"""
This script reads raw order data, processes the box types, and filters out irrelevant/problematic orders. The resulting
dataframe is then written to a new CSV file.

Input:
- The input data files 'Orderdata1.csv', 'Orderdata2.csv' and 'CurrentBoxOptionsUnique.csv' must be present in the 'data' directory.

Output:
- 'processed_order_data.csv': A CSV file containing the merged order data file joined with box data.
- 'sampled_data.csv': A CSV file containing sampled data.
- 'aggregated_sampled_data.csv': A CSV file containing sampled data aggregated on Order_id.

"""

#TODO: Check with Alex how to handle duplicate data

import pandas as pd
import time

# Read data files
print('Loading order data files...')
orderData1 = pd.read_csv("data/input/Orderdata1.csv",sep='|')
orderData2 = pd.read_csv("data/input/Orderdata2.csv",sep='|')

# completeOrderData = orderData1.concat(orderData2)

print('Concatenating order data into one data frame...')
completeOrderData = pd.concat([orderData1, orderData2])

print('Calculating volume of every SKU...')
completeOrderData['productVolume'] = completeOrderData['each_depth'] * completeOrderData['each_width'] * completeOrderData['each_height']


print('Loading box data...')
boxData = pd.read_csv("data/input/CurrentBoxOptionsUnique.csv")
boxData['boxVolume'] = boxData['EACH_DEPTH'] * boxData['EACH_WIDTH'] * boxData['EACH_HEIGHT']


# Altering dimensions of 2 products as per discussion with Alex
print('Fixing dimensions of SKU 62472 and 74135...')
completeOrderData.loc[completeOrderData['SKU_id'] == "62472", 'each_width'] = 0.4
completeOrderData.loc[completeOrderData['SKU_id'] == "74135", 'each_height'] = 15




# Merging the 9567 and 9569 series v_box_type
print('Merging the 9567 and 9569 series v_box_type...')
completeOrderData.loc[completeOrderData['v_box_type'] == "9567H", 'v_box_type'] = "9567"
completeOrderData.loc[completeOrderData['v_box_type'] == "9567I", 'v_box_type'] = "9567"
completeOrderData.loc[completeOrderData['v_box_type'] == "9567J", 'v_box_type'] = "9567"
completeOrderData.loc[completeOrderData['v_box_type'] == "9569H", 'v_box_type'] = "9569"
completeOrderData.loc[completeOrderData['v_box_type'] == "9569I", 'v_box_type'] = "9569"
completeOrderData.loc[completeOrderData['v_box_type'] == "9569J", 'v_box_type'] = "9569"

# Removing JUMBO and HEAVY BOXES


#print(completeOrderData.columns.values)

print('Removing orders with JUMBO, HEAVY BOXES and NA boxes...')
completeOrderData = completeOrderData[~completeOrderData['v_box_type'].isin(['JUMBO01', 'JUMBO02', 'JUMBO03', 'TOO HEAVY'])]
completeOrderData = completeOrderData[completeOrderData.v_box_type.notnull()]

# Merging with boxData to get Box Volume
print('Adding Box volume colume by merging with box data frame...')
completeOrderData['v_box_type']=completeOrderData['v_box_type'].astype(str)
boxData['SKU_ID']=boxData['SKU_ID'].astype(str)
completeOrderData = completeOrderData.merge(boxData[['SKU_ID', 'boxVolume']], left_on='v_box_type', right_on='SKU_ID', how='left')
completeOrderData.drop('SKU_ID', axis=1, inplace=True)
completeOrderData.rename(columns={'volume_x': 'productVolume', 'volume_y': 'boxVolume'}, inplace=True)

print('Calculating packing efficiency for each order...')
completeOrderData["packingEfficiency"] = completeOrderData["productVolume"]/completeOrderData["boxVolume"]
#print(completeOrderData.columns.values)

#print(completeOrderData.head())

# Processing the Order Data such that Depth always has the highest dimension for all products

print('Reordering dimenions of products to be non-increasing...')
start_time_1 = time.time()
for index, row in completeOrderData.reset_index().iterrows():
    #print(index)
    if not ((row['each_depth'] >= row['each_width']) and (row['each_width'] >= row['each_height'])):
        tempList = sorted([row['each_depth'], row['each_width'], row['each_height']], reverse= True)
        #aggregatedSampledData[i] = tempList[0]
        #aggregatedSampledData[i] = tempList[1]
        #aggregatedSampledData[i] = tempList[2]
        completeOrderData.loc[index, 'each_depth'] = tempList[0]
        completeOrderData.loc[index, 'each_width'] = tempList[1]
        completeOrderData.loc[index, 'each_height'] = tempList[2]

end_time_1 = time.time() - start_time_1

print('Saving data frame...', end='')
completeOrderData.to_csv("data/output/merged_order_data.csv", index=False)
print("Merged Order Data File Created!")

sample_size = 100000
seed=2803
print(f'Sampling subset of {sample_size} orders...')
distinctOrderIds = completeOrderData['Order_id'].drop_duplicates().sample(n=sample_size, random_state=seed)
sampledData = completeOrderData[completeOrderData['Order_id'].isin(distinctOrderIds)]

print('Saving sampled order data...', end='')
sampledData.to_csv("data/output/sampled_data.csv", index=False)
print("Sampled Data File Created")

print('Aggregrating sampled order data...')
aggregatedSampledData = sampledData.groupby('Order_id').agg({
    'Order_Month': 'first',  # Keep the first value of 'Order_Month' for each group
    'Order_day': 'first',  # Keep the first value of 'Order_day' for each group
    'SKU_id': 'count',  # Count the number of unique 'SKU_id' values for each group
    #'each_depth': 'sum',  # Sum the 'each_depth' values for each group
    #'each_width': 'sum',  # Sum the 'each_width' values for each group
    #'each_height': 'sum',  # Sum the 'each_height' values for each group
    'each_weight': 'sum',  # Sum the 'each_weight' values for each group
    'v_box_type': 'first',  # Keep the first value of 'v_box_type' for each group
    'productVolume': 'sum',  # Sum the 'volume' values for each group
    'boxVolume': 'first',  # Sum the 'volume' values for each group
    'packingEfficiency': 'sum'  # Sum the 'volume' values for each group
}).reset_index()

aggregatedSampledData = aggregatedSampledData.rename(columns={'productVolume': 'orderVolume'})

#FIXME:
print('Removing rows from aggregated data with > 100% packing efficiecny...')
packEffFeas=aggregatedSampledData['packingEfficiency']<=1
agg_nrows = aggregatedSampledData.shape[0]
feas_orders = sum(aggregatedSampledData['packingEfficiency']<=1)
aggregatedSampledData = aggregatedSampledData[packEffFeas]
print(f'...removed {agg_nrows - feas_orders} orders out of {agg_nrows}')

print('Saving aggregated data...')
aggregatedSampledData.to_csv("data/output/aggregated_sampled_data.csv", index=False)

print("Aggregated Sampled Data File Created")


print("Process 1 finished --- %s seconds ---" % (end_time_1))
