from boxsize_opt.utils import find_minimal_sets
from boxsize_opt.packing import dimensionFeasibility
from boxsize_opt.box import Box
from boxsize_opt.product import Product

def test_find_minimal_sets_1():
    sets = [(1,2,3), (2, 3, 4), (4,5,6,7), (2,3), (3,4)]
    true_min_sets = [frozenset((2,3)), frozenset((3,4)), frozenset((4,5,6,7))]
    min_sets = [frozenset(s) for s in find_minimal_sets(sets)]
    assert set(true_min_sets) == set(min_sets)

def test_find_minimal_sets_2():
    sets = [(1,2,3)]
    true_min_sets = [frozenset((1,2,3))]
    min_sets = find_minimal_sets(sets)
    assert set(true_min_sets) == set(min_sets)

def test_find_minimal_sets_3():
    sets = [(1,2,3), (1,2), (1,)]
    true_min_sets = {frozenset((1,))}
    min_sets = find_minimal_sets(sets)
    assert set(true_min_sets) == set(min_sets)

def test_dim_feasibility_1():
    order = [Product('A', 37.2, 35.2, 22.6)]
    box = Box('1', 40, 40, 20)
    assert not dimensionFeasibility(order, box)