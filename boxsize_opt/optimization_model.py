from pulp import *
import pandas as pd
from datetime import datetime
from .utils import find_minimal_sets
import os

def boxOptimizationModel(boxVolume: dict, eligibleBox: list, orderEligibleBoxEfficiency:list, orderEligibleBox: dict, minBoxLists: list, numberOfMaxBoxes: int, optimizationMethod: int):
    
    x = []
    #x = pulp.LpVariable.dicts("x", eligibleBox, cat=LpBinary)
    x = pulp.LpVariable.dicts("x", eligibleBox, lowBound=0, upBound=1, cat='Integer')
    
    y = []

    numberOfConstraints = 0
    numberOfConstraints1 = 0
    numberOfConstraints2 = 0
    numberOfConstraints3 = 0
    numberOfConstraints4 = 0
        
    orderBox = []
    for o in orderEligibleBox:
        box = orderEligibleBox[o]
        for b in box:
            orderBox.append((o,b))
    #y = pulp.LpVariable.dicts("y", orderBox, cat=LpBinary)
    y = pulp.LpVariable.dicts("y", orderBox, lowBound=0, upBound=1, cat='Integer')
    
    
    #Objective Function for Packing Efficiency
    if optimizationMethod == 1:
        print("Optimizing for Maximum Packing Efficiency")
        prob = LpProblem("Box_Optimization_Problem", LpMaximize)
        prob += pulp.lpSum(y[order, b] * orderEligibleBoxEfficiency[order][orderEligibleBox[order].index(b)] for order in orderEligibleBox for b in orderEligibleBox[order])

    #Objective Function for Volume
    if optimizationMethod == 2:
        print("Optimizing for Minimum Volume")
        prob = LpProblem("Box_Optimization_Problem", LpMinimize)
        prob += lpSum(y[i] * boxVolume[i[1]] for i in y)

    
    print("Starting Constraint Creation!!!")

    #First Constraint - The box for each order should be present in the box list
    #print(f"First Constraint Started at: {datetime.now().strftime('%H:%M:%S')}")

    for o in orderEligibleBox:
        for b in orderEligibleBox[o]:
            prob += (y[o, b] <= x[b])
            numberOfConstraints += 1 
            numberOfConstraints1 += 1
            
    #Second Constraint: Each order should get a box
    #print(f"Second Constraint Started at: {datetime.now().strftime('%H:%M:%S')}")
    for orders in orderEligibleBox:
        prob += (lpSum(y[o, _] for (o,_) in y if o == orders) == 1)
        numberOfConstraints += 1
        numberOfConstraints2 += 1
        #print(f"Second Constraint: {numberOfConstraints2}") 
        
    #Third Constraint: Maximum Number of Boxes == numberOfMaxBoxes(12)
    prob += (lpSum(x[i] for i in x) <= numberOfMaxBoxes)
    numberOfConstraints3 += 1
    numberOfConstraints += 1

    #Fourth Constraint: Minimal Set Constraint
    for boxes in minBoxLists:
        prob += (lpSum(x[_] for _ in boxes) >= 1)
        numberOfConstraints += 1 
        numberOfConstraints4 += 1
            

    print(f"Optimization Model Created: {datetime.now().strftime('%H:%M:%S')}")
    
    #print(f"Number of Constraints1: {numberOfConstraints1}")
    #print(f"Number of Constraints2: {numberOfConstraints2}")
    #print(f"Number of Constraints3: {numberOfConstraints3}")
    #print(f"Number of Constraints4: {numberOfConstraints4}")
    #print(f"Number of Constraints: {numberOfConstraints}")
    return x, y, prob

def variableFileWrite(variableOutputFile, optimalVariables, optimalCost, orderBoxOutputFile, optimalOrderBox, boxVolume, optimalBox, optimalBoxOutputFile, stochasticFlag):
    if not stochasticFlag:
        print("Writing File!!!")
        with open(variableOutputFile, "w") as file:
            file.write(f"Variable Value = 1\n\n")
            for var in optimalVariables:
                var_name = var.name
                var_value = var.varValue
                if var_value == 1:        
                    file.write(f"{var_name}: {var_value}\n")
            file.write(f"\n\nAll variables:\n")
            for var in optimalVariables:
                var_name = var.name
                var_value = var.varValue
                file.write(f"{var_name}: {var_value}\n")
            print("Total Cost = ", optimalCost)
            file.write(f"Total Cost = {optimalCost}")
            
        print(f"Variable values saved to {variableOutputFile}.")

        with open(orderBoxOutputFile, "w") as file:
            file.write("Order_Id\tBox_Id\tBox_Volume\n")
            for key in optimalOrderBox:
                    file.write(f"{key}\t{optimalOrderBox[key]}\t{boxVolume[optimalOrderBox[key]]}\n")
        
        
        with open(optimalBoxOutputFile, "w") as file:
            file.write("Box_Id,Box_Volume\n")
            for box in optimalBox:
                    file.write(f"{box},{boxVolume[box]}\n")

        print(f"Order Box values saved to {orderBoxOutputFile}.")




#def boxOptimizationCheck(boxVolume: dict, eligibleBox: list, orderEligibleBox: dict, numberOfMaxBoxes: int, solver = None):
def boxOptimizationCheck(boxAnalysis: list, probableBoxes: list, minBoxLists:list, numberOfMaxBoxes: int, optimizationMethod: int, counter: int, solver = None, stochasticFlag = False):
    eligibleBox = []
    for index, row in probableBoxes.iterrows():
        eligibleBox.append(row["PB_ID"])

    boxVolume = dict(zip(probableBoxes.PB_ID, probableBoxes.PB_Volume))
    orderEligibleBox= dict(zip(boxAnalysis.orderId, boxAnalysis.Padberg_Result))
    
    orderEligibleBoxEfficiency = dict(zip(boxAnalysis.orderId, boxAnalysis.Padberg_Packing_Efficiency))


    x, y, prob = boxOptimizationModel(boxVolume, eligibleBox, orderEligibleBoxEfficiency, orderEligibleBox, minBoxLists, numberOfMaxBoxes, optimizationMethod)
    
    lpFilename = "data/solver_files/BoxOptimizationProblem_" + str(counter) + ".lp"
    mpsFilename = "data/solver_files/BoxOptimizationProblem_" + str(counter) + ".mps"

    prob.writeLP(lpFilename)
    #prob.writeMPS(mpsFilename)

    #pulp.LpSolverDefault.keepFiles = False
    if solver == None:
        prob.solve()
    else:
        prob.solve(solver)
        

    #print("Status:", LpStatus[prob.status])

    if prob.status != 1:
        print(f"Problem was not solved to optimality. Returned with status {prob.status}")
        #raise ValueError(f'Problem was not solved to optimality. Returned with status {prob.status}')
    else:
        print("Optimal Solution Found!!!")


    #Fetching Optimal Values
    xValues = {var: var.varValue for var in x.values()}
    yValues = {var: var.varValue for var in y.values()}

    optimalBox = []
    for x in xValues:
        if xValues[x] == 1:
            optimalBox.append(str(x)[2:])

    #print(optimalBoxes)
    optimalOrderBox = {}
    for y in yValues:
        if yValues[y] == 1:
            orderId = str(y).split("(")[1].split(",")[0]
            boxId = str(y).split("(")[1].split("'")[1]
            optimalOrderBox[orderId] = boxId
            #optimalBoxes.append(str(x)[2:])
    
    optimalCost = prob.objective.value()

    variableOutputFile = "data/output/variable_values.txt"
    orderBoxOutputFile = "data/output/order_box.txt"
    optimalBoxOutputFile = "data/output/box.txt"
    
    variableFileWrite(variableOutputFile, prob.variables(), optimalCost, orderBoxOutputFile, optimalOrderBox, boxVolume, optimalBox, optimalBoxOutputFile, stochasticFlag)

    return optimalBox, optimalOrderBox, optimalCost, boxVolume, orderEligibleBox