from boxsize_opt.box import Box
from boxsize_opt.product import Product
from boxsize_opt.padberg import padberg_model, padberg_check 

def test_padberg_0():
    '''Example where all products should fit in box (box much larger than small products).'''
    boxA = Box('BoxA', 30, 30, 30)
    order = [Product('ProdA', 10, 10, 10), Product('ProdB', 10, 10, 10)]
    assert padberg_check(order, boxA)


def test_padberg_1():
    '''Example where one big product should fit in box exactly.'''
    box = Box('BoxA', 30, 30, 30)
    order = [Product('ProdA', 30, 30, 30)]
    assert padberg_check(order, box)


def test_padberg_2():
    '''Example where two products should fit in box tightly'''
    boxA = Box('BoxA', 30, 20, 10)
    order = [Product('ProdA', 30, 20, 5), Product('ProdB', 30, 20, 5)]
    assert padberg_check(order, boxA)

    # Rotated box (items still fit when rotated)
    boxB = Box('BoxB', 10, 30, 20)
    assert padberg_check(order, boxB)


def test_padberg_3():
    """Example where volume of products is less than box but products can't all fit it."""
    box = Box('BoxA', 30, 20, 10)
    order = [Product('ProdA', 30, 20, 5), Product('ProdB', 10, 10, 10)]
    assert not padberg_check(order, box)



def test_padberg_4():
    """Example where three products should fit in box tightly."""
    boxA = Box('BoxA', 30, 20, 10)
    order = [Product('ProdA', 30, 20, 5), Product('ProdB', 30, 10, 5), Product('ProdC', 30, 10, 5)]
    assert padberg_check(order, boxA)

    # Rotated box (items still fit when rotated)
    boxB = Box('BoxB', 10, 30, 20)
    assert padberg_check(order, boxB)