import pulp
from boxsize_opt.product import Product
from boxsize_opt.box import Box
from boxsize_opt.padberg import *
import pandas as pd

# importing the complete order data
df = pd.read_csv("data/output/merged_order_data.csv")

# storing the dimensions of the products in variables
depth = df[df['Order_id'] == 3453806501]['each_depth'].tolist()
width = df[df['Order_id'] == 3453806501]['each_width'].tolist()
height = df[df['Order_id'] == 3453806501]['each_height'].tolist()

# creating the product class for all the products and storing them in a variable
order = []
for j in range(0,len(depth)):
    order.append(Product(j+1,depth[j],width[j],height[j]))

# probable box dimensions
pb = 'PB_35_20_20'.split('_')


# solver = pulp.getSolver('GUROBI_CMD')
# solver = pulp.getSolver('SCIP_CMD')
# solver = pulp.getSolver('COIN_CMD')
# solver = pulp.getSolver('GLPK_CMD')
solver = pulp.getSolver('HiGHS_CMD')

result = padberg_check(order,Box(pb[0],int(pb[1]),int(pb[2]),int(pb[3])), solver=solver)
#result = padberg_check(order,Box(pb[0],int(pb[1]),int(pb[2]),int(pb[3])))

print(result)