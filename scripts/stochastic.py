import pandas as pd
import random
from boxsize_opt.optimization_model import boxOptimizationCheck
from boxsize_opt.utils import find_minimal_sets
import pulp
import ast
import time
import smtplib
import sys
from email.mime.text import MIMEText
from datetime import datetime



def parse_list(string):
    try:
        return ast.literal_eval(string)
    except (SyntaxError, ValueError):
        return []

def get_password():
    with open("scripts/keys.txt", "r") as file:
        return file.readlines()[0]

def send_email(message, recipients):
    subject = "Lakeland Stochastic Simulation Update"
    body = message
    sender = "tjkhandale@mitaoe.ac.in"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    password = get_password()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, msg.as_string())
    print("Email Sent")


rowsCount = 1000
boxAnalysis = pd.read_csv("data/output/padberg_results.csv", nrows=rowsCount, converters={'eligibleBoxesId': parse_list, 'eligibleBoxesPackingEfficiency': parse_list, 'Padberg_Result' : parse_list, 'Padberg_Packing_Efficiency' : parse_list})
probableBoxes = pd.read_csv("data/output/probable_boxes.csv")

boxAnalysis = boxAnalysis[boxAnalysis['Padberg_Result'].apply(lambda x: len(x) > 0)]


print(f"Size of boxAnalysis: {boxAnalysis.shape}")


numberOfTotalOrder = boxAnalysis.shape[0]
#numberOfTrials = 20
#inSampleSize = [500, 1000, 2000, 5000, 10000]
#numberOfMaxBoxes = [9, 10, 11, 12, 13, 14, 15]

#For Testing Purposes
numberOfTrials = 20
inSampleSize = [100,200,500]
numberOfMaxBoxes = [9, 10,11,12,13]

#print(f'Command line args: {sys.argv}')

#assert len(sys.argv) == 2
#if len(sys.argv) == 2:
#    numberOfMaxBoxes = [int(sys.argv[1])]
#    stochasticDataFile = f"data/output/padberg_results_stochasticData_{numberOfMaxBoxes}.txt"
#    stochasticBoxFile = f"data/output/padberg_results_stochasticBox_{numberOfMaxBoxes}.txt"
stochasticDataFile = f"data/output/padberg_results_stochasticData.txt"
stochasticBoxFile = f"data/output/padberg_results_stochasticBox.txt"

print(f"Argument: {numberOfMaxBoxes}")

# 1 = Packing Efficiency, 2 = Volume
optimizationMethod = [1, 2]
optimizationMethodName = {1: "Maximizing Packing Efficiency", 2: "Minimizing Volume"}

totalNumberOfTrials = len(inSampleSize) * len(numberOfMaxBoxes) * len(optimizationMethod)
trialsCompleted = 0

boxAnalysisDict = dict(zip(boxAnalysis.orderId, boxAnalysis.Padberg_Result))
boxVolumeAnalysisDict = dict(zip(boxAnalysis.orderId, boxAnalysis.orderVolume))
boxPackingEfficiencyDict = {}
for index, row in boxAnalysis.iterrows():
    order = row['orderId']
    eligible_boxes = row['Padberg_Result']
    packing_efficiencies = row['Padberg_Packing_Efficiency']
    for box, efficiency in zip(eligible_boxes, packing_efficiencies):
        key = (order, box)
        boxPackingEfficiencyDict[key] = efficiency


#print(boxPackingEfficiencyDict)


boxLists = boxAnalysis.Padberg_Result
minBoxLists = find_minimal_sets(boxLists, verbose=True)

print(f"Minimal Subset Length: {len(minBoxLists)}")

with open(stochasticDataFile, "a") as file:
    file.write(f"Method\tTrial\tSeed\tDataSize\tNumberofBoxes\tInSampleSize\tInSampleVolume\tOutSampleVolume\tInSamplePackingEfficiency\tOutSamplePackingEfficiency\tExecutionTime\tNoEligibleBox\n")
with open(stochasticBoxFile, "a") as file:
    file.write(f"Method\tTrial\tSeed\tDataSize\tInSampleSize\tNumberOfBoxes\tBoxList\n")

stochasticStartTime = time.time()
counter = 0
for method in optimizationMethod:
    for numberOfBoxes in numberOfMaxBoxes:
        for sampleSize in inSampleSize:
            trialStartTime = time.time()
            for i in range(numberOfTrials): 
                counter += 1
                outSampleCount = 0
                noEligibleBox = 0
                print(f"\n\nMethod:{optimizationMethodName[method]}, Number of Boxes: {numberOfBoxes}, Sample Size: {sampleSize}, Trial: {i}")
                #solver = pulp.GUROBI(threads = 12, msg = 0)
                solver = pulp.GUROBI(msg = 0)
                iterationStartTime = time.time()
                optimizedBox = {}
                totalVolume = 0
                inSampleVolume = 0
                outSampleVolume = 0
                totalPackingEfficiency = 0
                inSamplePackingEfficieny = 0
                outSamplePackingEfficieny = 0
                randSeed = random.randint(1,10000)
                boxAnalysisSample = boxAnalysis.sample(n=sampleSize, random_state=randSeed)
                optimalBox, optimalOrderBox, optimalCost, boxVolume, orderEligibleBox = boxOptimizationCheck(boxAnalysisSample, probableBoxes, minBoxLists, numberOfBoxes, method, counter, solver, True)
                afterOptimizationCounter = 0
                print(f"KPIs Calculation Started at: {datetime.now().strftime('%H:%M:%S')}")
                if method == 1:
                    for order, boxes in boxAnalysisDict.items():
                        eligibleBoxes = [box for box in boxes if box in optimalBox]
                        if eligibleBoxes:
                            # Find the box with the maximum efficiency
                            maxEfficientBox = max(boxPackingEfficiencyDict, key=lambda x: boxPackingEfficiencyDict[x] if x[0] == order else -1)[1]
                            if order in boxAnalysisSample["orderId"].values:
                                inSamplePackingEfficieny += (boxAnalysisSample[boxAnalysisSample["orderId"] == order]["orderVolume"].iloc[0])/boxVolume[maxEfficientBox]  
                                inSampleVolume += boxVolume[maxEfficientBox]
                            else:
                                outSampleCount += 1
                                outSamplePackingEfficieny += (boxAnalysis[boxAnalysis["orderId"] == order]["orderVolume"].iloc[0])/boxVolume[maxEfficientBox]
                                outSampleVolume += boxVolume[maxEfficientBox]
                        else:
                            noEligibleBox += 1

                if method == 2:
                    for order, boxes in boxAnalysisDict.items():
                        
                        eligibleBoxes = [box for box in boxes if box in optimalBox]
                        #print(eligibleBoxes)
                        if eligibleBoxes:
                            # Find the box with the lowest volume
                            lowestVolumeBox = min(eligibleBoxes, key=lambda box: boxVolume[box])
                            #optimizedBox[order] = lowestVolumeBox
                            #totalVolume += boxVolume[lowestVolumeBox]
                            if order in boxAnalysisSample["orderId"].values:
                                inSamplePackingEfficieny += (boxAnalysisSample[boxAnalysisSample["orderId"] == order]["orderVolume"].iloc[0])/boxVolume[lowestVolumeBox]
                                inSampleVolume += boxVolume[lowestVolumeBox]
                            else:
                                outSampleCount += 1
                                outSamplePackingEfficieny += (boxAnalysis[boxAnalysis["orderId"] == order]["orderVolume"].iloc[0])/boxVolume[lowestVolumeBox]
                                outSampleVolume += boxVolume[lowestVolumeBox]
                        else:
                            noEligibleBox += 1
                inSamplePackingEfficieny = round(inSamplePackingEfficieny/sampleSize, 4) if sampleSize != 0 else 0
                inSampleVolume = round(inSampleVolume/sampleSize, 4) if sampleSize != 0 else 0
                if numberOfTotalOrder == sampleSize:
                    outSamplePackingEfficieny = 0
                    outSampleVolume = 0
                else:
                    outSamplePackingEfficieny = round(outSamplePackingEfficieny/outSampleCount, 4) if outSampleCount != 0 else 0
                    outSampleVolume = round(outSampleVolume/outSampleCount, 4) if outSampleCount != 0 else 0
                iterationTime = (time.time() - iterationStartTime)/60 
                

                with open(stochasticDataFile, "a") as file:
                    file.write(f"{method}\t{i+1}\t{randSeed}\t{numberOfTotalOrder}\t{numberOfBoxes}\t{sampleSize}\t{inSampleVolume}\t{outSampleVolume}\t{inSamplePackingEfficieny}\t{outSamplePackingEfficieny}\t{iterationTime}\t{noEligibleBox}\n")
                with open(stochasticBoxFile, "a") as file:
                    #for box in optimalBox:
                    file.write(f"{method}\t{i+1}\t{randSeed}\t{numberOfTotalOrder}\t{sampleSize}\t{numberOfBoxes}\t{optimalBox}\n")
            trialsCompleted += 1
            timeForTrial = round((time.time() - trialStartTime)/60,2)
            recipients = ["tejask1997@gmail.com"]
            message = f"Simulation Done for Method - {optimizationMethodName[method]}\nSample Size - {sampleSize}\nBoxes - {numberOfBoxes}\nTrials Done - {trialsCompleted}/{totalNumberOfTrials}\nTime Taken - {timeForTrial} min"
            send_email(message,recipients)
            
recipients = ["tejask1997@gmail.com", "j.fairbrother@lancaster.ac.uk"]
message = f"Simulation Completed"
#send_email(message,recipients)
print(f"Time required to complete: {(time.time() - stochasticStartTime)/60}") 