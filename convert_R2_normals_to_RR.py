from PIL import Image
import os
import glob
import numpy as np
import math

#get the current working directory
directory = os.getcwd()

def checkTransparency(img):
    #checks if image has transparent alpha channel
    if img.info.get("transparency", None) is not None:
        return True
    # P -> (8-bit pixels, mapped to any other mode using a color palette)
    if img.mode == "P":
        transparent = img.info.get("transparency", -1)
        for _, index in img.getcolors():
            if index == transparent:
                return True
    elif img.mode == "RGBA":
        extrema = img.getextrema()
        if extrema[3][0] < 255:
            return True

    return False


def loadImagesFromFolder(directory):

    def channelToArray(channel):
        channel = np.array(channel).astype(np.float64)
        return channel

    def arrayToChannel(array):
        array = Image.fromarray(array.astype(np.uint8))
        return array

    def generateBlueChannel(red, green, blue):
        for i, item in enumerate(blue):
            for k, value in enumerate(item):
                # Equation: blue = √(1 - (red^2 + green^2))
                blue[i][k] = round(math.sqrt(abs(1- (red[i][k]**2 + green[i][k]**2))),1)

    def convertR2NormalsToRomeRemastered(filename, image):
        # Split into 4 channels
        red, green, blue, alpha = image.split()
        # Assign alpha channel to red channel
        red = alpha
        # Convert color channels to numpy arrays
        red = channelToArray(red)
        green = channelToArray(green)
        blue = channelToArray(blue)
        # Generate missing blue (B) channel from R, G
        generateBlueChannel(red, green, blue)
        # Transform array back to color channel
        red = arrayToChannel(red)
        green = arrayToChannel(green)
        blue = arrayToChannel(blue)
        # Recombine back to RGB image
        result = Image.merge('RGB', (red, green, blue))
        # Save image
        try:
            result.save(filename)
            print("{} converted successfully.".format(filename))
        except:
            print("An error occurred.") 

    for filename in glob.glob('*.dds'):
        # Make sure files are normals
        if filename[-10:-4] == "normal":
            image = Image.open(filename)
            # Check if there's an alpha channel before continuing
            if checkTransparency(image) == True:
                convertR2NormalsToRomeRemastered(filename, image)
                
if __name__ == "__main__":
    loadImagesFromFolder(directory)