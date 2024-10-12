from pulp import PULP_CBC_CMD

from boxsize_opt.box import Box
from boxsize_opt.product import Product
from boxsize_opt.filter import get_eligible_boxes, probable_box

# ┌─────────┐
# │    F    │   ┌───┐
# └────▲────┘   │ D │
#      │        └─▲─┘
# ┌────┴────┐     │
# │    E    │   ┌─┴─┐
# └─────────┘   │ B │
#               └─▲─┘
#        ┌───┐    │
#        │ C │  ┌─┴─┐
#        └───┘◄─┤ A │
#               └───┘
# Arrows indicate source box can fit in destination box

def test_eligible_box_filter():
    solver=PULP_CBC_CMD(msg=False)

    boxes = ['PB_20_10_10', # A
             'PB_20_15_15', # B
             'PB_30_15_10', # C
             'PB_20_20_20', # D
             'PB_90_10_5', # E
             'PB_100_10_5'] # F
    order_1 = [Product('A', 20, 10, 10)]
    boxes_1 = set(get_eligible_boxes(order_1, boxes, solver=solver, verbose=True))
    assert boxes_1 == {'PB_20_10_10', # A
                        'PB_20_15_15', # B
                        'PB_30_15_10', # C
                        'PB_20_20_20'}# D}

    order_2 = [Product('B', 20, 15, 15)]
    boxes_2 = set(get_eligible_boxes(order_2, boxes, solver=solver, verbose=True))
    assert boxes_2 == {'PB_20_15_15', # B
                        'PB_20_20_20'} #D

    order_3 = [Product('E', 90, 10, 5)]
    boxes_3 = set(get_eligible_boxes(order_3, boxes, solver=solver, verbose=True))
    assert boxes_3 == {'PB_90_10_5', # E
                        'PB_100_10_5'} # F
