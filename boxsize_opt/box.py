from __future__ import annotations

"""
box.py: Contains the definition of the Box class.

The Box class represents a box with its dimensions and volume. It provides methods to retrieve the box details.

Attributes:
    boxId (str): The ID of the box.
    boxDepth (float): The depth of the box.
    boxWidth (float): The width of the box.
    boxHeight (float): The height of the box.
    boxVolume (float): The volume of the box.

"""
#TODO: Add TSA as an attribute
class Box:
    def __init__(self, boxId, boxDepth, boxWidth, boxHeight):
        """
        Initialize a Box object with the provided parameters.

        Args:
            boxId (str): The ID of the box.
            boxDepth (float): The depth of the box.
            boxWidth (float): The width of the box.
            boxHeight (float): The height of the box.
        """
        self.boxId = boxId
        self.boxDepth = boxDepth
        self.boxWidth = boxWidth
        self.boxHeight = boxHeight
        self.boxVolume = round(boxDepth * boxWidth * boxHeight,2)
        self.surfaceArea = 2 * (boxDepth * boxWidth + boxWidth * boxHeight + boxDepth * boxHeight)

    def boxDetails(self):
        print(" Box Details: Box ID - {boxId}, Box Depth - {boxDepth}, Box Width - {boxWidth}, Box Height - {boxHeight}, Box Volume - {boxVolume}".format(boxId = self.boxId, boxDepth = self.boxDepth, boxWidth = self.boxWidth, boxHeight = self.boxHeight, boxVolume = self.boxVolume))

    def contains(self, box: Box) -> bool:
        '''Checks whether this box could contain `box`'''
        dims1 = sorted([self.boxDepth, self.boxWidth, self.boxHeight])
        dims2 = sorted([box.boxDepth, box.boxWidth, box.boxHeight])
        return dims1[0] >= dims2[0] and dims1[1] >= dims2[1] and dims1[2] >= dims2[2]
