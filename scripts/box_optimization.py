from boxsize_opt.optimization_model import boxOptimizationCheck
import pandas as pd
import ast
import pulp
import time
#import gurobipy
from boxsize_opt.utils import find_minimal_sets


def parse_list(string):
    try:
        return ast.literal_eval(string)
    except (SyntaxError, ValueError):
        return []

numberOfMaxBoxes = 5

boxAnalysis = pd.read_csv("data/output/padberg_results.csv", converters={'eligibleBoxesId': parse_list, 'eligibleBoxesPackingEfficiency': parse_list, 'Padberg_Result' : parse_list, 'Padberg_Packing_Efficiency' : parse_list})
probableBoxes = pd.read_csv("data/output/probable_boxes.csv")

numberOfOrders = 100

boxAnalysis = boxAnalysis.sample(n=numberOfOrders, random_state=28)

eligibleBox = []
for index, row in probableBoxes.iterrows():
    eligibleBox.append(row["PB_ID"])

boxVolume = dict(zip(probableBoxes.PB_ID, probableBoxes.PB_Volume))
orderEligibleBox= dict(zip(boxAnalysis.orderId, boxAnalysis.eligibleBoxesId))

boxLists = boxAnalysis.eligibleBoxesId
minBoxLists = find_minimal_sets(boxLists, verbose=True)
optimizationStartTime = time.time()

#solver=pulp.getSolver('HiGHS_CMD', keepFiles=False, msg = 1)
#pulp.LpSolverDefault.keepFiles = False
#solver=pulp.getSolver('HiGHS_CMD')
#solver = pulp.HiGHS_CMD(keepFiles= False, msg= True)


#solver=pulp.getSolver('HiGHS_CMD')
solver = pulp.GUROBI()

#x, y, optimalCost = boxOptimizationCheck(boxVolume, eligibleBox, orderEligibleBox, numberOfMaxBoxes, solver)
optimalBox, optimalOrderBox, optimalCost, _, _ = boxOptimizationCheck(boxAnalysis, probableBoxes, minBoxLists, numberOfMaxBoxes, 2, solver, False)
#x, y, optimalCost = boxOptimizationCheck(boxVolume, eligibleBox, orderEligibleBox, numberOfMaxBoxes)
print("Box Details:")
print(f"Number of Boxes: {len(optimalBox)}")
print(f"List of Boxes: {optimalBox}")
print("Order Details:")
print(f"Box for each order: {optimalOrderBox}")
print(f"Optimal Cost: {optimalCost}")

print(f"Time required to complete: {(time.time() - optimizationStartTime)/60}") 
