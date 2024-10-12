from typing import Tuple, List
import itertools
import pulp
from .box import Box
from .product import Product

def padberg_model(order: List[Product], box: Box, use_knapsack: bool = False):
  prob = pulp.LpProblem("Padberg", pulp.LpMaximize)

  n_prod = len(order)
  H = ('X', 'Y', 'Z')
  alpha = range(3)

  # Decision variables representing alignment of products in box
  # delta_idxs = [c for c in itertools.product(H, alpha, range(n_prod))]
  delta_idxs = itertools.product(range(n_prod), H, alpha)

  delta = pulp.LpVariable.dicts("delta", delta_idxs, lowBound=0, upBound=1,
                                cat=pulp.LpInteger)
  
  # Coordinates of centres of gravity for each product
  # x_idxs = [c for c in itertools.product(range(n_prod), H)]
  x_idxs = itertools.product(range(n_prod), H)
  x = pulp.LpVariable.dicts("x", x_idxs, lowBound=0)


  # Precedence variables
  lam_idxs = []
  for h in H:
    for (i, p1) in enumerate(order):
      for (k, p2) in enumerate(order):
        if i != k:
          lam_idxs.append((h, i, k))
  lam = pulp.LpVariable.dicts("lambda", lam_idxs, lowBound=0, upBound=1,
                              cat=pulp.LpInteger)
  

  D = {'X': box.boxDepth, 'Y': box.boxWidth, 'Z': box.boxHeight}

  #L = {i : (p.productDepth, p.productWidth, p.productHeight) for (i,p) in enumerate(order)}
  l = {i : (p.productDepth/2, p.productWidth/2, p.productHeight/2) for (i,p) in enumerate(order)}
  

  # Objective - total products packed
  prob += (pulp.lpSum(delta[i, h, 0] for h in H for i in range(n_prod)))
  
  for (i,p) in enumerate(order):
    # Orthogonal placement constraints: ensure
    # that if we assign one dimension of product to X, Y, or Z,
    # then we must assign other two dimensions. If we don't assign
    # first dimension of a product, then we don't assign any others
    prob += (
      delta[i, 'X', 0] + delta[i, 'Y', 0] + delta[i, 'Z', 0] <= 1.0,
      f"Product {i} - Orthogonal Placement 1")
    prob +=(
      delta[i, 'X', 1] + delta[i, 'Y', 1] + delta[i, 'Z', 1] == delta[i, 'X', 0] + delta[i, 'Y', 0] + delta[i, 'Z', 0],
      f"Product {i} - Orthogonal Placement 2")
    for h in H:
      prob +=(
        pulp.lpSum(delta[i, h, ai] for ai in alpha) == delta[i, 'X', 0] + delta[i, 'Y', 0] + delta[i, 'Z', 0],
        f"Product {i} - Orthogonal Placement 3 - {h}")
      
    # Domain constraints
    for h in H:
      prob += (
        x[i, h] >= pulp.lpSum(l[i][ai]*delta[i, h, ai] for ai in alpha),
        f"Product {i} - Domain Constraints - Lower {h}")
      prob += (
        x[i, h] <= pulp.lpSum((D[h] - l[i][ai])*delta[i, h, ai] for ai in alpha),
        f"Product {i} - Domain Constraints - Upper {h}")

  # Non-intersection constraints
  for (i,p1) in enumerate(order):
    for j in range(i+1, n_prod):
      p2=order[j]
      for h in H:
        prob += (D[h]*lam[h, j, i] + pulp.lpSum(l[i][ai]*delta[i, h, ai] for ai in alpha) -
                 pulp.lpSum((D[h] - l[j][ai])*delta[j, h, ai] for ai in alpha) <= x[i, h] - x[j, h],
                 f"Non-intersection - Products {i} and {j} - {h} - 1Lower")
        prob += (pulp.lpSum((D[h] - l[i][ai])*delta[i, h, ai] for ai in alpha) -
                 pulp.lpSum(l[j][ai]*delta[j, h, ai] for ai in alpha) -
                 D[h]*lam[h, i, j] >= x[i, h] - x[j, h],
                 f"Non-intersection - Products {i} and {j} - {h} - 1Upper")
        
      prob += (pulp.lpSum(lam[h, i, j] + lam[h, j, i] for h in H) <= pulp.lpSum(delta[i, h, 0] for h in H),
                f"Non-intersection - Products {i} and {j} - {h} - 2A)")
      prob += (pulp.lpSum(lam[h, i, j] + lam[h, j, i] for h in H) <= pulp.lpSum(delta[j, h, 0] for h in H),
                f"Non-intersection - Products {i} and {j} - {h} - 2B)")

      prob += (pulp.lpSum(delta[i, h, 0] + delta[j, h, 0] for h in H) <= 1 + pulp.lpSum(lam[h, i, j] + lam[h, j, i] for h in H),
                f"Non-intersection - Products {i} and {j} - {h} - 3")

  if use_knapsack:
    vol = [p.productVolume for p in order]
    box_vol = box.boxVolume
    prob += (pulp.lpSum(vol[i]*delta[i, h, 0] for i in range(n_prod) for h in H) <= box_vol)

  return prob, x, delta, lam

# the function
def padberg_check(order: List[Product], box: Box, solver = None, use_knapsack = False) -> bool:

  prob, x, delta, lam = padberg_model(order, box, use_knapsack=use_knapsack)
  # Solve problem
  if solver is None:
    prob.solve(pulp.PULP_CBC_CMD(msg=1, maxSeconds=15))
  else:
    prob.solve(solver)

  # Check problem solved to optimality - if not try reducing target return
  if prob.status != 1:
    return False
    #raise ValueError(f'Problem was not solved to optimality. Returned with status {prob.status}')

  x_val = {c: x[c].value() for c in x}
  delta_val = {c: delta[c].value() for c in delta}
  lam_val = {c: lam[c].value() for c in lam}


  if round(pulp.value(prob.objective)) < len(order):
    return False

  return True
