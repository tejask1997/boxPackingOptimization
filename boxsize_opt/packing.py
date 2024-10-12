"""
packing.py: Contains functions related to box packing feasibility.

The module provides functions to check the volume and dimensions feasibility of an order with respect to a box.
It also includes a function to determine eligible boxes for a given order.

Functions:
    volumeFill(currentOrderVolume, box): Checks if the order volume is compatible with the box volume.
    dimensionFeasibility(currentOrderDepth, currentOrderWidth, currentOrderHeight, box): Checks if the order dimensions are compatible with the box dimensions.
    packingFeasibility(currentOrderId, currentOrderVolume, currentOrderDepth, currentOrderWidth, currentOrderHeight, boxes): Determines the eligible boxes for a given order.

"""

from typing import Tuple, List
from .box import Box
from .product import Product

def volumeFill(currentOrderVolume: float, box: Box) -> bool:
    """Checks volume of order is compatible with the given container(box)"""

    """
    Checks if the volume of the current order is compatible with the given box.

    Args:
        currentOrderVolume (float): The volume of the current order.
        box (Box): The box object.

    Returns:
        bool: True if the current order can fit in the box, False otherwise.
    """
    
    #print("Current order volume:{currentOrderVolume}, Current box Volume:{boxVolume}".format(currentOrderVolume = currentOrderVolume, boxVolume = box.getboxVolume()))
    return currentOrderVolume <= box.boxVolume


def dimensionFeasibility(products: List[Product], box: Box) -> bool:
    """Checks dimensions of order are compatible with given container (box)."""

    """
    Checks if the dimensions of the current order are compatible with the given box.

    Args:
        currentOrderDepth (float): The depth of the current order.
        currentOrderWidth (float): The width of the current order.
        currentOrderHeight (float): The height of the current order.
        box (Box): The box object.

    Returns:
        bool: True if the dimensions of the current order can fit in the box, False otherwise.
    """

    for product in products:
        maxCurrentOrderDepth = max(products, key=lambda product: product.productDepth).productDepth
        maxCurrentOrderWidth = max(products, key=lambda product: product.productWidth).productWidth
        maxCurrentOrderHeight = max(products, key=lambda product: product.productHeight).productHeight
    
    productDimensions = sorted([maxCurrentOrderDepth,maxCurrentOrderWidth,maxCurrentOrderHeight])

    boxDimensions = sorted([box.boxDepth, box.boxWidth, box.boxHeight])
    
    allGreater =lambda productDimensions, boxDimensions: all(x <= y for x, y in zip(productDimensions, boxDimensions))
    result = allGreater(productDimensions, boxDimensions)
    
    #print(allGreater, result)
    #print(result) 
    #print(productDimensions, "\t", boxDimensions, "\t", allGreater)

    return result

def packingFeasibility(currentOrderId: str, currentOrderVolume: float, products: Product, boxes: Box) -> Tuple:
    """
    Iterates through all the orders sampled and gets the list of containers(boxes) which are compatible for a particular order based on its volume and dimensions.
    """

    """
    Iterates through all the orders sampled and gets the list of containers (boxes) which are compatible for a particular order based on volume and dimension feasibility.

    Args:
        currentOrderId (str): The ID of the current order.
        currentOrderVolume (float): The volume of the current order.
        currentOrderDepth (float): The depth of the current order.
        currentOrderWidth (float): The width of the current order.
        currentOrderHeight (float): The height of the current order.
        boxes (list): List of Box objects.

    Returns:
        Tuple: A tuple containing the eligible boxes, eligible box IDs, the most eligible box, and its volume.
    """
    
    eligibleBoxes = []
    eligibleBoxesPackingEfficiency = []

    mostEligibleBoxVolume = 0
    mostEligibleBox = ""
    for box in boxes:
        volumeFillFlag = volumeFill(currentOrderVolume, box)
        dimensionFeasibilityFlag = dimensionFeasibility(products, box)

        if(volumeFillFlag and dimensionFeasibilityFlag):
            #eligibleBoxes.append(box.getBoxId())
            eligibleBoxes.append(box)
            eligibleBoxesPackingEfficiency.append(round(currentOrderVolume/box.boxVolume, 2))

    eligibleBoxesId = [box.boxId for box in eligibleBoxes]
    if eligibleBoxes:
        mostEligibleBox = min(eligibleBoxes, key=lambda box: box.boxVolume).boxId
        mostEligibleBoxVolume = min(eligibleBoxes, key=lambda box: box.boxVolume).boxVolume

    #print("Eligible Boxes: ", eligibleBoxes)
    #print("Current Order Id: {currentOrderId} Eligible Boxes: {eligibleBoxesId} Most Eligible Box: {mostEligibleBox}".format(currentOrderId = currentOrderId, eligibleBoxesId = eligibleBoxesId, mostEligibleBox = mostEligibleBox))
    return eligibleBoxes, eligibleBoxesId, eligibleBoxesPackingEfficiency, mostEligibleBox, mostEligibleBoxVolume