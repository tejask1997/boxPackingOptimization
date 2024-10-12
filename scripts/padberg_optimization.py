from boxsize_opt.optimization_model import boxOptimizationCheck
import pandas as pd
import ast
import pulp
import time
#import gurobipy


def parse_list(string):
    try:
        return ast.literal_eval(string)
    except (SyntaxError, ValueError):
        return []

numberOfMaxBoxes = 12
boxAnalysis = pd.read_csv("data/output/padberg_results.csv", converters={'eligibleBoxesId': parse_list, 'Padberg_Result': parse_list})
probableBoxes = pd.read_csv("data/output/probable_boxes.csv")

#print(boxAnalysis.dtypes)

#numberOfTotalOrder = boxAnalysis.shape[0]

#boxAnalysis = boxAnalysis.sample(n=numberOfTotalOrder, random_state=28)
#boxAnalysis = boxAnalysis[boxAnalysis['PadbergCheck'] == False]
boxAnalysis = boxAnalysis[boxAnalysis['Padberg_Result'].apply(lambda x: len(x) > 0)]

numberOfTotalOrder = boxAnalysis.shape[0]
#boxAnalysis = boxAnalysis.head(numberOfTotalOrder)
boxAnalysis.to_csv("data/output/temp.csv", index = False)

boxAnalysisDict = dict(zip(boxAnalysis.orderId, boxAnalysis.eligibleBoxesId))
boxAnalysisDict = dict(zip(boxAnalysis.orderId, boxAnalysis.Padberg_Result))
boxVolumeAnalysisDict = dict(zip(boxAnalysis.orderId, boxAnalysis.orderVolume))

eligibleBox = []
for index, row in probableBoxes.iterrows():
    eligibleBox.append(row["PB_ID"])


optimizationStartTime = time.time()

#solver=pulp.getSolver('HiGHS_CMD')
solver = pulp.GUROBI()

#x, y, optimalCost = boxOptimizationCheck(boxVolume, eligibleBox, orderEligibleBox, numberOfMaxBoxes, solver)
optimalBox, optimalOrderBox, optimalCost, boxVolume, orderEligibleBox = boxOptimizationCheck(boxAnalysis, probableBoxes, numberOfMaxBoxes, solver, False, True)
#x, y, optimalCost = boxOptimizationCheck(boxVolume, eligibleBox, orderEligibleBox, numberOfMaxBoxes)
print("Box Details:")
print(f"Number of Boxes: {len(optimalBox)}")
print(f"List of Boxes: {optimalBox}")
print("Order Details:")
print(f"Box for each order: {optimalOrderBox}")
print(f"Optimal Cost: {optimalCost}")

optimizedBox = {}
totalVolume = 0
packingEfficieny = 0

for order, boxes in boxAnalysisDict.items():

    eligibleBoxes = [box for box in boxes if box in optimalBox]
    if eligibleBoxes:
        # Find the box with the lowest volume
        lowestVolumeBox = min(eligibleBoxes, key=lambda box: boxVolume[box])
        optimizedBox[order] = lowestVolumeBox
        totalVolume += boxVolume[lowestVolumeBox]
        packingEfficieny += (boxAnalysis[boxAnalysis["orderId"] == order]["orderVolume"].iloc[0])/boxVolume[lowestVolumeBox]
        #print(packingEfficieny)        

packingEfficieny = round(packingEfficieny/numberOfTotalOrder, 2)
print(f"Packing Efficiency: {packingEfficieny}")


print(f"Time required to complete: {(time.time() - optimizationStartTime)/60}") 