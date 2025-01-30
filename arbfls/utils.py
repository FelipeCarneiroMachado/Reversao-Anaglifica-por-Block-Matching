#General utilities
import numpy as np
import cv2 as cv
import imageio as iio
from arbfls.config import config_dict


def split_channels(anaglyph : np.ndarray, config : dict = config_dict) -> tuple[np.ndarray, np.ndarray, tuple[int, int]]:
    #Split the channels
    match config["anaglyph_type"]:
        case "green_magenta": 
            l = anaglyph.copy()
            l[:, :, 0] = l[:, :, 1]
            l[:, :, 2] = l[:, :, 1]
            r =  anaglyph.copy()
            r[:, :, 1] = r[:, :, 0]
        case "red_cyan":
            l = anaglyph[:, :, 0]
            r =  anaglyph.copy()
            r[:, :, 0] *= 0
        case "blue_yellow":
            l = anaglyph[:, :, 2]
            r =  anaglyph.copy()
            r[:, :, 2] *= 0
        case _:
            raise Exception("Unsuported anaglyph type")
    return l, r
  
def resize_anaglyph(anaglyph:np.ndarray, config:dict = config_dict):
    f = lambda x : (config["block_size"] - (x % config["block_size"]) 
                    if x % config["block_size"] != 0 
                    else 0)
    #Resizing the channels
    resized = cv.copyMakeBorder(anaglyph
                                  , 0,
                                  f(anaglyph.shape[0]),
                                  0,
                                  f(anaglyph.shape[1]),
                                  cv.BORDER_CONSTANT,
                                  value=[0, 0, 0])
    return resized

#Resizes the channels so the dimensios are divisible by the block size
def resize_channels(l:np.ndarray, r:np.ndarray, config:dict = config_dict)->tuple[np.ndarray,np.ndarray, np.shape]:
    #This function makes so the new size is divisible by the blocks
    f = lambda x : (config["block_size"] - (x % config["block_size"]) 
                    if x % config["block_size"] != 0 
                    else 0)
    #Resizing the channels
    resized_l = cv.copyMakeBorder(l
                                  , 0,
                                  f(l.shape[0]),
                                  0,
                                  f(l.shape[1]),
                                  cv.BORDER_CONSTANT,
                                  value=[0, 0, 0])
    resized_r = cv.copyMakeBorder(r
                                  , 0,
                                  f(r.shape[0]),
                                  0,
                                  f(r.shape[1]),
                                  cv.BORDER_CONSTANT,
                                  value=[0, 0, 0])
    return resized_l, resized_r, resized_l.shape


#Returns if a coordinate is valid
def valid_coordinate(y:int, x:int, dimensions:tuple[int, int, int])->bool:
    if x >= 0 and x < (dimensions[1]):
        if y >= 0 and y < (dimensions[0]):
            return True
        else:
            return False
    else:
        return False
    
#Determines if the coordinate is a valid value for a block
def valid_block(y : int, x : int, dimensions:tuple[int, int, int], config : dict = config_dict) -> bool:
    if x >= 0 and x <= (dimensions[1] - config["block_size"]):
        if y >= 0 and y <= (dimensions[0] - config["block_size"]):
            return True
        else:
            return False
    else:
        return False

#Returns the image with the given block , does not alter the image
def contour_block(image : np.ndarray, colour : tuple, coordinates : tuple[int, int], config : dict = config_dict) -> np.ndarray:
    image = image.copy()
    for x in range(coordinates[0] -1, coordinates[0] + config["block_size"] + 1):
        if valid_coordinate(x, coordinates[1] - 1):
            image[x, coordinates[1] - 1] = colour
        if valid_coordinate(x, coordinates[1] + config["block_size"] + 1):
            image[x, coordinates[1] + config["block_size"] + 1] = colour
    for y in range(coordinates[1] -1, coordinates[1] + config["block_size"] + 1):
        if valid_coordinate(coordinates[0] - 1, y):
            image[coordinates[0] - 1, y] = colour
        if valid_coordinate(coordinates[0] + config["block_size"] + 1, y):
            image[coordinates[0] + config["block_size"] + 1, y] = colour
    return image

#Returns the image with the search window contoured, does not alter the image
def contour_search_window(image:np.ndarray, colour:tuple, coordinates:tuple[int, int], config:dict = config_dict)->np.ndarray:
    image = image.copy()
    for y in range(coordinates[0] - config["vertical_window"] - 1, coordinates[0] + config["block_size"] + config["vertical_window"] + 1):
        if valid_coordinate(y, coordinates[1] - config["horizontal_window"]- 1):
            image[y, coordinates[1] - config["horizontal_window"]- 1] = colour
        if valid_coordinate(y, coordinates[1] +  config["horizontal_window"] +config["block_size"] + 1):
            image[y, coordinates[1] +  config["horizontal_window"] +config["block_size"] + 1] = colour
    for x in range(coordinates[1] -config["horizontal_window"] - 1, coordinates[1]+config["horizontal_window"] + config["block_size"] + 1):
        if valid_coordinate(coordinates[0] -config["vertical_window"]- 1, x):
            image[coordinates[0] -config["vertical_window"]- 1, x] = colour
        if valid_coordinate(coordinates[0] + config["block_size"] +config["vertical_window"]+ 1, x):
            image[coordinates[0] + config["block_size"] +config["vertical_window"]+ 1, x] = colour
    return image


# Return the channels to the original dimensions
def return_dimensions(result_left:np.ndarray, result_right:np.ndarray, dimensions:np.shape, config:dict = config_dict) -> None:
    bs = config["block_size"]
    f = lambda x :  -(bs - (x % bs)) if x % bs != 0 else x
    l = result_left[:dimensions[0], :dimensions[1]]
    r = result_right[:dimensions[0], :dimensions[1]]
    return l, r


def gen_anaglyph(l:np.ndarray, r:np.ndarray, config:dict = config_dict) -> np.ndarray:
    match config["anaglyph_type"]:
        case "green_magenta": 
            l, r, d = resize_channels(l, r, config)
            anaglyph = l.copy()
            anaglyph[:, :, [0, 2]] = r[:, :, [0, 2]]
        case "red_cyan":
            l, r, d = resize_channels(l, r, config)
            anaglyph = l.copy()
            anaglyph[:, :, [1, 2]] = r[:, :, [1, 2]]
        case "blue_yellow":
            l, r, d = resize_channels(l, r, config)
            anaglyph = l.copy()
            anaglyph[:, :, [0, 1]] = r[:, :, [0, 1]]
        case _:
            raise Exception("Unsuported anaglyph type")
    return anaglyph

