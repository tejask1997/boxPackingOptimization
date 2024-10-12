import pandas as pd
from typing import List
import ast
import matplotlib.pyplot as plt
import pandas as pd
import pulp
from boxsize_opt.utils import find_minimal_sets

def minimal_set_cover(box_lists: List[List[str]]):
    all_boxes = set()
    for boxes in box_lists:
        all_boxes = all_boxes.union(boxes)
    print(f'{len(all_boxes)} boxes in lists')

    prob = pulp.LpProblem('Minimal Set Covering', pulp.LpMinimize)
    x = pulp.LpVariable.dicts("x", all_boxes, lowBound=0, upBound=1, cat='Integer')
    prob += pulp.lpSum(x[box] for box in all_boxes)
    
    for boxes in box_lists:
        prob += (pulp.lpSum(x[b] for b in boxes) >= 1)
    
    prob.solve()
    if prob.status != 1:
        raise ValueError(f'Problem was not solved to optimality. Returned with status {prob.status}')
    return prob.objective.value()

def parse_list(string):
    try:
        return ast.literal_eval(string)
    except (SyntaxError, ValueError):
        return []

results_fn = "data/output/padberg_results_HEC.csv"
#results_fn = "data/output/padberg_results.csv"


#nrows_list = [1000, 5000, 10000, 20000, 40000]
nrows_list = [10000]
records = []
for nrows in nrows_list:
    print(f'Reading file for nrows={nrows}...')
    boxAnalysis = pd.read_csv(results_fn, usecols=['Padberg_Result'],  nrows=nrows, converters={'Padberg_Result': parse_list})
    #boxAnalysis = pd.read_csv("data/output/probable_box_data_analysis.csv", usecols=['eligibleBoxesId'], nrows=nrows)

    #box_lists = [parse_list(boxes_str) for boxes_str in boxAnalysis.eligibleBoxesId]
    box_lists = boxAnalysis.Padberg_Result
    print('Generating lists...')
    
    min_box_lists = find_minimal_sets(box_lists, verbose=True)
    print('\n'.join(' '.join(boxes) for boxes in min_box_lists))
    print(f'{len(min_box_lists)} minimal subsets')

    min_boxes = minimal_set_cover(min_box_lists)
    print('Minimum number of boxes required:', min_boxes)
    records.append({'n_orders': nrows, 'minimal_subsets': len(min_box_lists), 'min boxes required': min_boxes, 'min_box_list': min_box_lists})

df = pd.DataFrame.from_records(records)
print(df)