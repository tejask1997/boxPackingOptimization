"""
probable_boxes.py

This script generates a list of probable box options based on specified dimensions and constraints.
It then performs packing feasibility analysis for a subset of orders using the probable boxes.
The analysis results are saved to a CSV file.

Input:
- The script requires the boxsize_opt package and its dependencies.
- The input data files 'sampled_data.csv' and 'aggregated_sampled_data.csv' must be present in the 'data' directory.

Output:
- 'probable_boxes.csv': A CSV file containing the generated probable box options.
- 'probable_box_data_analysis.csv': A CSV file containing the packing feasibility analysis results for the orders.

"""

import pandas as pd
from boxsize_opt.box import Box
from boxsize_opt.product import Product
from boxsize_opt.packing import packingFeasibility
import time

print('Reading data...')
sampledData = pd.read_csv("data/output/sampled_data.csv")
aggregatedSampledData = pd.read_csv("data/output/aggregated_sampled_data.csv")


print('Generating boxes...')
probableDepth = [i for i in range(20,120,5)]
probableWidth = [i for i in range(10,120,5)]
probableHeight = [i for i in range(5,120,5)]

probableBoxesDF = pd.DataFrame(columns=["PB_ID", "PB_Depth", "PB_Width", "PB_Height", "PB_Volume"])
probableBoxes = []
probableBoxesCount = 0
for d in probableDepth:
    for w in probableWidth:
        for h in probableHeight:
            if d >= w and w >= h and d + 2*w + 2*h <= 225:
                probableBoxesCount += 1
                probableBoxName = "PB_" + str(d) + "_" + str(w) + "_" + str(h)                
                #print(probableBoxName)
                box = Box(probableBoxName, d, w, h)
                probableBoxes.append(box)
                probableBoxesDF.loc[probableBoxesCount, 'PB_ID'] = probableBoxName
                probableBoxesDF.loc[probableBoxesCount, 'PB_Depth'] = d
                probableBoxesDF.loc[probableBoxesCount, 'PB_Width'] = w
                probableBoxesDF.loc[probableBoxesCount, 'PB_Height'] = h
                probableBoxesDF.loc[probableBoxesCount, 'PB_Volume'] = d*w*h

probableBoxesDF.to_csv("data/output/probable_boxes.csv", index=False)

print("Number of Probable Box Generated: ", probableBoxesCount)

print('Calculating eligible boxes...')
start_time = time.time()

boxAnalysisPB = pd.DataFrame(columns=["orderId", "orderVolume", "eligibleBoxesId", "eligibleBoxesPackingEfficiency", "mostEligibleBox", "mostEligibleBoxVolume", "mostEligibleBoxPackingEfficiency"])
#print(dataDF)
for index, row in aggregatedSampledData.iterrows():
    if index % 1000 == 1:
        print(f'Order {index} out of {len(aggregatedSampledData)} ({100*index/len(aggregatedSampledData):.1f}% done)')
    #print(index)
    currentOrderId = int(row['Order_id'])
    currentOrderVolume = round(row['orderVolume'],2)

    products = []
    productCurrentOrder = sampledData[sampledData['Order_id'] == currentOrderId]

    for index, row in productCurrentOrder.iterrows():
        product = Product(row['SKU_id'], row['each_depth'], row['each_width'], row['each_height'])
        products.append(product)
    
    eligibleBoxes, eligibleBoxesId, eligibleBoxesPackingEfficiency, mostEligibleBox, mostEligibleBoxVolume = packingFeasibility(currentOrderId, currentOrderVolume, products, probableBoxes)

    boxAnalysisPB.loc[index, 'orderId'] = currentOrderId
    boxAnalysisPB.loc[index, 'orderVolume'] = currentOrderVolume
    boxAnalysisPB.loc[index, 'eligibleBoxesId'] = eligibleBoxesId
    boxAnalysisPB.loc[index, 'eligibleBoxesPackingEfficiency'] = eligibleBoxesPackingEfficiency
    boxAnalysisPB.loc[index, 'mostEligibleBox'] = mostEligibleBox
    boxAnalysisPB.loc[index, 'mostEligibleBoxVolume'] = mostEligibleBoxVolume
    
    boxAnalysisPB.loc[index, 'mostEligibleBoxPackingEfficiency'] = currentOrderVolume/mostEligibleBoxVolume if mostEligibleBoxVolume != 0 else 0

boxAnalysisPB.to_csv("data/output/probable_box_data_analysis.csv", index=False)

print("Process finished --- %s seconds ---" % (time.time() - start_time))
