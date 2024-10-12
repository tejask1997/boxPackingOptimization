"""
product.py: Contains the definition of the Product class.

The Product class represents a product with its dimensions and volume. It provides methods to retrieve the product details.

Attributes:
    productId (str): The ID of the product.
    productDepth (float): The depth of the product.
    productWidth (float): The width of the product.
    productHeight (float): The height of the product.
    productVolume (float): The volume of the product.

"""
#TODO: Add TSA as an attribute
class Product:
    def __init__(self, productID, productDepth, productWidth, productHeight):
        """
        Initialize a Box object with the provided parameters.

        Args:
            boxId (str): The ID of the box.
            boxDepth (float): The depth of the box.
            boxWidth (float): The width of the box.
            boxHeight (float): The height of the box.
        """
        self.productID = productID
        self.productDepth = productDepth
        self.productWidth = productWidth
        self.productHeight = productHeight
        self.productVolume = round(productDepth * productWidth * productHeight,2)
        
    def productDetails(self):
        print("Product Details: Product ID - {productID}, Product Depth - {productDepth}, Product Width - {productWidth}, Product Height - {productHeight}, Product Volume - {productVolume}".format(productID = self.productID, productDepth = self.productDepth, productWidth = self.productWidth, productHeight = self.productHeight, productVolume = self.productVolume))

    def __repr__(self):
        return f"Product({self.productDepth},{self.productWidth},{self.productHeight})"